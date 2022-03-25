


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
        out: list[str] = []
        es = self.esettings
        out.append(es.get_outdir())
        out.append(es.get_xml_wrappers_dir())
        out.append(es.get_janis_tools_dir())
        out.append(es.get_janis_steps_dir())
        out = list(set(out))
        out.sort(key=lambda x: len(x))
        return out

    def get_files_to_init(self) -> list[str]:
        out: list[str] = []
        es = self.esettings
        out.append(es.get_janis_workflow_path())
        out.append(es.get_janis_workflow_configfile_path())
        return list(set(out))


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
            es.get_outdir(),     # the subfolder for this tool
        ]
        folders = list(set([f for f in folders if type(f) is str]))
        folders.sort(key=lambda x: len(x))
        return folders

    def get_files_to_init(self) -> list[str]:
        es = self.esettings
        return list(set([
            es.get_logfile_path(),
            es.get_janis_definition_path()
        ]))

