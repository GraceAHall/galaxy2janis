


# files
DATATYPES = 'data/datatypes/gxformat_combined_types.yaml'
WRAPPER_CACHE = 'data/wrappers.json'
CONTAINER_CACHE = 'data/container_url_cache.json'
LOGGING_CONFIG = 'data/logging_config.yaml'

# folders
DOWNLOADED_WRAPPERS_DIR = 'data/wrappers'
DEFAULT_TOOL_OUTDIR = 'parsed/tools'
DEFAULT_WORKFLOW_OUTDIR = 'parsed/workflows'


from .managers import PathManager
from .managers import ToolModePathManager
from .managers import WorkflowModePathManager

manager: PathManager

def init_manager(name: str) -> None:
    global manager
    match name:
        case 'tool':
            manager = ToolModePathManager()
        case 'workflow':
            manager = WorkflowModePathManager()
        case _:
            raise RuntimeError()

