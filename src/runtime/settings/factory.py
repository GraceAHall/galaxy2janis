

from typing import Any, Optional
from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings
from file_io.formats.paths import UnifiedPathManager


def create_workflow_settings(args: dict[str, Optional[str]]) -> WorkflowExeSettings:
    initialiser = WorkflowSettingsInitialiser()
    return initialiser.init_settings(args)

def create_tool_settings(args: dict[str, Optional[str]]) -> ToolExeSettings:
    initialiser = ToolSettingsInitialiser()
    return initialiser.init_settings(args)




class WorkflowSettingsInitialiser:

    def init_settings(self, args: dict[str, Any]) -> WorkflowExeSettings:
        return WorkflowExeSettings(
            workflow=args['workflow'], # type: ignore
            outdir=self.format_outdir(args),
            container_cachedir=self.format_cachedir(args),
            dev_no_test_cmdstrs=args['dev_no_test_cmdstrs'],
            dev_no_partial_eval=args['dev_no_partial_eval']
        )

    def format_outdir(self, args: dict[str, Optional[str]]) -> str:
        basename = args['workflow'].lower().replace('-', '_').rsplit('/', 1)[-1].rsplit('.', 1)[0] # type: ignore
        if args['outdir']:
            return f"{args['outdir']}/{basename}"
        return f'parsed/workflows/{basename}'
    
    def format_cachedir(self, args: dict[str, Optional[str]]) -> str:
        if args['cachedir']:
            return args['cachedir']
        return 'container_uri_cache.json'


class ToolSettingsInitialiser:

    def init_settings(self, args: dict[str, Any]) -> ToolExeSettings:
        return ToolExeSettings(
            download_dir=self.format_download_dir(args),
            container_cachedir=self.format_cachedir(args),
            xmlfile=args['xml'], 
            xmldir=args['dir'],
            remote_url=args['remote_url'],
            user_outdir=self.format_user_outdir(args),
            dev_no_test_cmdstrs=args['dev_no_test_cmdstrs']
        )

    def format_user_outdir(self, args: dict[str, Optional[str]]) -> Optional[str]:
        """
        can't be formatted straight away in case of tool download. 
        don't yet know the xml basename!
        """
        if args['outdir']:
            return args['outdir']
        return None
        
    def format_cachedir(self, args: dict[str, Optional[str]]) -> str:
        if args['cachedir']:
            return args['cachedir']
        return 'container_uri_cache.json'
    
    def format_download_dir(self, args: dict[str, Optional[str]]) -> str:
        if args['download_dir']:
            return args['download_dir']
        return './' #???