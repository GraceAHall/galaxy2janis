

import argparse
from typing import Optional

from classes.execution.settings import ExecutionSettings, InputWorkflow, RunMode
from classes.execution.validation import SettingsValidator
from classes.execution.file_initialisation import ProjectFileInitialiser

def startup(argv: list[str]) -> ExecutionSettings:
    esettings = create_execution_settings(argv)
    validate_settings(esettings)
    setup_files(esettings)
    return esettings


def create_execution_settings(argv: list[str]) -> ExecutionSettings:
    args = get_args(argv)
    esettings = init_settings(args)
    workflow = init_workflow(args)
    
    if workflow:
        esettings.add_workflow(workflow)
    return esettings
  

def get_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("xmlfile", 
                        help="tool xml file", 
                        type=str)
    parser.add_argument("xmldir", 
                        help="tool directory", 
                        type=str)
    parser.add_argument("-o",
                        "--outdir", 
                        help="parent folder for parsed tools", 
                        type=str)
    parser.add_argument("-w", 
                        "--wflow", 
                        type=str,
                        help="Must be used with --wstep. workflow_file[str]. parses the provided .ga workflow  during runtime to help understand tool.")
    parser.add_argument("-s", 
                        "--wstep", 
                        type=int,
                        help="Must be used with --wflow. workflow_step[int]. parses the provided step from the .ga workflow given in --wflow.")
    parser.add_argument("-d",
                        "--debug",
                        help="run in debug mode (writes many lines to stdout)", 
                        action="store_true")
    args = parser.parse_args(argv)
    return args


def init_settings(args: argparse.Namespace) -> ExecutionSettings:
    esettings = ExecutionSettings(
        args.xmlfile, 
        args.xmldir.rstrip('/'),
        args.outdir
    )
    if args.debug:
        esettings.runmode = RunMode.DEBUG
    return esettings


def init_workflow(args: argparse.Namespace) -> Optional[InputWorkflow]:
    if args.wflow and args.wstep:
        return InputWorkflow(args.wflow, args.wstep)


def validate_settings(esettings: ExecutionSettings) -> None:
    sv = SettingsValidator(esettings)
    sv.validate()


def setup_files(esettings: ExecutionSettings) -> None:
    pfi = ProjectFileInitialiser(esettings)
    pfi.initialise()
