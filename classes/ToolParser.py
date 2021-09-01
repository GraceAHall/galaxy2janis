

from xml.etree import ElementTree as et

# Class to read galaxy tool xml. Heavy use of etree.
class ToolParser:
    def __init__(self, tool_dir, tool_xml):
        self.tool_dir = tool_dir
        self.tool_xml = tool_xml
        self.set_macro_files()


    def set_macro_files(self):
        xml = et.parse(f'{self.tool_dir}/{self.tool_xml}')
        root = xml.getroot()
        imports = root.find('macros').findall('import')

        macro_files = []
        for elem in imports:
            macro_files.append(elem.text)

        self.macro_files = macro_files


    def expand_macros(self):
        # expand macros in tool xml and any imported macro files. 
        # macros need to be expanded 
        macro_expander = 
        for filename in self.macro_files:
            xml = et.parse(f'{self.tool_dir}/{filename}')
            root = xml.getroot()
            print()
        pass


# macro expansion
# - 


    def find_recursive(self):
        pass




    def expand_xml(self):
        xml = et.parse(self.macros)
        root = xml.getroot()

        


