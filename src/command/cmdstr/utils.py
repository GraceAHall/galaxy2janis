

from Bio import pairwise2
import shlex


def split_lines(cmdstr: str) -> list[str]:
    lines = cmdstr.split('\n')
    lines = [ln.strip() for ln in lines]
    lines = [ln for ln in lines if ln != '']
    return lines 

def join_lines(lines: list[str]) -> str:
    return '\n'.join(lines)

def split_to_words(line: str) -> list[str]:
    return shlex.split(line)

def global_align(pattern: str, template: str) -> int:
    pattern = pattern.lower()
    template = template.lower()
    outcome = pairwise2.align.globalms(pattern, template, 2, -1, -.5, -.1) # type: ignore
    if len(outcome) > 0: # type: ignore
        score = outcome[0].score # type: ignore
    else:
        score = 0
    return score # type: ignore