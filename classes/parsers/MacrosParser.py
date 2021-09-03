

from classes.parsers.SubtreeParser import SubtreeParser
from classes.parsers.MacroParser import MacroParser
from classes.datastructures.MacroList import MacroList
import xml.etree.ElementTree as et
from typing import Optional


# parse all macros inside a <macros> element
class MacrosParser(SubtreeParser):
    def __init__(self, filename: str, workdir: str, root: Optional[et.Element] = None):
        """
        init of this class is modified. 
        sometimes <macros> elem will be embedded in xml, othertimes it is the root elem of an import. if root elem is not given, go fetch the new import xml root & check its a <macros> elem. 
        """
        root = self.set_root(filename, workdir, root)  

        # now that we definitely have an et.Element, can init base class
        super().__init__(filename, workdir, root)
        
        self.parsable_elems = ['import', 'token'] 
        self.subtree_elems = ['macro', 'xml']
        self.subtrees = [] 
        self.macrolist = MacroList()
        

    def set_root(self, filename: str, workdir: str, root: Optional[et.Element]) -> et.Element:
        if root is None:
            filepath = f'{workdir}/{filename}'
            xml = et.parse(filepath)
            root = xml.getroot()
            assert(root.tag == 'macros')
        
        return root


    def print(self):
        self.print_details('Macro list', self.macrolist)


    # only macros tags allow imports
    def import_xml(self, node):
        # create a new MacrosParser for the import.xml
        # merge the MacrosParser return details into this instance of MacrosParser
        filename = node.text
        mp = MacrosParser(filename, self.workdir)
        mp.parse()
        print()


    def parse_subtree(self, node, tree_path):
        # create new Parser to parse subtree. 
        # override.
        macro = MacroParser(self.filename, self.workdir, node)
        macro.parse()
        # absorb results into current MacrosParser
        self.macrolist.add_macro(macro) # will be a single Macro()
        # tokens?
        # imports?


    def add_token(self, key, val):
        self.macrolist.tokens[key] = val
    