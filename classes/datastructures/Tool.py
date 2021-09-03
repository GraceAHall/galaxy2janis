



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
        self.tokens = {}

    
    def add_container(self, type, image):
        new_container = {"type": type, "image": image}
        self.containers.append(new_container) 