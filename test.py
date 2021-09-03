
# pyright: strict

import xml.etree.ElementTree as et


class MacroExpander:
    def __init__(self):
        self.xml = et.parse('test.xml')
        self.root = self.xml.getroot()
        self.macros: dict[str, et.Element] = {}


    def expand(self) -> None:
        self.extract_macros()
        self.expand_macros(self.root)
        self.check_macro_expansion(self.root)
        et.dump(self.root)
        print()


    def extract_macros(self) -> None:
        # recursive
        for child in self.root:
            self.explore_node(child)


    def explore_node(self, node: et.Element) -> None:
        if node.tag in ['xml', 'macro']:
            macro_name = node.attrib['name']
            self.macros[macro_name] = node  # type: ignore
        
        for child in node:
            self.explore_node(child)

    
    def expand_macros(self, parent: et.Element) -> None:
        children = []
        for child in parent:
            children.append(child)  # type: ignore

        children_to_delete = []

        for child in parent:
            if child.tag == 'expand':
                # mark the expand elem for removal
                children_to_delete.append(child)  # type: ignore

                # fetch the relevant macro element
                macro = self.fetch_macro_elem(child)
                
                # handle yield injection
                self.resolve_yield_statments(macro, child)

                self.resolve_macro_tokens(macro)
                
                # append macro contents to parent
                for elem in macro:
                    parent.append(elem)
            
            # recursive (macro inside macro)
            self.expand_macros(child)

        # only deleted expanded elems at end! otherwise the child iteration can have strange behaviour
        for child in children_to_delete:  # type: ignore
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
        # gather all tokens
        local_tokens: dict[str, str] = {}

        # extract all tokens supplied in macro def
        for key, val in macro.attrib.items():
            if key.startswith('token_'):
                token = '@' + key.lstrip('token_').upper() + '@'
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

    def check_macro_expansion(self, node: et.Element):
        for child in node:
            assert(child.tag != 'expand')
            self.check_macro_expansion(child)


expander = MacroExpander()
expander.expand()







