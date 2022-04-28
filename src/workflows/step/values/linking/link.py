






# module entry
def link_step_input_values(workflow: Workflow):
    for step in workflow.list_steps():
        assert(step.tool)
        # assign actual Param objects to gxparam field of inputs
        step.inputs.assign_gxparams(step.tool)  
        linker = InputValueLinker(step, workflow)
        #linker = CheetahValueLinker(step, workflow)
        linker.link()