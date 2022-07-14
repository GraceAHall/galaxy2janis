
import logs.logging as logging
import requests
import tarfile
from typing import Optional

import utils.galaxy as utils
from gx.wrappers.downloads.cache import DownloadCache

from paths import DOWNLOADED_WRAPPERS_DIR
CACHE: DownloadCache = DownloadCache(DOWNLOADED_WRAPPERS_DIR)


def fetch_wrapper(owner: str, repo: str, revision: str, tool_id: str) -> str:
    """gets the wrapper locally or from toolshed then returns path to xml"""
    path: Optional[str] = None
    if not path:
        path = _fetch_cache(repo, revision, tool_id)
    if not path:
        path = _fetch_toolshed(owner, repo, revision, tool_id)
    if not path:
        raise RuntimeError(f'could not find wrapper for {tool_id}:{revision}')
    else:
        return path

def _fetch_cache(repo: str, revision: str, tool_id: str) -> Optional[str]:
    wrapper = CACHE.get(repo, revision)
    if wrapper:
        xml = utils.get_xml_by_id(wrapper, tool_id)
        if xml:
            return f'{wrapper}/{xml}'
    return None

def _fetch_toolshed(owner: str, repo: str, revision: str, tool_id: str) -> Optional[str]:
    # download and add to cache
    url = _get_url_via_revision(owner, repo, revision)
    logging.msg_downloading_tool(url)
    tar = _download_wrapper(url)
    CACHE.add(tar)
    # fetch from cache
    return _fetch_cache(repo, revision, tool_id)

def _get_url_via_revision(owner: str, repo: str, revision: str) -> str:
    return f'https://toolshed.g2.bx.psu.edu/repos/{owner}/{repo}/archive/{revision}.tar.gz'

def _download_wrapper(url: str) -> tarfile.TarFile:
    response = requests.get(url, stream=True)
    return tarfile.open(fileobj=response.raw, mode='r:gz')


