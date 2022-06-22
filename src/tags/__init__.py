


"""
Module governs tags within a workflow. 
Only the entities in this file should be accessed from external locations. 
"""

from .manager import ToolTagManager
from .manager import WorkflowTagManager

# SINGLETONS
tool = ToolTagManager()
workflow = WorkflowTagManager()