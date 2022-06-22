


from Bio import pairwise2

def global_align(pattern: str, template: str) -> int:
    pattern = pattern.lower()
    template = template.lower()
    outcome = pairwise2.align.globalms(pattern, template, 2, -1, -.5, -.1) # type: ignore
    if len(outcome) > 0: # type: ignore
        score = outcome[0].score # type: ignore
    else:
        score = 0
    return score # type: ignore

def is_int(the_string: str) -> bool:
    if the_string.isdigit():
        return True
    return False

def is_float(the_string: str) -> bool:
    if not is_int(the_string):
        try:
            float(the_string)
            return True
        except ValueError:
            pass
    return False

