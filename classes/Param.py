





class Param:
    def __init__(self, node, tree_path):
        self.node = node
        self.tree_path = tree_path
        self.name = None
        self.type = None
        self.local_path = None
        self.default_value = None
        self.prefix = None
        self.help_text = None
        self.is_optional = False
        self.is_argument = False
        self.is_ui_param = False


    def parse(self):
        self.set_basic_details()
        self.set_is_argument()
        self.set_local_path()


    def set_basic_details(self):
        # basic info
        self.name = self.get_attribute_value('name')
        self.type = self.get_janis_type()
        self.default_value = self.get_attribute_value('value')
        self.help_text = self.get_attribute_value('help')

        # is param optional?
        if self.get_attribute_value('optional') == "true":
            self.is_optional = True
        

    def set_is_argument(self):
        # is param an argument param?
        if self.get_attribute_value('argument') is not None:
            argument = self.get_attribute_value('argument')
            self.name = argument.lstrip('-').replace('-', '_') 
            self.prefix = argument 
            self.is_argument = True


    def set_local_path(self):
        # set param local path
        local_path = '.'.join(self.tree_path)
        if local_path == '':
            self.local_path = self.name
        else:
            self.local_path = local_path + f'.{self.name}'
            
        
    def get_janis_type(self):
        galaxy_type = self.get_attribute_value('type')
        galaxy_format = self.get_attribute_value('format')
        """
        text: string
        integer: integer
        float: float

        boolean: 
         - has truevalue and falseval. map of 0/1 to strings

        genomebuild
        select
        color
        data_column
        hidden
        hidden_data
        baseurl
        file
        ftpfile
        data:
         - dataset from history
         - 'format' determines datatype - format can be comma-separated list so multiple types. Is galaxy doing type conversion here? 
         - for tool io
         - multiple="true" specifies array of files as input
         

        data_collection
        library_data
        drill_down
        """



    def get_attribute_value(self, attribute):
        '''
        accepts node, returns attribute value or None 
        '''
        for key, val in self.node.attrib.items():
            if key == attribute:
                return val
        return None


    def print(self):
        print('\nclass: param')
        print(f'name: {self.name}')
        print(f'local_path: {self.local_path}')
        print(f'type: {self.type}')
        print(f'prefix: {self.prefix}')
        print(f'default: {self.default_value}')
        print(f'help_text: {self.help_text}')
        print(f'is_optional: {self.is_optional}')
        print(f'is_argument: {self.is_argument}')
        print(f'is_ui_param: {self.is_ui_param}')