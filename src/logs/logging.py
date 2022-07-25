
from logging import getLogger, config
from typing import Optional

import warnings
import yaml
import sys 

import paths
import settings

# -------------
# configuration
# -------------


# logging 
def configure_logging() -> None:
    with open(paths.LOGGING_CONFIG, "r") as fp:
        the_dict = yaml.safe_load(fp)
        the_dict['handlers']['janis_log']['filename'] = paths.manager.janis_log()
        the_dict['handlers']['message_log']['filename'] = paths.manager.message_log()
    config.dictConfig(the_dict)

# warnings configuration
def configure_warnings() -> None:
    warnings.filterwarnings("ignore")

# -------
# logging
# -------

# messages
def msg_parsing_tool():
    print(f'parsing tool {settings.tool.tool_path}')

def msg_parsing_workflow():
    print(f'parsing workflow {settings.workflow.workflow_path}')

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
    logger.info(f'cheetah loop')

def has_cheetah_function():
    logger = getLogger('tool')
    logger.info('cheetah function')

def no_base_cmd():
    logger = getLogger('tool')
    logger.info('no base cmd')

def has_configfile():
    logger = getLogger('tool')
    logger.info('configfile')

def no_container():
    logger = getLogger('tool')
    logger.info('no container')

def no_ga4gh_data():
    logger = getLogger('tool')
    logger.info('no ga4gh data')

def container_version_mismatch():
    logger = getLogger('tool')
    logger.info('container version mismatch')

def color_param_ignored():
    logger = getLogger('tool')
    logger.info('ignored unsupported param type: color')

def uncertain_output():
    logger = getLogger('tool')
    logger.info('uncertain outputs')

def unlinked_input_connection():
    logger = getLogger('workflow')
    logger.info('unknown input')


# warning
# (things that will probably cause issues and require human editing in the workflow)

def no_inputs():
    logger = getLogger('tool')
    logger.warning('no inputs')

def no_outputs():
    logger = getLogger('tool')
    logger.warning('no outputs')

def zero_length_tag():
    logger = getLogger('tool')
    logger.warning('zero length tag')

# error
# (unsupported features)

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
