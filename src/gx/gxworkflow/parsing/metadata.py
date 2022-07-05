


from typing import Any

from entities.workflow import Workflow
from entities.workflow.metadata import WorkflowMetadata


def ingest_metadata(workflow: Workflow, gxworkflow: dict[str, Any]) -> None:
    metadata = parse_metadata(gxworkflow)
    workflow.set_metadata(metadata)

def parse_metadata(gxworkflow: dict[str, Any]) -> WorkflowMetadata:
    """scrape basic workflow metadata"""
    return WorkflowMetadata(
        name=gxworkflow['name'],
        uuid=gxworkflow['uuid'],
        annotation=gxworkflow['annotation'],
        version=gxworkflow['version'],
        tags=gxworkflow['tags']
    )