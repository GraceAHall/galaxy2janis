




import sys
from xml.etree import ElementTree as et

from classes.SubtreeExplorer import SubtreeParser, ToolParser, MacrosParser, MacroParser
from classes.Datastructures import Tool, MacroList



# class to parse XML file
# 2nd level class, only ToolParser is above. 
# Each XML file will get an XMLParser. 
# The XML parser mostly just handles info relating to the XML doc. 
# A SubtreeExplorer actually explores the tree
class XMLDoc:
    def __init__(self, filepath):
        self.filepath = filepath 
        self.root = et.parse(self.filepath).getroot()
        if self.root.tag == 'tool':
            self.subtree_parser = ToolParser(self.root, [])
        elif self.root.tag == 'macros':
            self.subtree_parser = MacrosParser(self.root, [])


    def parse(self):
        self.subtree_parser.parse()



def main(argv):
    filepath = argv[0]
    parser = XMLDoc(filepath)
    parser.parse()
    print()



if __name__ == '__main__':
    main(sys.argv[1:])






    

