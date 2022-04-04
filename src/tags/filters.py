

prohibited_keys = {
    "identifier",
    "tool",
    "scatter",
    "ignore_missing",
    "output",
    "input",
    "inputs"
}

def format_capitalisation(tag: str) -> str:
    # allow first letter capital, rest lower
    if len(tag) > 1:
        return tag.lower()
    return tag[0]

def replace_non_alphanumeric(tag: str) -> str:
    """
    to satisfy janis tag requirements
    to avoid janis reserved keywords
    """
    tag = tag.strip('\\/-$')
    tag = tag.replace('-', '_')
    tag = tag.replace('(', '')
    tag = tag.replace(')', '')
    tag = tag.replace('.', '_')
    tag = tag.replace(' ', '_')
    tag = tag.replace('|', '_')
    tag = tag.replace('/', '_')
    tag = tag.replace('\\', '_')
    tag = tag.replace('"', '')
    tag = tag.replace("'", '')
    return tag

def handle_prohibited_key(tag: str) -> str:
    if tag in prohibited_keys:
        tag = f'{tag}_param'
    return tag

def handle_short_tag(tag: str, details: dict[str, str]) -> str:
    if len(tag) == 1 and 'datatype' in details:
        if tag[0].isnumeric():
            tag = f"{details['datatype']}_{tag}"
        else:
            tag = f"{tag}_{details['datatype']}"
    return tag

def encode(tag: str) -> str:
    return fr'{tag}'
