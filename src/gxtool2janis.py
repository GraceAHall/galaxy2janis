


#pyright: strict

import sys
import os
from typing import Tuple
from classes.JanisFormatter import JanisFormatter

from classes.parsers.ToolParser import ToolParser
import xml.etree.ElementTree as et

# main entry point
def main(argv: list[str]):
    tool_xml = argv[0]
    tool_workdir = argv[1]
    
    # check we have the right file
    if is_valid_tool_xml(tool_xml, tool_workdir):
        
        # init outdir and contents
        out_log, out_def = init_out_files(tool_xml, tool_workdir)

        # parse tool 
        tp = ToolParser(tool_xml, tool_workdir, out_log)
        tp.parse()

        # generate janis py
        jf = JanisFormatter(tp, out_def)
        jf.format()
        jf.write()
        print()


def init_out_files(filename: str, workdir: str) -> Tuple[str, str]:
    outdir = get_outdir_path(workdir)
    out_log, out_def = get_filenames(filename, outdir)

    for filename in [out_log, out_def]:
        # wipe prev file
        if os.path.exists(filename):
            os.remove(filename)
        
        # touch new file
        with open(filename, 'w') as fp:
            pass

    return out_log, out_def


def get_outdir_path(workdir: str) -> str:
    folder = workdir.rsplit('/', 1)[-1]
    outdir = f'parsed_tools/{folder}'
    if not os.path.exists(outdir):
        os.mkdir(outdir) 
    return outdir


def get_filenames(filename: str, outdir: str) -> Tuple[str, str]:
    basename = filename.rstrip('.xml')
    out_log = f'{outdir}/{basename}.log'
    out_def = f'{outdir}/{basename}.py'
    return out_log, out_def


def is_valid_tool_xml(filename: str, workdir: str) -> bool:
    tree = et.parse(f'{workdir}/{filename}')
    root = tree.getroot()
    if root.tag == 'tool':
        return True
    return False


if __name__ == '__main__':
    main(sys.argv[1:])






    

