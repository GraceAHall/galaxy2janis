
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

@nostdout
def main():
    print('hello')

if __name__ == '__main__':
    main()