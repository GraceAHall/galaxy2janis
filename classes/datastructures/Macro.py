





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
        new_container = {"type": type, "image": image}
        self.containers.append(new_container) 


    def add_param(self, param):
        self.params.append(param)

