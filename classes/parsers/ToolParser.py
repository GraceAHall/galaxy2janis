
# pyright: strict

from copy import deepcopy
import xml.etree.ElementTree as et

from classes.datastructures.Param import Param
from classes.datastructures.Tool import Tool
from classes.MacroExpander import MacroExpander
from classes.parsers.CommandParser import CommandParser



class ToolParser:
    def __init__(self, filename: str, workdir: str):
        self.filename = filename
        self.workdir = workdir
        self.tree: et.ElementTree = et.parse(f'{workdir}/{filename}')
        self.root: et.Element = self.tree.getroot()

        self.galaxy_depth_elems = ['conditional', 'section']
        self.ignore_elems = ['outputs', 'tests']
        self.parsable_elems = ['description', 'command', 'param', 'repeat', 'help', 'citations']

        self.tree_path: list[str] = []
        self.tokens: dict[str, str] = {}
        self.tool: Tool = Tool()


    def write_tree(self, filepath: str) -> None:
        et.dump(self.root)
        with open(filepath, 'w') as f:
            self.tree.write(f, encoding='unicode')


    def expand_macros(self) -> None:
        me = MacroExpander(self.workdir, self.filename)
        me.collect()
        me.expand()

        # update the xml tree
        self.tokens.update(me.tokens)
        self.tree = me.tree 
        self.root = self.tree.getroot() #type: ignore

        # QC
        self.confirm_macro_expansion(self.root)


    def confirm_macro_expansion(self, node: et.Element) -> None:
        for child in node:
            assert(child.tag != 'expand')
            self.confirm_macro_expansion(child)


    def resolve_tokens(self):
        self.gather_tokens(self.root)
        self.apply_tokens(self.root)


    def gather_tokens(self, node: et.Element) -> None:
        for child in node:
            if child.tag == 'token':
                self.add_token(node)
            # recursive
            self.gather_tokens(child)

    
    def add_token(self, node: et.Element) -> None:
        try: 
            key = node.attrib['name']
            val = node.text or ""
            self.tokens[key] = val
        except KeyError:
            pass


    def apply_tokens(self, node: et.Element) -> None:
        # for each attribute, identify any embedded tokens and map the token to realised value.
        if node.tag != 'token':

            for att_key, att_val in node.attrib.items():
                for tok_key, tok_val in self.tokens.items():
                    if tok_key in att_val:
                        att_val = att_val.replace(tok_key, tok_val)
                        node.attrib[att_key] = att_val
                        
            # also check if the text contains a token (command can contain tokens)
            if node.text:
                for tok_key, tok_val in self.tokens.items():
                    if tok_key in node.text:
                        node.text = node.text.replace(tok_key, tok_val)
                   
        # recursive
        for child in node:
            self.apply_tokens(child)


    def set_tool_metadata(self) -> None:
        self.tool.name = self.root.attrib['id']
        self.tool.version = self.root.attrib['version']


    def parse_command(self):
        cp = CommandParser(self.tree)
        cp.parse()
        print()


    def add_container(self, node: et.Element) -> None:
        key = node.attrib['name']
        val = node.text or ""
        self.tool.containers[key] = val


    def parse_params(self) -> None:
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
        param.set_basic_details()
        param.set_argument_info()
        self.add_param(param)


    def parse_repeat(self, node, tree_path):
        pass

    
    def pretty_print(self) -> str:
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






