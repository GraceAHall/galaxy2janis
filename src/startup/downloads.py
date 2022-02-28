


import os
import tarfile
import wget


def download_repo(uri: str, folder: str) -> str:
    tarball_filename: str = wget.download(uri, out=folder)
    tar = tarfile.open(tarball_filename, "r:gz")
    tar.extractall(path=folder)
    tar.close()
    os.remove(tarball_filename)
    foldername = tarball_filename.rsplit('.tar', 1)[0]
    return foldername