



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
        return arg[0]

    def string(self, n):
        return str(n[0])

    def integer(self, n):
        return int(n[0])

    def number(self, n):
        return float(n[0])

    plist = list
    parameter = list


parameters_parser = Lark(ruleset, start='plist')
tree = parameters_parser.parse(text)
parameters = ParameterTransformer().transform(tree)
print(parameters)
print()



