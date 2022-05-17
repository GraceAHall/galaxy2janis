

import logging
import os
import tarfile
import requests

from startup.ExeSettings import ToolExeSettings
import utils.etree as etree_utils 


def handle_downloads(intended_tool_id: str, esettings: ToolExeSettings) -> ToolExeSettings:
    logger = logging.getLogger('gxtool2janis')
    logger.info(f'downloading tool repo from {esettings.remote_url}')
    esettings.xmldir = download_repo(esettings)
    esettings.xmlfile = select_xml_source(intended_tool_id, esettings)
    return esettings

def download_repo(esettings: ToolExeSettings) -> str:
    assert(esettings.remote_url)  
    url = esettings.remote_url
    download_folder = esettings.get_download_dir()
    response = requests.get(url, stream=True)
    tar = tarfile.open(fileobj=response.raw, mode='r:gz')
    tar.extractall(path=download_folder)
    folder_name = os.path.commonprefix(tar.getnames())
    folder_path = f"{download_folder}/{folder_name.rstrip('/')}"
    return folder_path

def select_xml_source(intended_tool_id: str, esettings: ToolExeSettings) -> str:
    assert(esettings.xmldir)
    xmls = [x for x in os.listdir(esettings.xmldir) if x.endswith('.xml') and 'macros' not in x]
    if len(xmls) == 0:  # if no xmls, theres some error
        pass
    elif len(xmls) == 1:  # if only 1 valid xml, return
        return xmls[0]
    else: # else, open each and look at the tool_id and match to esettings
        for xml_file in xmls:
            full_path = os.path.join(esettings.xmldir, xml_file)
            xml_tool_id = etree_utils.get_xml_tool_id(full_path)
            if xml_tool_id == intended_tool_id:
                return xml_file
    raise RuntimeError('no valid tool xml in downloaded wraper folder')
            

