



from typing import Any
from workflows.step.metadata.StepMetadata import StepMetadata



def parse_step_metadata(gxstep: dict[str, Any]) -> StepMetadata:
    if 'tool_shed_repository' not in gxstep:
        return get_step_metadata_builtin(gxstep)
    else:
        return get_step_metadata_repo(gxstep)

def get_step_metadata_builtin(gxstep: dict[str, Any]) -> StepMetadata:
    return StepMetadata(
        uuid=gxstep['uuid'],
        step_id=gxstep['id'],
        step_name=gxstep['name'],
        tool_id=gxstep['tool_id'],
        tool_state=gxstep['tool_state'], 
        is_inbuilt=True,
        workflow_outputs=gxstep['workflow_outputs'],
        label=gxstep['label'],
        owner=None,
        changeset_revision=None,
        shed=None,
    )

def get_step_metadata_repo(gxstep: dict[str, Any]) -> StepMetadata:
    'toolshed.g2.bx.psu.edu/repos/devteam/picard/picard_MarkDuplicates/2.18.2.1'
    repo_url_split = gxstep['tool_id'].split('/')
    tool_id = repo_url_split[4]
    return StepMetadata(
        uuid=gxstep['uuid'],
        step_id=gxstep['id'],
        step_name=gxstep['name'],
        repo_name=gxstep['tool_shed_repository']['name'],
        tool_id=tool_id,
        tool_state=gxstep['tool_state'],
        is_inbuilt=False,
        workflow_outputs=gxstep['workflow_outputs'],
        label=gxstep['label'],
        owner=gxstep['tool_shed_repository']['owner'],
        changeset_revision=gxstep['tool_shed_repository']['changeset_revision'],
        shed=gxstep['tool_shed_repository']['tool_shed'],
    )
