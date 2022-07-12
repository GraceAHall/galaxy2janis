

from datetime import datetime
from typing import Optional
from formats.workflow_definition.ToolInputLine import ToolInputLine
from formats.imports.Import import Import
from entities.workflow import InputValue



# GENERAL ----------------------------------

def import_snippet(imp: Import) -> str:
    return f'from {imp.path} import {imp.entity}\n'




# WORKFLOW ---------------------------------




# STEP -------------------------------------



