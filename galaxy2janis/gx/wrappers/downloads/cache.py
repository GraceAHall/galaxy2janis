


import os
import tarfile
from typing import Optional

DOWNLOADED_WRAPPERS_DIR = 'galaxy2janis/gx/wrappers/data'

class DownloadCache:
    """
    keeps track of the location of downloaded wrapper folders.
    DownloadCache.get() will return the local path to a tool xml if already downloaded
    DownloadCache.add() saves a tar as a download and notes its path. 
    """

    def __init__(self):
        self.cache: set[str] = self._load()

    def get(self, query_repo: str, query_revision: str) -> Optional[str]:
        """returns the local file path for the tool xml if already downloaded or None"""
        for folder in self.cache:
            repo, revision = folder.split('-', 1)
            if repo == query_repo and revision == query_revision:
                return f'{DOWNLOADED_WRAPPERS_DIR}/{folder}'
        return None

    def add(self, tar: tarfile.TarFile) -> None:
        self._save(tar)
        self.cache = self._load()

    def _save(self, tar: tarfile.TarFile) -> None:
        tar.extractall(path=DOWNLOADED_WRAPPERS_DIR)

    def _load(self) -> set[str]:
        folders = os.listdir(DOWNLOADED_WRAPPERS_DIR)
        folders = [f for f in folders if os.path.isdir(f'{DOWNLOADED_WRAPPERS_DIR}/{f}')]
        return set(folders)

