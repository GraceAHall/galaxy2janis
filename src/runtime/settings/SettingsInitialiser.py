

from typing import Optional
from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings



class WorkflowSettingsInitialiser:

    def init_settings(self, args: dict[str, Optional[str]]) -> WorkflowExeSettings:
        return WorkflowExeSettings(
            workflow=args['workflow'], # type: ignore
            outdir=self.format_outdir(args),
            container_cachedir=self.format_cachedir(args),
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

    def init_settings(self, args: dict[str, Optional[str]]) -> ToolExeSettings:
        return ToolExeSettings(
            download_dir=self.format_download_dir(args),
            container_cachedir=self.format_cachedir(args),
            xmlfile=args['xml'], 
            xmldir=args['dir'],
            remote_url=args['remote_url'],
            user_outdir=self.format_user_outdir(args),
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