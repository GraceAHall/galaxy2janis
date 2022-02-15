


import shlex


def split_lines(cmdstr: str) -> list[str]:
    lines = cmdstr.split('\n')
    lines = [ln.strip() for ln in lines]
    lines = [ln for ln in lines if ln != '']
    return lines 

def join_lines(lines: list[str]) -> str:
    return '\n'.join(lines)

def split_words(line: str) -> list[str]:
    return shlex.split(line)