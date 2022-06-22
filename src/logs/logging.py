
from logging import getLogger, config
from typing import Optional
import warnings
import yaml
import sys 

import settings.tool.settings as tsettings
import settings.workflow.settings as wsettings
from runtime.paths import LOGGING_CONFIG

# -------------
# configuration
# -------------

# logging 
def configure_tool_logging() -> None:
    with open(LOGGING_CONFIG, "r") as fp:
        the_dict = yaml.safe_load(fp)
        the_dict['handlers']['tool_file']['filename'] = tsettings.logfile_path()
    config.dictConfig(the_dict)

def configure_workflow_logging() -> None:
    with open(LOGGING_CONFIG, "r") as fp:
        the_dict = yaml.safe_load(fp)
        the_dict['handlers']['workflow_file']['filename'] = wsettings.logfile_path()
    config.dictConfig(the_dict)


# warnings configuration
def configure_warnings() -> None:
    warnings.filterwarnings("ignore")


# -------
# logging
# -------

# messages
def msg_parsing_tool():
    print(f'parsing tool {tsettings.tool_path}')

def msg_parsing_workflow():
    print(f'parsing workflow {wsettings.workflow_path}')

def msg_downloading_tool(url: str):
    print(f'downloading wrapper from {url}')


# debug
# (just runtime data and info messages which don't impact program)
def runtime_data(data: str):
    logger = getLogger('tool')
    logger.debug(str(data))

def evaluation_failed():
    logger = getLogger('tool')
    logger.debug('cheetah evaluation failed')


# info
# (things that MAY cause issues or just metric collecting)

def has_preprocessing():
    logger = getLogger('tool')
    logger.info('preprocessing')

def has_postprocessing():
    logger = getLogger('tool')
    logger.info('postprocessing')

def has_backtick_statement():
    logger = getLogger('tool')
    logger.info('backtick statement')

def has_multiline_str():
    logger = getLogger('tool')
    logger.info('multiline string')

def has_repeat():
    logger = getLogger('tool')
    logger.info('repeat param')

def has_cheetah_loop(text: Optional[str]=None):
    logger = getLogger('tool')
    logger.info(f'cheetah loop:\t{text}')

def has_cheetah_function():
    logger = getLogger('tool')
    logger.info('cheetah function')

def no_base_cmd():
    logger = getLogger('tool')
    logger.info('no base cmd')

# warning
# (things that WILL cause issues and require human editing in the workflow)

def uncertain_output():
    logger = getLogger('tool')
    logger.warning('uncertain outputs')

def unlinked_input_connection():
    logger = getLogger('workflow')
    logger.warning('unknown input')

def zero_length_tag():
    logger = getLogger('tool')
    logger.warning('zero length tag')

def no_inputs():
    logger = getLogger('tool')
    logger.warning('no inputs')

def no_outputs():
    logger = getLogger('tool')
    logger.warning('no outputs')

def no_container():
    logger = getLogger('tool')
    logger.warning('no container')

def no_ga4gh_data():
    logger = getLogger('tool')
    logger.warning('no ga4gh data')

def container_version_mismatch():
    logger = getLogger('tool')
    logger.warning('container version mismatch')

# error
# (unsupported features)

def has_configfile():
    logger = getLogger('tool')
    logger.error('configfile')

def workflow_step_array_connections():
    logger = getLogger('workflow')
    logger.error('workflow step array connections')
 
# critical
# (program failed - uncaught exceptions)

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
