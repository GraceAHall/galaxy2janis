
import runtime.logging.logging as logging
import requests
import tarfile
from typing import Optional

from runtime.settings.ExeSettings import ToolExeSettings
from wrappers.cache import DownloadCache

import utils.general_utils as utils


CACHE: DownloadCache = DownloadCache('data/wrappers')


def fetch_wrapper(tool_id: str, esettings: ToolExeSettings) -> str:
    path: Optional[str] = None
    if not path:
        path = _fetch_cache(tool_id, esettings)
    if not path:
        path = _fetch_toolshed(tool_id, esettings)
    if not path:
        raise RuntimeError(f'could not find wrapper for {tool_id}')
    else:
        return path

def _fetch_cache(tool_id: str, esettings: ToolExeSettings) -> Optional[str]:
    assert(esettings.remote_url)
    repository: str = esettings.remote_url.rsplit('/', 3)[-3]
    revision: str = esettings.remote_url.rsplit('/', 1)[-1].split('.', 1)[0]
    directory = CACHE.get(repository, revision)
    if directory:
        xml = utils.get_xmlfile_by_tool_id(directory, tool_id)
        if xml:
            return f'{directory}/{xml}'
    return None

def _fetch_toolshed(tool_id: str, esettings: ToolExeSettings) -> Optional[str]:
    # download and add to cache
    assert(esettings.remote_url)
    logging.msg_downloading_tool(esettings.remote_url)
    tar = _download_wrapper(esettings.remote_url)
    CACHE.add(tar)
    # fetch from cache
    return _fetch_cache(tool_id, esettings)

def _download_wrapper(url: str) -> tarfile.TarFile:
    response = requests.get(url, stream=True)
    return tarfile.open(fileobj=response.raw, mode='r:gz')


