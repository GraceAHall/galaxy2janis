


from abc import ABC, abstractmethod
from file_io.initialisation import init_file
from file_io.initialisation import init_folder
from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings


data_folders = set([
    'data/containers',
    'data/datatypes',
    'data/wrappers',
    'data/xml',
])


class FileInitialiser(ABC):

    def initialise(self) -> None:
        folders = self.get_folders_to_init()
        for path in folders:
            init_folder(path)
        
        files = self.get_files_to_init()
        for path, contents in files.items():
            init_file(path, contents=contents)
    
    @abstractmethod
    def get_folders_to_init(self) -> list[str]:
        ...
    
    @abstractmethod
    def get_files_to_init(self) -> dict[str, str]:
        ...


class WorkflowFileInitialiser(FileInitialiser):

    def __init__(self, esettings: WorkflowExeSettings):
        self.esettings = esettings

    def get_folders_to_init(self) -> list[str]:
        folders: set[str] = set()
        folders = folders | data_folders
        folders.add(self.esettings.outdir)
        folders.add(self.esettings.get_xml_wrappers_dir())
        folders.add(self.esettings.get_janis_tools_dir())
        folders.add(self.esettings.get_janis_steps_dir())
        return list(folders)

    def get_files_to_init(self) -> dict[str, str]:
        files: dict[str, str] = dict()
        files[self.esettings.container_cachedir] = '{}'
        files[self.esettings.get_janis_workflow_path()] = ''
        return files


class ToolFileInitialiser(FileInitialiser):
    
    def __init__(self, esettings: ToolExeSettings):
        self.esettings = esettings

    def get_folders_to_init(self) -> list[str]:
        folders: set[str] = set()
        folders.add(self.esettings.download_dir) 
        folders.add(self.esettings.get_outdir()) 
        return list(folders)

    def get_files_to_init(self) -> dict[str, str]:
        files: dict[str, str] = dict()
        files[self.esettings.container_cachedir] = '{}'
        files[self.esettings.get_janis_definition_path()] = ''
        files[self.esettings.get_logfile_path()] = ''
        return files

