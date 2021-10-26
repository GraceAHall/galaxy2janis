



from lark import Lark
from lark import Transformer

with open('command_parsing/parameters/parameters.txt', 'r') as fp:
    text = fp.read()

with open('command_parsing/parameters/parameters.lark', 'r') as fp:
    ruleset = fp.read()

# class Parameter:
#     def __init__(self, flag, arg):
#         pass


class ParameterTransformer(Transformer):
    def pname(self, name):
        return str(name[0])

    def parg(self, arg):
        return str(arg[0])

    def string(self, n):
        return None

    def item(self, the_item):
        if the_item[0] != None:
            return the_item

    parameter = list

parameters_parser = Lark(ruleset, start='text')
tree = parameters_parser.parse(text)
parameters = ParameterTransformer().transform(tree)


print()

for child in parameters.children:
    if child != None:
        print(child)




