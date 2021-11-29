


#pyright: basic

import os
from typing import Tuple
import argparse

from classes.tool.ToolXMLParser import ToolXMLParser
import xml.etree.ElementTree as et

# main entry point
def main():
    args = handle_program_args()

    # check we have the right file
    if is_valid_tool_xml(args.toolxml, args.tooldir):
        
        # init outdir and contents
        out_log, out_def = init_out_files(args.toolxml, args.tooldir)

        # parse tool 
        tp = ToolXMLParser(args.toolxml, args.tooldir, out_log, out_def, debug=args.debug)
        tp.parse()
    

def handle_program_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("toolxml", help="tool xml file")
    parser.add_argument("tooldir", help="tool directory")
    parser.add_argument( "--debug", help="run in debug mode (writes many lines to stdout)", action="store_true")
    args = parser.parse_args()

    if args.debug:
        print('running in debug mode')

    return args



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
    basename = filename[:-4]
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
    main()






    

