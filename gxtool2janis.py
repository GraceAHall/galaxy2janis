

import sys

from classes.parsers.ToolParser import ToolParser
import xml.etree.ElementTree as et

# main entry point
def main(argv):
    filename = argv[0]
    workdir = argv[1]

    tp = ToolParser(filename, workdir)
    tp.expand_macros()
    tp.resolve_tokens()
    tp.set_tool_metadata()
    tp.parse_command()
    tp.write_tree('output.xml')
    print()


if __name__ == '__main__':
    main(sys.argv[1:])






    

