

# pyright: strict

import xml.etree.ElementTree as et



class CommandParser:
    def __init__(self, tree: et.ElementTree):
        self.tree = tree
        self.command_string = ''


    def parse(self) -> None:
        self.set_command_string()
        print()


    def set_command_string(self) -> None:
        root = self.tree.getroot()
        
        # <command> only permitted as child of <tool>
        for child in root:
            if child.tag == 'command':
                self.command_string = child.text

