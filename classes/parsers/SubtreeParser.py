
# pyright: basic

from copy import deepcopy
import xml.etree.ElementTree as et

from classes.datastructures.Param import Param

class SubtreeParser:
    def __init__(self, filename: str, workdir: str, root: et.Element):
        self.filename = filename
        self.workdir = workdir
        self.root = root
        self.galaxy_depth_elems = ['conditional', 'section']
        self.ignore_elems = ['outputs', 'tests']
        self.parsable_elems = []
        self.subtree_elems = []
        self.tree_path = []
        self.tokens = {}


    def parse(self) -> None:
        for child in self.root:
            if self.should_descend(child):
                self.explore_node(child, self.tree_path)
        self.print() #type: ignore


    # recursively explore node
    def explore_node(self, node: et.Element, prev_path: list[str]) -> None:
        # would this extend the galaxy variable path?
        curr_path = deepcopy(prev_path)
        if node.tag in self.galaxy_depth_elems:
            curr_path.append(node.attrib['name'])

        # Should we parse this node or just continue?
        if node.tag in self.parsable_elems:
            self.parse_elem(node, curr_path)

        # Should we parse node as new independent subtree?
        if node.tag in self.subtree_elems:
            self.parse_subtree(node, curr_path)

        # descend to child nodes (recursive)
        for child in node:
            if self.should_descend(child):
                self.explore_node(child, curr_path)


    def should_descend(self, node: et.Element) -> bool:
        if node.tag in self.ignore_elems:
            return False
        return True


    def parse_elem(self, node: et.Element, tree_path: list[str]) -> None:
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
            self.parse_param(node, tree_path)
        elif node.tag == 'expand':
            self.parse_expand(node, tree_path)
        elif node.tag == 'repeat':
            self.parse_repeat(node, tree_path)
        elif node.tag == 'import':
            self.import_xml(node)


    def parse_token(self, node: et.Element) -> None:
        key = node.attrib['name']
        val = node.text
        self.tokens[key] = val
        

    def parse_option_list(self, node):
        pass


    def parse_citations(self, node):
        pass


    def parse_description(self, node):
        pass

    
    def parse_container(self, node):
        pass


    def parse_help(self, node):
        pass


    def parse_param(self, node, tree_path):
        param = Param(node, tree_path)
        param.parse()
        self.add_param(param)


    def parse_expand(self, node, tree_path):
        pass


    def parse_repeat(self, node, tree_path):
        pass

    
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
        






