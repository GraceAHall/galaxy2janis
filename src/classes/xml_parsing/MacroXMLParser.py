


import xml.etree.ElementTree as et
import os

from classes.logging.Logger import Logger

class MacroXMLParser:
    def __init__(self, workdir: str, filename: str, logger: Logger) -> None:
        self.workdir = workdir
        self.filename = filename
        self.logger = logger
        self.set_tree()
        self.root = self.tree.getroot()
        self.tokens: dict[str, str] = {}
        self.macros: dict[str, et.Element] = {}

 
    def set_tree(self) -> None:
        filepath = ''
        if os.path.exists(f'{self.workdir}/{self.filename}'):
            filepath = f'{self.workdir}/{self.filename}'
        elif os.path.exists(f'macros/{self.filename}'):
            filepath = f'macros/{self.filename}'
        else:
            raise Exception(f'cannot find macro file {self.filename}')

        self.tree = et.parse(filepath)


    def parse(self) -> None:
        self.collect()
        self.expand()


    def collect(self) -> None:
        for node in self.tree.iter():
            self.parse_node(node)


    def parse_node(self, node: et.Element) -> None:
        if node.tag == 'import':
            self.import_xml(node)
        elif node.tag == 'token':
            self.add_token(node)
        elif node.tag in ['xml', 'macro']:
            self.add_macro(node)
            
        for child in node:
            self.parse_node(child)


    def import_xml(self, node: et.Element) -> None:
        xml_file = node.text or ""
        mp = MacroXMLParser(self.workdir, xml_file, self.logger)
        mp.collect()
        self.tokens.update(mp.tokens)
        self.macros.update(mp.macros)


    def add_token(self, node: et.Element) -> None:
        key = node.attrib['name']
        val = node.text or ""
        self.tokens[key] = val
        

    def add_macro(self, node: et.Element) -> None:
        macro_name = node.attrib['name']
        self.macros[macro_name] = node


    def expand(self) -> None:
        self.expand_macros(self.root)
        self.check_macro_expansion(self.root)


    def expand_macros(self, parent: et.Element) -> None:
        """
        expands <expand> elements
        <expand> yield statements are handled here
        <expand> tokens are also handled

        iterates through child nodes, inserting relevant macro using etree insert() when an <expand> elem is encountered.

        original <expand> elem is deleted at end of function to avoid iteration errors. 
        """
        
        expand_elems_to_delete = []

        for i, child in enumerate(parent):
            if child.tag == 'expand':
                # mark the expand elem for removal
                expand_elems_to_delete.append(child)  # type: ignore

                # fetch the relevant macro element
                macro = self.fetch_macro_elem(child)
                
                # handle macro yield statement if necessary (modifies macro in-place)
                self.resolve_yield_statments(macro, child)

                # apply macro tokens to macro (modifies macro in-place)
                self.resolve_macro_tokens(macro)
                
                # append macro to parent (each child elem of macro)
                for j, elem in enumerate(macro):
                    parent.insert(i+j+1, elem)
            
            # recursive (macro inside macro)
            self.expand_macros(child)

        
        for child in expand_elems_to_delete:  # type: ignore
            parent.remove(child)  # type: ignore


    def fetch_macro_elem(self, node: et.Element) -> et.Element:
        macro_name = node.attrib['macro']
        return self.macros[macro_name]


    def resolve_yield_statments(self, macro: et.Element, expand_elem: et.Element) -> None:
        for macro_child in macro:
            if macro_child.tag == 'yield':
                macro.remove(macro_child)

                for expand_child in expand_elem:
                    macro.append(expand_child)

            else:
                self.resolve_yield_statments(macro_child, expand_elem)
    
    
    def resolve_macro_tokens(self, macro: et.Element) -> None:
        # init token dict
        local_tokens: dict[str, str] = {}

        # extract all tokens supplied in macro def
        for key, val in macro.attrib.items():
            if key.startswith('token_'):
                token = '@' + key[6:].upper() + '@'
                local_tokens[token] = val

        # resolve token values in the macro
        for child in macro:
            self.apply_macro_tokens(child, local_tokens)

        
    def apply_macro_tokens(self, node: et.Element, tokens: dict[str, str]) -> None:
        # for each attribute, identify any embedded tokens and map the token to realised value.
        for att_key, att_val in node.attrib.items():
            for tok_key, tok_val in tokens.items():
                if tok_key in att_val:
                    node.attrib[att_key] = att_val.replace(tok_key, tok_val)
                    
        # also check if the text contains a token (command can contain tokens)
        if node.text:
            for tok_key, tok_val in tokens.items():
                if tok_key in node.text:
                    node.text = node.text.replace(tok_key, tok_val)
                   
        # recursive
        for child in node:
            self.apply_macro_tokens(child, tokens)


    def check_macro_expansion(self, node: et.Element) -> None:
        for child in node:
            assert(child.tag != 'expand')
            self.check_macro_expansion(child)


    def write_tree(self, filepath: str) -> None:
        #et.dump(self.root)
        with open(filepath, 'w') as f:
            self.tree.write(f, encoding='unicode')