




from typing import Optional
from fileio.imports.Import import Import, ImportType
import formats.workflow_definition.snippets as snippets
from entities.workflow.input import WorkflowInput
from entities.workflow.output import WorkflowOutput
from entities.workflow.workflow import WorkflowStep



# GENERAL

def format_docstring(entity: WorkflowStep | WorkflowInput | WorkflowOutput) -> Optional[str]:
    raw_doc = entity.docstring
    if raw_doc:
        return raw_doc.replace('"', "'")
    return None

def format_imports(imports: list[Import]) -> str:
    dtype_imports = [x for x in imports if x.itype == ImportType.DATATYPE]
    class_imports = [x for x in imports if x.itype == ImportType.JANIS_CLASS]
    tool_imports = [x for x in imports if x.itype == ImportType.TOOL_DEF]
    step_imports = [x for x in imports if x.itype == ImportType.STEP_DEF]
    out: str = ''
    for i, category in enumerate([dtype_imports, class_imports, tool_imports, step_imports]):
        if category:
            if i > 0:
                out += '\n'
            for imp in category:
                out += snippets.import_snippet(imp)
    return out


# WORKFLOW

def format_workflow_input(tag: str, inp: WorkflowInput) -> str:
    return snippets.workflow_input_snippet(
        tag=tag,
        datatype=inp.get_janis_datatype_str(),
        doc=format_docstring(inp)
    )

def format_workflow_output(tag: str, output: WorkflowOutput) -> str:
    return snippets.workflow_output_snippet(
        tag=tag,
        datatype=output.get_janis_datatype_str(),
        step_tag=output.step_tag,
        toolout_tag=output.toolout_tag
    )




