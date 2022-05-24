

import runtime.logging.logging as logging
import os
import tarfile
from typing import Optional
import requests
import json

from runtime.settings.ExeSettings import ToolExeSettings
import utils.general_utils as general_utils


def handle_downloads(intended_tool_id: str, esettings: ToolExeSettings) -> ToolExeSettings:
    assert(esettings.remote_url)
    handler = DownloadHandler(
        intended_tool_id=intended_tool_id, 
        wrappers_dir=esettings.download_dir,
        url=esettings.remote_url
    )
    handler.get()
    esettings.xmldir = handler.xmldir
    esettings.xmlfile = handler.xmlfile
    return esettings


class DownloadHandler:
    def __init__(self, intended_tool_id: str, wrappers_dir: str, url: str):
        self.intended_tool_id = intended_tool_id
        self.wrappers_dir = wrappers_dir
        self.url = url
        
        self.cache: DownloadCache = DownloadCache(wrappers_dir)
        self.xmldir: Optional[str] = None
        self.xmlfile: Optional[str] = None

    def get(self) -> None:
        xmldir = self.cache.get(self.url)  # returns the file xmldir (the xml)
        # cached
        if xmldir is not None:
            self.xmldir = xmldir
            self.xmlfile = general_utils.select_xmlfile(xmldir, self.intended_tool_id)
        # not cached
        else:
            self.log_message()
            tar = self.perform_download()
            self.xmldir = self.get_xmldir(tar)
            self.xmlfile = general_utils.select_xmlfile(self.xmldir, self.intended_tool_id)
            self.update_cache()

    def log_message(self) -> None:
        logging.msg_downloading_tool(self.url)

    def perform_download(self) -> tarfile.TarFile:
        response = requests.get(self.url, stream=True)
        tar = tarfile.open(fileobj=response.raw, mode='r:gz')
        tar.extractall(path=self.wrappers_dir)
        return tar
        
    def get_xmldir(self, tar: tarfile.TarFile) -> str:
        folder_name = os.path.commonprefix(tar.getnames())
        return f"{self.wrappers_dir}/{folder_name.rstrip('/')}"
    
    def update_cache(self) -> None:
        assert(self.xmldir)
        assert(self.xmlfile)
        self.cache.update(self.url, self.xmldir)


class DownloadCache:
    def __init__(self, wrapper_folder: str):
        self.wrapper_folder = wrapper_folder
        self.cache = self.load_cache()

    def load_cache(self) -> dict[str, str]:
        cache: dict[str, str] = {}
        xmldirs = next(os.walk(self.wrapper_folder))[1]
        for xmldir in xmldirs:
            path = f'{self.wrapper_folder}/{xmldir}'
            url = self.read(path)
            if url is not None:
                cache[url] = path
        return cache

    def read(self, xmldir: str) -> Optional[str]:
        path = f'{xmldir}/metadata.json'
        if os.path.exists(path):
            with open(path, 'r') as fp:
                data = json.load(fp)
                return data['url']
        return None

    def write(self, url: str, xmldir: str) -> None:
        with open(f'{xmldir}/metadata.json', 'w') as fp:
            the_dict = {
                'url': url,
            }
            json.dump(the_dict, fp)

    def get(self, url: str) -> Optional[str]:
        """returns the local file path for the tool xml if already downloaded or None"""
        if url in self.cache:
            return self.cache[url]
        
    def update(self, url: str, xmldir: str) -> None:
        self.write(url, xmldir)
