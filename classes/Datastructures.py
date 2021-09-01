



#configfiles are handled as params

class Tool:
    def __init__(self):
        self.name = None
        self.command = None
        self.version = None
        self.creator = None
        self.containers = [] # from requirements tag
        self.tool_module = 'bioinformatics' 
        self.macros = []
        self.params = []
        self.inputs = []
        self.outputs = []
        self.tests = []
        self.help = None
        self.citations = None
        self.expands = []

    
    def add_container(self, type, image):
        new_container = Container(type, image)
        self.containers.append(new_container) 


class MacroList:
    def __init__(self):
        self.name = None
        self.imports = []
        self.params = []
        self.macros = []
        self.tokens = {}

    
    def add_macro(self, macro):
        self.macros.append(macro)



# similar to Tool class 
# Macros shouldn't have command elems, but have tag params & yield statements.

class Macro:
    def __init__(self, name):
        self.name = name
        self.has_yield = False
        self.version = None
        self.creator = None
        self.containers = [] # from requirements tag
        self.params = []
        self.output_data = []
        self.tests = []
        self.help = None
        self.citations = None
        self.expands = []


    def add_container(self, type, image):
        new_container = Container(type, image)
        self.containers.append(new_container) 

    def add_param(self, param):
        self.params.append(param)


class Container:
    def __init__(self):
        self.type = None
        self.image = None


    def print(self):
        print('\nclass: container')
        print(f'type: {self.type}')
        print(f'image: {self.image}')






class Expand:
    def __init__(self, macro_reference, local_path):
        self.macro_reference = macro_reference
        self.local_path = local_path