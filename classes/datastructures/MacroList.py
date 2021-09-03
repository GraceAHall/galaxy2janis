



class MacroList:
    def __init__(self):
        self.name = None
        self.imports = []
        self.params = []
        self.macros = []
        self.tokens = {}

    
    def add_macro(self, macro):
        self.macros.append(macro)