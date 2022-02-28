


import os
from startup.ExeSettings import ToolExeSettings, WorkflowExeSettings


def init_files(filepaths: list[str]) -> None:
    for path in filepaths:
        init_file(path)

def init_file(filepath: str) -> None:
    # remove file if already exists
    if os.path.exists(filepath):
        os.remove(filepath)
    # touch file
    with open(filepath, 'w') as fp: # type: ignore
        pass

def safe_init_file(filepath: str) -> None:
    if not os.path.exists(filepath):
        init_file(filepath)

def init_cache_dir(filepath: str) -> None:
    if not os.path.exists(filepath):
        with open(filepath, 'w') as fp:
            fp.write('{}')

def safe_init_folders(folders: list[str]) -> None:
    for folder in folders:
        if not os.path.isdir(folder):
            os.mkdir(folder)


class WorkflowFileInitialiser:

    def initialise(self, esettings: WorkflowExeSettings) -> None:
        self.esettings = esettings
        folders = self.get_folders_to_init()
        files = self.get_files_to_init()
        safe_init_folders(folders)
        init_files(files)
        init_cache_dir(self.esettings.get_container_cache_path())
    
    def get_folders_to_init(self) -> list[str]:
        es = self.esettings
        folders = [
            es.get_parent_outdir(),
        ]
        return [f for f in folders if type(f) is str] 

    def get_files_to_init(self) -> list[str]:
        return []


class ToolFileInitialiser:

    def initialise(self, esettings: ToolExeSettings) -> None:
        self.esettings = esettings
        folders = self.get_folders_to_init()
        files = self.get_files_to_init()
        safe_init_folders(folders)
        init_files(files)
        init_cache_dir(self.esettings.get_container_cache_path())

    def get_folders_to_init(self) -> list[str]:
        es = self.esettings
        folders = [
            es.parent_outdir,   # the parent folder
            es.get_outdir(),     # the subfolder for this tool
        ]
        return [f for f in folders if type(f) is str] 

    def get_files_to_init(self) -> list[str]:
        es = self.esettings
        return [
            es.get_logfile_path(),
            es.get_janis_definition_path()
        ]

