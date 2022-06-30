


import os
import tarfile
from typing import Optional


class DownloadCache:
    """
    keeps track of the location of downloaded wrapper folders.
    DownloadCache.get() will return the local path to a tool xml if already downloaded
    DownloadCache.add() saves a tar as a download and notes its path. 
    """

    def __init__(self, wrappers_folder: str):
        self.directory = wrappers_folder
        self.cache: set[str] = self._load()

    def get(self, query_repo: str, query_revision: str) -> Optional[str]:
        """returns the local file path for the tool xml if already downloaded or None"""
        for wrapper in self.cache:
            repo, revision = wrapper.split('-', 1)
            if repo == query_repo and revision == query_revision:
                return f'{self.directory}/{wrapper}'
        return None

    def add(self, tar: tarfile.TarFile) -> None:
        self._save(tar)
        self.cache = self._load()

    def _save(self, tar: tarfile.TarFile) -> None:
        tar.extractall(path=self.directory)

    def _load(self) -> set[str]:
        wrappers = os.listdir(self.directory)
        wrappers = [w for w in wrappers if os.path.isdir(f'{self.directory}/{w}')]
        return set(wrappers)

