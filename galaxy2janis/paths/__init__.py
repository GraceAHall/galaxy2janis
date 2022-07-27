



# folders
DEFAULT_TOOL_OUTDIR = './parsed/tools'
DEFAULT_WORKFLOW_OUTDIR = './parsed/workflows'

from .managers import PathManager
from .managers import ToolModePathManager
from .managers import WorkflowModePathManager

manager: PathManager

def init_manager(name: str, outdir: str) -> None:
    global manager
    match name:
        case 'tool':
            manager = ToolModePathManager(outdir)
        case 'workflow':
            manager = WorkflowModePathManager(outdir)
        case _:
            raise RuntimeError()

