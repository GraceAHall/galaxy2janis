
ALL = r'.+'

QUOTES = r'[\'"]'
QUOTED_SECTIONS = r'"(.*?)"|\'(.*?)\''
QUOTED_STRINGS = r'(\'.*?(?<!\\)\')|(".*?(?<!\\)")'
QUOTED_NUMBERS = r'[\'"](?<!\w)(-?\d+(\.\d+)?)(?!\d)[\'"]'

RAW_NUMBERS = r'(?<=\s|^)-?\.?\d+(\.\d*)?(?=\s|$)'
RAW_STRINGS = r'(?<=\s|^)([\/\\\w\d-.*`])[-\w\d\{\}\$.\/\\_:*`]*(?=\s|$)'
SIMPLE_STRINGS = r'[\w$_-]+'
#NUMBERS_QUOTED_STRINGS = r'(\'.*?(?<!\\)\')|(".*?(?<!\\)")|(?<!\w)(-?\d+(\.\d+)?)(?!\d)'

WORDS = r'(\'.*?(?<!\\)\'[^\s]*)|(".*?(?<!\\)"[^\s]*)|([^\s]+)'
KEYVAL_PAIRS = r'(?<=\s|^)(\S+?)([=:])(\S+?)(?=\s|$)'

VARIABLES = r'\$\{?[\w.]+\}?'
GX_DYNAMIC_KEYWORDS = r'\\?\$\{?_?GALAXY_.*?[\s:]-(\w+?)\}'
GX_STATIC_KEYWORDS = r'\$__tool_directory__|\$__new_file_path__|\$__tool_data_path__|\$__root_dir__|\$__datatypes_config__|\$__user_id__|\$__user_email__|\$__app__|\$__target_datatype__'

SH_STATEMENT_DELIMS = r'(?<!\\)(&&|\|?\|(?! tee |tee ))(?=\s|$)' 
SH_REDIRECT = r'((?<=\s)\d|&)?>[>&]?(?![>&]?\d)'
SH_TEE = r'(?<![\d&])\| ?tee( -a)?'
SH_STREAM_MERGE = r'(?<=\s|^)\d?>&\d'

OPERATOR = r'[-+\\/*=]?='
VERSIONS = r'(\d+)(\.\d+)*'