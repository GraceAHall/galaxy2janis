


from typing import Any, Optional, Tuple
from datetime import datetime

from galaxy2janis.entities.workflow import Workflow
from galaxy2janis.entities.workflow import WorkflowInput
from galaxy2janis.entities.workflow import WorkflowMetadata
from galaxy2janis.entities.workflow import InputValue
from galaxy2janis.entities.workflow import StepOutput
from galaxy2janis.entities.workflow import WorkflowStep
from galaxy2janis.entities.workflow import StaticInputValue
from galaxy2janis.entities.workflow import ConnectionInputValue
from galaxy2janis.entities.workflow import WorkflowInputInputValue
from galaxy2janis.runtime.dates import JANIS_DATE_FMT
from galaxy2janis import tags

from janis_core.graph.node import Node
from janis_core import WorkflowBuilder
from janis_core import CommandToolBuilder
from janis_core import ScatterDescription
from janis_core import ScatterMethods
from janis_core import WorkflowMetadata as JanisWorkflowMetadata

from .general import to_janis_datatype
from .tool import to_janis_tool


### MODULE EXPORTS

def to_janis_workflow(internal: Workflow) -> WorkflowBuilder:
    """
    maps internal model workflow to janis model workflow
    missing the following (unnecessary?):
        friendly_name
        tool_provider
        tool_module
    """
    wf = WorkflowBuilder(
        identifier=internal.tag,
        version=internal.metadata.version,
        metadata=_to_janis_workflow_metadata(internal.metadata),
        doc=internal.metadata.annotation
    )
    for internal_inp in internal.inputs:
        _add_input(internal_inp, wf)
    for internal_step in internal.steps:
        _add_step(internal_step, wf)
    for internal_out in internal.outputs:
        _add_output(internal_out, wf)
    return wf

def to_janis_inputs_dict(internal: Workflow) -> dict[str, Any]:
    out_dict: dict[str, Any] = {}
    for internal_inp in internal.inputs:
        key = internal_inp.tag
        val = internal_inp.value if internal_inp.value else None
        out_dict[key] = val
    return out_dict



### HELPER METHODS ###

def _to_janis_workflow_metadata(internal: WorkflowMetadata) -> JanisWorkflowMetadata:
    contributors = ['gxtool2janis']
    return JanisWorkflowMetadata(
        short_documentation=internal.annotation,
        contributors=contributors,
        keywords=internal.tags,
        dateCreated=datetime.today().strftime(JANIS_DATE_FMT),
        dateUpdated=datetime.today().strftime(JANIS_DATE_FMT),
        version=internal.version
    )

def _add_input(internal: WorkflowInput, wf: WorkflowBuilder) -> None:
    """
    missing wf.input.default (not supported in galaxy)
    """
    wf.input(
        identifier=internal.tag,
        datatype=to_janis_datatype(internal),
        value=internal.value,
        doc=internal.docstring, # type: ignore
    )

def _add_output(internal: StepOutput, wf: WorkflowBuilder) -> None:
    """
    missing the following (unnecessary):
        output_folder
        output_name
        extension
    """
    step_tag = tags.get(internal.step_uuid)
    step_node = wf.nodes[step_tag]
    out_tag = internal.tool_output.tag
    wf.output(
        identifier=f'{step_tag}_{out_tag}',
        datatype=to_janis_datatype(internal),
        source=(step_node, out_tag),
        doc=internal.tool_output.docstring,  # type: ignore
    )

def _add_step(internal: WorkflowStep, wf: WorkflowBuilder) -> None:
    """
    missing the following (unnecessary / feature not in galaxy):
        _foreach
        when
        ignore_missing
    """
    step_tag = internal.tag
    tool = to_janis_tool(internal.tool)
    _set_tool_input_values(internal, tool, wf)
    scatter_names = _get_scatter_input_names(internal)
    scatter_obj = _get_scatter_object(scatter_names)
    wf.step(
        identifier=step_tag,
        tool=tool,
        scatter=scatter_obj,        # type: ignore
        doc=internal.metadata.label
    )

def _set_tool_input_values(internal: WorkflowStep, tool: CommandToolBuilder, wf: WorkflowBuilder) -> None:
    for invalue in internal.inputs.all: # TODO ordering? currently unordered
        if invalue.component:
            tag = invalue.input_tag
            value = _get_input_value(invalue, wf)
            tool.connections[tag] = value
        else:
            # TODO LOG  (unknown input)
            pass
    
def _get_input_value(invalue: InputValue, wf: WorkflowBuilder) -> Any | Node | Tuple[Node, str]:
    match invalue:
        case StaticInputValue():
            return invalue.raw_value                        # Any
        case WorkflowInputInputValue():
            str_value = invalue.wrapped_value
            node_tag = str_value.split('.')[-1]
            return wf.input_nodes[node_tag]                 # Node
        case ConnectionInputValue():
            str_value = invalue.wrapped_value
            node_tag = str_value.split('.')[-2]
            out_tag = str_value.split('.')[-1]
            return (wf.step_nodes[node_tag], out_tag)       # Tuple[Node, str]
        case _:
            return None

def _get_scatter_input_names(internal: WorkflowStep) -> list[str]:
    unknown_count: int = 0
    names: list[str] = []
    invalues = internal.inputs.all
    for val in invalues:
        if val.component and val.scatter:
            if not val.component:
                unknown_count += 1
                names.append(f'{val.input_tag}{unknown_count}')  # TODO attention
            else:
                names.append(val.input_tag)
        else:
            # TODO LOG  (scatter on unknown input)
            pass
    return names

def _get_scatter_object(names: list[str]) -> Optional[str | ScatterDescription]:
    if len(names) == 0:
        return None
    elif len(names) == 1:
        return names[0]
    else:
        return ScatterDescription(fields=names, method=ScatterMethods.dot)

