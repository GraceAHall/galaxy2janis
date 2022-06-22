


from typing import Optional

tool_path: str
dev_test_cmdstrs: bool
forced_outdir: Optional[str] = None
owner: Optional[str] = None
repo: Optional[str] = None
revision: Optional[str] = None
tool_id: Optional[str] = None

# properties
def xml_basename() -> str:
    return tool_path.rsplit('/', 1)[-1].split('.')[0]

def xml_dir() -> str:
    if '/' not in tool_path:
        return '.'
    return tool_path.rsplit('/', 1)[0]

def logfile_path() -> str:
    return f'{xml_basename()}.log'


# setting
def set_dev_test_cmdstrs(value: bool) -> None:
    global dev_test_cmdstrs
    dev_test_cmdstrs = value

def set_owner(value: str) -> None:
    global owner
    owner = value

def set_repo(value: str) -> None:
    global repo
    repo = value

def set_tool_id(value: str) -> None:
    global tool_id
    tool_id = value

def set_revision(value: str) -> None:
    global revision
    revision = value

def set_tool_path(value: str) -> None:
    global tool_path
    tool_path = value


