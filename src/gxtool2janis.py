

import sys
import os

from classes.parsers.ToolParser import ToolParser
import xml.etree.ElementTree as et

# main entry point
def main(argv):
    filename = argv[0]
    workdir = argv[1]
    outdir = init_outdir(filename, workdir)

    tp = ToolParser(filename, workdir, outdir)
    tp.parse()

    # generate janis! 
    print()


def init_outdir(filename: str, workdir: str) -> str:
    outdir = get_outdir_path(filename, workdir)
    wipe_dir(outdir)
    touch_log(outdir)
    return outdir


def get_outdir_path(filename: str, workdir: str) -> str:
    outdir = filename.split('.', 1)[0]
    outdir = f'parsed_tools/{outdir}'
    if not os.path.exists(outdir):
        os.mkdir(outdir) 
    return outdir


def wipe_dir(direct: str) -> None:
    files = os.listdir(direct)
    for f in files:
        os.remove(f'{direct}/{f}')


def touch_log(direct: str) -> None:
    with open(f'{direct}/log.txt', 'w') as fp:
        pass



if __name__ == '__main__':
    main(sys.argv[1:])






    

