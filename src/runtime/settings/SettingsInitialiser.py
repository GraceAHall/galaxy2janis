

from typing import Optional
from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings



class WorkflowSettingsInitialiser:

    def init_settings(self, args: dict[str, Optional[str]]) -> WorkflowExeSettings:
        esettings = WorkflowExeSettings(
            workflow=args['workflow'], # type: ignore
        )
        if args['outdir']:
            esettings.user_outdir = args['outdir']
        if args['cachedir']:
            esettings.user_container_cachedir = args['cachedir']
        return esettings


class ToolSettingsInitialiser:

    def init_settings(self, args: dict[str, Optional[str]]) -> ToolExeSettings:
        esettings = ToolExeSettings(
            xmlfile=args['xml'], 
            xmldir=args['dir'],
            remote_url=args['remote_url'],
            user_download_dir=args['download_dir']
        )
        if args['outdir']:
            esettings.user_outdir = args['outdir']
        if args['cachedir']:
            esettings.user_container_cachedir = args['cachedir']
        return esettings