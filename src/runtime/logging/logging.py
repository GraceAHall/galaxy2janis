
from logging import getLogger, config
from typing import Optional
import warnings
import yaml
import sys 

from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings

# -------------
# configuration
# -------------

# logging 
def configure_tool_logging(esettings: ToolExeSettings) -> None:
    with open("src/runtime/logging/logging_config.yaml", "r") as fp:
        the_dict = yaml.safe_load(fp)
        the_dict['handlers']['tool_file']['filename'] = esettings.get_logfile_path()
    config.dictConfig(the_dict)

def configure_workflow_logging(esettings: WorkflowExeSettings) -> None:
    with open("src/runtime/logging/logging_config.yaml", "r") as fp:
        the_dict = yaml.safe_load(fp)
        the_dict['handlers']['workflow_file']['filename'] = esettings.get_logfile_path()
    config.dictConfig(the_dict)


# warnings configuration
def configure_warnings() -> None:
    warnings.filterwarnings("ignore")


# -------
# logging
# -------

# messages
def msg_parsing_tool(filename: str):
    print(f'parsing tool {filename}')

def msg_parsing_workflow(filename: str):
    print(f'parsing workflow {filename}')

def msg_downloading_tool(url: str):
    print(f'downloading tool repo from {url}')


# info
# (just runtime data and info messages which don't impact program)
def runtime_data(data: str):
    logger = getLogger('tool')
    logger.info(str(data))

def evaluation_failed():
    logger = getLogger('tool')
    logger.info('cheetah evaluation failed')


# warning
# (things that MAY cause issues)
def has_preprocessing():
    logger = getLogger('tool')
    logger.warning('preprocessing')

def has_postprocessing():
    logger = getLogger('tool')
    logger.warning('postprocessing')

def has_backtick_statement():
    logger = getLogger('tool')
    logger.warning('backtick statement')

def has_multiline_str():
    logger = getLogger('tool')
    logger.warning('multiline string')

def has_repeat():
    logger = getLogger('tool')
    logger.warning('repeat param')

def has_cheetah_loop(text: Optional[str]=None):
    logger = getLogger('tool')
    logger.warning(f'cheetah loop:\t{text}')

def has_cheetah_function():
    logger = getLogger('tool')
    logger.warning('cheetah function')

def uncertain_output():
    logger = getLogger('tool')
    logger.warning('uncertain outputs')

def unlinked_input_connection():
    logger = getLogger('workflow')
    logger.warning('unknown input')

def has_configfile():
    logger = getLogger('tool')
    logger.warning('configfile')

def zero_length_tag():
    logger = getLogger('tool')
    logger.warning('zero length tag')

def workflow_step_array_connections():
    logger = getLogger('workflow')
    logger.warning('workflow step array connections')

# def has_bash_script():
#     logger = getLogger('tool')
#     logger.warning('bash script')





# error
# (things that WILL cause issues)
def no_container():
    logger = getLogger('tool')
    logger.error('no container')

def no_ga4gh_data():
    logger = getLogger('tool')
    logger.error('no ga4gh data')

def no_inputs():
    logger = getLogger('tool')
    logger.error('no inputs')

def no_outputs():
    logger = getLogger('tool')
    logger.error('no outputs')

def no_base_cmd():
    logger = getLogger('tool')
    logger.error('no base cmd')

# critical (exceptions)
def tool_exception():
    logger = getLogger('tool')
    logger.critical('exception')
    sys.exit(1)

def no_close_quotation():
    logger = getLogger('tool')
    logger.critical('no closing quotation')
    sys.exit(1)

def workflow_exception():
    logger = getLogger('workflow')
    logger.critical('exception')
    sys.exit(1)
