


import os
from runtime.settings import ExecutionSettings


class ProjectFileInitialiser:
    def __init__(self, esettings: ExecutionSettings) -> None:
        self.esettings = esettings

    def initialise(self) -> None:
        self.safe_init_folders()
        self.init_files()

    def safe_init_folders(self) -> None:
        for folder in self.get_folders_to_init():
            if not os.path.isdir(folder):
                os.mkdir(folder)

    def get_folders_to_init(self) -> list[str]:
        es = self.esettings
        folders = [
            es.parent_outdir,   # the parent folder
            es.get_outdir(),     # the subfolder for this tool
        ]
        return [f for f in folders if type(f) is str] 

    def init_files(self) -> None:
        files_to_init = self.get_files_to_init()
        for filepath in files_to_init:
            self.init_file(filepath)
        self.init_cache_dir()

    def get_files_to_init(self) -> list[str]:
        es = self.esettings
        return [
            es.get_logfile_path(),
            es.get_janis_definition_path()
        ]

    def init_file(self, filepath: str) -> None:
        # remove file if already exists
        if os.path.exists(filepath):
            os.remove(filepath)
        # touch file
        with open(filepath, 'w') as fp: # type: ignore
            pass

    def safe_init_file(self, filepath: str) -> None:
        if not os.path.exists(filepath):
            self.init_file(filepath)

    def init_cache_dir(self) -> None:
        filepath = self.esettings.get_container_cache_path()
        if not os.path.exists(filepath):
            with open(filepath, 'w') as fp:
                fp.write('{}')