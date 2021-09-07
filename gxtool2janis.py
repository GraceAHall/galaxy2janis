

import sys

from classes.parsers.ToolParser import ToolParser
import xml.etree.ElementTree as et

# main entry point
def main(argv):
    filename = argv[0]
    workdir = argv[1]

    tp = ToolParser(filename, workdir)

    # preprocessing
    tp.parse_macros()
    tp.parse_tokens()
    tp.write_tree('output.xml')
    
    # params
    tp.parse_params()
    tp.write_tree('output.xml')
    
    # command
    #tp.parse_command()
    #tp.write_tree('output.xml')
    
    # metadata
    #tp.parse_metadata()
    #tp.write_tree('output.xml')

    # generate janis! 
    print()


if __name__ == '__main__':
    main(sys.argv[1:])






    

