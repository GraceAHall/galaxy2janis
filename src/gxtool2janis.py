

import sys

from classes.parsers.ToolParser import ToolParser
import xml.etree.ElementTree as et

# main entry point
def main(argv):
    filename = argv[0]
    workdir = argv[1]

    tp = ToolParser(filename, workdir)
    tp.parse()

    # generate janis! 
    print()


if __name__ == '__main__':
    main(sys.argv[1:])






    

