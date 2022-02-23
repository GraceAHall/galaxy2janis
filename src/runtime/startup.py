

from typing import Optional
from runtime.settings import ToolExeSettings
#from runtime.settings import InputWorkflow
from runtime.validation import ArgsValidator, FileValidator
from runtime.file_initialisation import ProjectFileInitialiser


def load_settings(args: dict[str, Optional[str]]) -> ToolExeSettings:
    validate_args(args)
    esettings = init_execution_settings(args)
    validate_settings(esettings)
    setup_files(esettings)
    return esettings

def validate_args(args: dict[str, Optional[str]]):
    sv = ArgsValidator(args)
    sv.validate()

def init_execution_settings(args: dict[str, Optional[str]]) -> ToolExeSettings:
    esettings = ToolExeSettings(
        xmlfile=args['xml'], 
        xmldir=args['dir'],
        remote_url=args['remote_url'],
    )
    if args['outdir']:
        esettings.parent_outdir = args['outdir']
    if args['cachedir']:
        esettings.container_cachedir = args['cachedir']
    return esettings

def validate_settings(esettings: ToolExeSettings):
    fv = FileValidator(esettings)
    fv.validate()

# def init_workflow(args: argparse.Namespace) -> Optional[InputWorkflow]:
#     if args.wflow and args.wstep:
#         return InputWorkflow(args.wflow, args.wstep)

def setup_files(esettings: ToolExeSettings) -> None:
    pfi = ProjectFileInitialiser(esettings)
    pfi.initialise()
