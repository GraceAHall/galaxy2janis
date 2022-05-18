
#sys.path.append('./galaxy/lib')

#import logging
from logging import config
import logging
import warnings
import yaml
import sys
from typing import Optional
from startup.CLIparser import CLIparser

from parse_tool import parse_tool
from parse_workflow import parse_workflow
from runtime.settings import load_tool_settings
from runtime.ExeSettings import ToolExeSettings
from runtime.settings import load_workflow_settings
from runtime.ExeSettings import WorkflowExeSettings
from file_io.write import write_tool, write_workflow

"""
gxtool2janis program entry point
parses cli settings then hands execution to other files based on command
"""

def main():
    configure_logging()
    configure_warnings()
    args = load_args()
    run_sub_program(args)

def configure_logging() -> None:
    with open("src/config/logging_config.yaml", "r") as fp:
        the_dict = yaml.safe_load(fp)
    config.dictConfig(the_dict)

def configure_warnings() -> None:
    warnings.filterwarnings("ignore")

def load_args() -> dict[str, Optional[str]]:
    parser = CLIparser(sys.argv)
    return parser.args

def run_sub_program(args: dict[str, Optional[str]]) -> None:
    match args['command']:
        case 'tool':
            run_tool_mode(args)
        case 'workflow':
            run_workflow_mode(args)
        case _:
            pass

def run_tool_mode(args: dict[str, Optional[str]]):
    esettings: ToolExeSettings = load_tool_settings(args) 
    tool = parse_tool(esettings)
    write_tool(esettings, tool)

def run_workflow_mode(args: dict[str, Optional[str]]):
    esettings: WorkflowExeSettings = load_workflow_settings(args)
    workflow = parse_workflow(esettings)
    write_workflow(esettings, workflow)
    

if __name__ == '__main__':
    main()



"""

#import re

#if str($in.custom) == 'false'
    #set $labels = ','.join( [re.sub('[^\w\-_]', '_', str($x.element_identifier)) for $x in $in.inputs])
    echo $labels &&
#else
    #set $labels = []
    #for $x in $in.inputs
        #if str($x.labels) != ''
            #silent $labels.append(re.sub('[^\w\-_]', '_', str($x.labels)))
        #else
            #silent $labels.append(re.sub('[^\w\-_]', '_', str($x.input.element_identifier)))
        #end if
    #end for
    #set $labels = ','.join($labels)
#end if

#if $assembly.type == 'metagenome' and $assembly.ref.origin == 'list'
    #set $temp_ref_list_fp = 'temp_ref_list_fp'
    #set $temp_ref_list_f = open($temp_ref_list_fp, 'w')
    #silent $temp_ref_list_f.write('\n'.join([x.strip() for x in $assembly.ref.references_list.split(',')]))
    #silent $temp_ref_list_f.close()
#end if

"""

"""


INPUT1 = #SET ME
FASTQC_OUTDIR = #SET ME
FASTQC_OUTDIR = #SET ME
FASTQC_OUTDIR = #SET ME
FASTQC_OUTDIR = #SET ME
FASTQC_OUTDIR = #SET ME
FASTQC_OUTDIR = #SET ME
FASTQC_OUTDIR = #SET ME
FASTQC_OUTDIR = #SET ME




w.step(
    "step4_fastqc",
    fastqc(
            quiet=False,
            extract=False,
            nogroup=false,
            outdir=RUNTIMEVALUE,
            contaminants=RUNTIMEVALUE,
            adapters=RUNTIMEVALUE,
            limits=RUNTIMEVALUE,
            kmers=7,
            f_file=RUNTIMEVALUE,
    )
)

"""

    

