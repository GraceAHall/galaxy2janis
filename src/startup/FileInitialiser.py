


import os
from startup.ExeSettings import ToolExeSettings, WorkflowExeSettings

default_folders = []
#     'runtimefiles'
# ]

default_files = []
#     'runtimefiles/tool_name_tagregister.json',
#     'runtimefiles/tool_input_tagregister.json',
#     'runtimefiles/tool_output_tagregister.json',
#     'runtimefiles/workflow_name_tagregister.json',
#     'runtimefiles/workflow_step_tagregister.json',
#     'runtimefiles/workflow_input_tagregister.json',
#     'runtimefiles/workflow_output_tagregister.json'
# ]

def init_files(filepaths: list[str]) -> None:
    for path in filepaths:
        init_file(path)

def init_file(filepath: str) -> None:
    # remove file if already exists
    if os.path.exists(filepath):
        os.remove(filepath)
    # touch file
    with open(filepath, 'w') as fp: # type: ignore
        if filepath.endswith('.json'):
            fp.write('{}')
        else:
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
        folders: list[str] = default_folders
        es = self.esettings
        folders.append(es.get_outdir())
        folders.append(es.get_xml_wrappers_dir())
        folders.append(es.get_janis_tools_dir())
        folders.append(es.get_janis_steps_dir())
        folders = list(set(folders))
        folders.sort(key=lambda x: len(x))
        return folders

    def get_files_to_init(self) -> list[str]:
        files: list[str] = default_files
        es = self.esettings
        # files.append(es.get_janis_workflow_path())
        # files.append(es.get_janis_workflow_configfile_path())
        return list(set(files))


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
        folders: list[str] = default_folders
        folders.append(es.get_outdir())     # the subfolder for this tool
        folders = list(set([f for f in folders if type(f) is str]))
        folders.sort(key=lambda x: len(x))
        return folders

    def get_files_to_init(self) -> list[str]:
        files: list[str] = default_files
        es = self.esettings
        #files.append(es.get_logfile_path())
        #files.append(es.get_janis_definition_path())
        return list(set(files))

