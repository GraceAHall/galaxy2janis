


from startup.ExeSettings import ToolExeSettings, WorkflowExeSettings

MOCK_TOOL_ESETTINGS = ToolExeSettings(
    xmlfile='abricate.xml',
    xmldir='test/data/abricate',
    remote_url=None,
    parent_outdir='test/temp',
    container_cachedir='test/temp/container_cache.json'
)

MOCK_WORKFLOW_ESETTINGS = WorkflowExeSettings(
    workflow='test/data/workflows/simple_workflow.ga',
    parent_outdir='test/temp',
    container_cachedir='test/temp/container_cache.json'
)






