






# module entry
from workflows.step.values.linking.CheetahValueLinker import CheetahValueLinker
from workflows.step.values.linking.InputDictValueLinker import InputDictValueLinker
from workflows.workflow.Workflow import Workflow


def link_step_input_values(workflow: Workflow):
    for step in workflow.list_steps():
        assert(step.tool)
        # assign actual Param objects to gxparam field of inputs
        step.inputs.assign_gxparams(step.tool)  
        #linker = InputDictValueLinker(step, workflow)
        linker = CheetahValueLinker(step, workflow)
        step.values = linker.link()