

# from stackoverflow: Alex Martelli
# https://stackoverflow.com/questions/2828953/silence-the-stdout-of-a-function-in-python-without-trashing-sys-stdout-and-resto


import sys
from typing import Any

class DummyFile(object):
    def write(self, x: Any): pass

def nostdout(func):  # type: ignore
    def wrapper(*args): # type: ignore
        save_stdout = sys.stdout  # save current stdout reference
        sys.stdout = DummyFile()  # set new dummy stdout reference
        res = func(*args)         # call function
        sys.stdout = save_stdout  # restore original stdout reference
        return res
    return wrapper

    

#import contextlib
# @contextlib.contextmanager
# def nostdout():
#     save_stdout = sys.stdout
#     sys.stdout = DummyFile()
#     yield
#     sys.stdout = save_stdout

