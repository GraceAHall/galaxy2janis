

import argparse
import sys
from typing import Optional

useage_str = '''
gxtool2janis command [OPTIONS]

Commands:
   tool         Parse single galaxy tool
   workflow     Parse all tools in a galaxy workflow

'''

class CLIparser:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='gxtool2janis.py',
            usage=useage_str
        )
        parser.add_argument('command', help='Command')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print(f'Unrecognized command {sys.argv[1]}')
            parser.print_help()
            exit(1)
        # dispatch pattern (calls the function with same name as args.command)
        self.command = args.command
        getattr(self, args.command)()

    def tool(self):
        parser = argparse.ArgumentParser(
            description='Parse single galaxy tool'
        )
        parser.add_argument("-d",
                            "--dir", 
                            help="tool directory. used with --xml. must contain tool.xml and any other required tool files", 
                            type=str)
        parser.add_argument("-x",
                            "--xml", 
                            help="tool xml. used with --dir. the specific tool.xml file to parse within --dir.", 
                            type=str)
        parser.add_argument("-r",
                            "--remote_url", 
                            help="toolshed url. used in place of --dir and --xml. downloads tool from the toolshed and parses",
                            type=str)
        parser.add_argument("-o",
                            "--outdir", 
                            help="parent folder to place output janis definitions. default='parsed/'", 
                            type=str)
        parser.add_argument("-c",
                            "--cachedir", 
                            help="path to local container cache. default='./'", 
                            type=str)
        args = parser.parse_args(sys.argv[2:])
        out: dict[str, Optional[str]] = args.__dict__
        out['command'] = self.command
        self.args = out

    def workflow(self):
        parser = argparse.ArgumentParser(
            description='') 
        parser.add_argument('repository')
        args = parser.parse_args(sys.argv[2:])
        out: dict[str, Optional[str]] = args.__dict__
        out['command'] = self.command
        self.args = out


if __name__ == '__main__':
    CLIparser()