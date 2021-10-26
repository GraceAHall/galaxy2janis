
from lark import Lark
from lark.indenter import Indenter
from lark import Transformer


with open('command_parsing/cheetah_conditional/ch_conditional3.txt', 'r') as fp:
    text = fp.read()

with open('command_parsing/cheetah_conditional/ch_conditional.lark', 'r') as fp:
    ruleset = fp.read()


# class TreeIndenter(Indenter):
#     NL_type = '_NL'
#     OPEN_PAREN_types = []
#     CLOSE_PAREN_types = []
#     INDENT_type = '_INDENT'
#     DEDENT_type = '_DEDENT'
#     tab_len = 4


class ConditionalTransformer(Transformer):
    def statement(self, entities):
        return 'STATEMENT ' + ' '.join(entities)


    def comment(self, entities):
        return 'COMMENT ' + ' '.join(entities)
        
        # return ' '.join([ent[1] for ent in entities])


# parser = Lark(ruleset, postlex=TreeIndenter())
parser = Lark(ruleset, start='conditional')

def test():
    tree = parser.parse(text)
    parameters = ConditionalTransformer().transform(tree)
    print(parameters.pretty())


if __name__ == '__main__':
    test()


