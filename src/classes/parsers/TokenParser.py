




from xml.etree import ElementTree as et

from classes.Logger import Logger


class TokenParser:
    def __init__(self, tree: et.ElementTree, existing_tokens: dict[str, str], logger: Logger):
        self.tree = tree
        self.tokens = existing_tokens
        self.logger = logger 


    def parse(self):
        root = self.tree.getroot()
        self.gather_tokens(root)
        self.apply_tokens(root)


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