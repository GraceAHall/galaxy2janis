
ALL = r'.+'


WITHIN_BRACKETS = r''
# within brackets = quoted sections, 


QUOTES = r'[\'"]'
QUOTED_SECTIONS = r'"([^\"]*?)"|\'([^\']*?)\''
QUOTED_STRINGS = r'(\'.*?(?<!\\)\')|(".*?(?<!\\)")'
QUOTED_NUMBERS = r'[\'"](?<!\w)(-?\d+(\.\d+)?)(?!\d)[\'"]'
QUOTED_SECTION_W_NEWLINE = r'\'[^\']*?\n[^\']*?\'|"[^"]*?\n[^"]*?"'
BACKTICK_SECTIONS = r'`.+?`'

RAW_NUMBERS = r'(?<=\s|^)-?\.?\d+(\.\d*)?(?=\s|$)'
RAW_STRINGS = r'(?<=\s|^)([\/\\\w\d-.*`@])[-\w\d\{\}\$.\/\\_:*`@]*(?=\s|$)'
SIMPLE_STRINGS = r'[\w$_-]+'

WORDS = r'(\'.*?(?<!\\)\'[^\s]*)|(".*?(?<!\\)"[^\s]*)|([^\s]+)'
KEYVAL_PAIRS = r'(?<=\s|^)(\S+?)([=:])(\S+?)(?=\s|$)'


VARIABLES_FMT1 = r'\$\w[\w._]+'
VARIABLES_FMT2 = r'\$\{\w[\w._]+\}'
FUNCTION_CALL_FMT1 = r'\$\{[^(].+?(\(.*\))[^(]*\}'
FUNCTION_CALL_FMT2 = r'\$[^(){} \n\'"]+(\(.*\))[^(){} \n\'"]*'

GX_DYNAMIC_KEYWORDS = r'\\?\$\{?_?GALAXY_.*?[\s:]-(\w+?)\}'
GX_STATIC_KEYWORDS = r'\$__tool_directory__|\$__new_file_path__|\$__tool_data_path__|\$__root_dir__|\$__datatypes_config__|\$__user_id__|\$__user_email__|\$__app__|\$__target_datatype__'

SH_STATEMENT_DELIMS = r'(?<!\\)(&&|\|?\|(?! tee |tee ))(?=\s|$)' 
SH_REDIRECT = r'((?<=\s)\d|&)?>[>&]?(?![>&]?\d)'
SH_TEE = r'(?<![\d&])\| ?tee( -a)?'
SH_STREAM_MERGE = r'(?<=\s|^)\d?>&\d'

OPERATOR = r'[-+\\/*=]?='
VERSIONS = r'(\d+)(\.\d+)*'

