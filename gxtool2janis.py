

import sys

from classes.parsers.ToolParser import ToolParser
import xml.etree.ElementTree as et

# main entry point
def main(argv):
    filename = argv[0]
    workdir = argv[1]

    filepath = f'{workdir}/{filename}'
    xml = et.parse(filepath)
    root = xml.getroot()
    assert(root.tag == 'tool')

    doc = ToolParser(filename, workdir, root)
    doc.parse()
    print()


if __name__ == '__main__':
    main(sys.argv[1:])






    

