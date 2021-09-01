

from classes.Datastructures import Tool, MacroList, Macro, Container, Param

class SubtreeParser:
    def __init__(self, root, tree_position):
        self.root = root
        self.tree_position = tree_position
        self.galaxy_depth_elems = ['conditional', 'section']
        self.parsable_elems = None
        self.subtree_elems = None
        self.subtree_parser = None  # set when instantiating class


    # explore
    def parse(self):
        children = self.root.getchildren()
        print()
        for child in children:
            self.explore_node(child, self.tree_position)
        self.print()


    # recursively explore node
    def explore_node(self, node, position):
        # would this node count as a galaxy level?
        if node.tag in self.galaxy_depth_elems:
            position.append(node.attrib['name'])

        # Should we parse this node or just continue?
        if node.tag in self.parsable_elems:
            self.parse_elem(node, position)

        # Should we parse node as new independent subtree?
        if node.tag in self.subtree_elems:
            self.parse_subtree(node, position)

        # descend to child nodes
        children = node.getchildren()
        for child in children:
            self.explore_node(child, position)


    def parse_elem(self, node, position):
        if node.tag == 'token':
            self.parse_token(node)
        elif node.tag == 'citations':
            self.parse_citations(node)
        elif node.tag == 'description':
            self.parse_description(node)
        elif node.tag == 'container':
            self.parse_container(node)
        elif node.tag == 'help':
            self.parse_help(node)
        elif node.tag == 'param':
            self.parse_param(node, position)
        elif node.tag == 'expand':
            self.parse_expand(node, position)
        elif node.tag == 'repeat':
            self.parse_repeat(node, position)
        elif node.tag == 'import':
            self.import_xml(node)


    def parse_token(self, node):
        key = node.attrib['name']
        val = node.text
        self.add_token(key, val)
        

    def parse_citations(self, node):
        pass


    def parse_description(self, node):
        pass

    
    def parse_container(self, node):
        pass


    def parse_help(self, node):
        pass


    def parse_param(self, node, position):
        param_name = self.get_attribute_value(node, 'name')
        param_type = self.get_param_type(node)

        # param basics
        new_param = Param(param_name, param_type)
        new_param.default_value = self.get_attribute_value(node, 'value')
        new_param.help_text = self.get_attribute_value(node, 'help')

        # is param optional?
        if self.get_attribute_value(node, 'optional') == "true":
            new_param.is_optional = True
        
        # is param an argument param?
        if self.get_attribute_value(node, 'argument') is not None:
            argument = self.get_attribute_value(node, 'argument')
            new_param.name = argument.lstrip('-').replace('-', '_') 
            new_param.prefix = argument 
            new_param.is_argument = True

        # set param local path
        local_path = '.'.join(position)
        if local_path == '':
            new_param.local_path = new_param.name
        else:
            new_param.local_path = local_path + f'.{new_param.name}'
            
        self.add_param(new_param)


    def get_param_type(self, node):
        pass


    def parse_expand(self, node, position):
        pass


    def parse_repeat(self, node, position):
        pass


    def get_attribute_value(self, node, attribute):
        '''
        accepts node, returns attribute value or None 
        '''
        for key, val in node.attrib.items():
            if key == attribute:
                return val
        return None

    
    def print_details(self, classname, entity):
        print(f'\n===== {classname} =====')
        print(f'name: {entity.name}')

        if hasattr(entity, 'version') and entity.version != None:
            print(f'version: {entity.version}')
        
        if hasattr(entity, 'creator') and entity.creator != None:
            print(f'creator: {entity.creator}')
        
        if hasattr(entity, 'help') and entity.help != None:
            print(f'help: {entity.help}')
        
        if hasattr(entity, 'citations') and entity.citations != None:
            print(f'citations: {entity.citations}')

        if hasattr(entity, 'tokens') and len(entity.tokens) != 0:
            print('\ntokens --------')
            for key, val in entity.tokens.items():
                print(f'{key}: {val}')

        if hasattr(entity, 'params') and len(entity.params) != 0:
            print('\nparams --------')
            for param in entity.params:
                param.print()

        if hasattr(entity, 'containers') and len(entity.containers) != 0: 
            print('\ncontainers --------')
            for container in entity.containers:
                container.print()
        
        if hasattr(entity, 'expands') and len(entity.expands) != 0: 
            print('\nexpands --------')
            for expand in entity.expands:
                print(f'macro name: {expand.macro_reference}')
                print(f'local path: {expand.local_path}')
        



class ToolParser(SubtreeParser):
    def __init__(self, root, tree_position):
        super().__init__(root, tree_position)
        self.parsable_elems = ['token', 'description', 'expand', 'command', 'param', 'repeat', 'tests', 'help', 'citations']
        self.subtree_elems = ['macros']
        self.tool = Tool()
        self.set_metadata()


    def set_metadata(self):
        self.tool.name = self.root.attrib['id']
        self.tool.version = self.root.attrib['version']


    def print(self):
        self.print_details('Tool', self.tool)


    def parse_command(self):
        pass


    def parse_subtree(self, node, position):
        # create new Parser to parse subtree. 
        # override.
        mp = MacrosParser(node, position)
        mp.parse()
        self.tool.macros += mp.macrolist.macros
        
        
    def add_token(self, key, val):
        self.tool.tokens[key] = val


    def add_param(self, param):
        self.tool.params.append(param)
  

    def add_container(self, container):
        self.tool.containers.append(container)



# parse all macros inside a <macros> element
class MacrosParser(SubtreeParser):
    def __init__(self, root, tree_position):
        super().__init__(root, tree_position)
        self.parsable_elems = ['import', 'token'] 
        self.subtree_elems = ['macro', 'xml']
        self.subtrees = [] # will only be MacroParser
        self.macrolist = MacroList()


    def print(self):
        self.print_details('Macro list', self.macrolist)


    # only macros tags allow imports
    def import_xml(self, node):
        # create new XMLDoc
        # parse that doc 
        pass


    def parse_subtree(self, node, position):
        # create new Parser to parse subtree. 
        # override.
        macro = MacroParser(node, position)
        macro.parse()
        # absorb results into current MacrosParser
        self.macrolist.add_macro(macro) # will be a single Macro()
        # tokens?
        # imports?


    def add_token(self, key, val):
        self.macrolist.tokens[key] = val
    


# parse a single <macro> or <xml> element
class MacroParser(SubtreeParser):
    def __init__(self, root, tree_position):
        super().__init__(root, tree_position)
        self.parsable_elems = ['token', 'description', 'expand', 'param', 'repeat', 'tests', 'help', 'citations', 'container']
        self.subtree_elems = []  # macros can't have macro definitions inside. Can reference other macros. 
        self.set_tag_tokens()
        self.macro = Macro(self.root.attrib['name'])


    def print(self):
        self.print_details('Macro', self.macro)


    def set_tag_tokens(self):
        for key, val in self.root.attrib.items():
            if key.startswith('token_'):
                token_name = '@' + key.lstrip('token_').upper() + '@'
                token_value = val
                self.tokens[token_name] = token_value


    def parse_container(self, node):
        container_type = self.get_attribute_value('type')
        container_image = node.text
        self.datastructure.add_container(container_type, container_image)


    def add_param(self, param):
        self.macro.params.append(param)
  

    def add_container(self, container):
        self.macro.containers.append(container)


    def add_token(self, key, val):
        self.macro.tokens[key] = val



