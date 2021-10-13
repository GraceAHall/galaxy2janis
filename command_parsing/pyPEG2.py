



from pypeg2 import *
import re


OPERATOR = re.compile("\+|\-|\*|\/|\=\=")
SYMBOL = re.compile("\w+")
LITERAL = re.compile('\d*\.\d*|\d+|".*?"|\'.*?\'')
COMMENT = [re.compile("##.*"), re.compile("#\*.*?\*#", re.DOTALL)] # does this work? 


class Expression:
    grammar = [LITERAL, OPERATOR, SYMBOL]

class ExpressionList:
    grammar = Expression, maybe_some(",", Expression)

class FunctionCall:
    grammar = SYMBOL, "(", ExpressionList, ")"

class Operation:
    grammar = SYMBOL, OPERATOR, [LITERAL, FunctionCall]

class ReturnStatement:
    grammar = Keyword("return"), Expression

class IfStatement:
    grammar = (Keyword("if"), "(", Expression, ")", Block, Keyword("else"), Block)

class Statement:
    grammar = [IfStatement, ReturnStatement], ";"

class Block:
    grammar = "{", some(Statement), "}"

class ParameterList:
    grammar = "(", SYMBOL, maybe_some(",", SYMBOL), ")"

class Function:
    grammar = Keyword("function"), SYMBOL, ParameterList, Block

class TestLanguage:
    grammar = Function


with open('command_parsing/data/test2.txt', 'r') as fp:
    command_str = fp.read()


print()

#FLAG = re.compile("(?<=^)--.*?(?=($|\s))")
#TEST = re.compile("(?<=foo)bar(?=bar)")
#print(re.findall(TEST, 'foobarbarfoo'))

"""
Flags have whitespace, then a string starting with '--' till another whitespace. 
may be followed by a word  
"""
#FLAG = re.compile("(?<!\S)-+.*?(?=\s)")
#FLAG_NAME = re.compile("(?<!\S)|(?<=^)-{1,2}(\w+-)*\w+(?=[\s=:])")
FLAG_NAME = re.compile("((?<=^)|(?<=\s))-{1,2}(\w+-)*\w+")
print(re.search(FLAG_NAME, ' --hello '))
print(re.search(FLAG_NAME, ' --hello:there'))
print(re.search(FLAG_NAME, '\n --hello\n'))

FLAG_SEP = re.compile("\s+|:|=")

FLAG_ARG = re.compile("(\s+|=|:)\S+\s*")
print(re.search(FLAG_ARG, '--hello \nthere'))
print(re.search(FLAG_ARG, '--hello=there'))
print(re.search(FLAG_ARG, '--hello:there'))
print(re.search(FLAG_ARG, '"--cpu \${GALAXY_SLOTS:-4}"'))
print()

WORD = re.compile("\S+")
# print(re.search(WORD, 'input'))
# print(re.search(WORD, '${input}'))
# print(re.search(WORD, "'${input}'"))
# print()



class Flag(str):
    grammar = attr('flag', FLAG_NAME), optional(attr('arg', WORD)), endl
    print()

out = parse('--cpu \${GALAXY_SLOTS:-4}', Flag)
print(out.flag)
print(out.arg)

out = parse("--update-data", Flag)
print(out.flag)
if hasattr(out, 'arg'):
   print(out.arg)
   print('---')
print()

class Flags(List):
    grammar = some(Flag)

with open('command_parsing/data/test.txt', 'r') as fp:
    command_str = fp.read()

out = parse(command_str, Flags)

for flag in out:
    print(flag.flag, flag.arg)

print(out.flag)
print(out.arg)
print()

# lists - how to do in grammar def?
NUMBER = re.compile("\d+")
LETTERS = re.compile("[a-zA-Z]")

print(parse('23', [NUMBER, LETTERS])) # ok

class LettersOrNumber(List):
    grammar = [(Symbol, ':', Symbol), Symbol]

print(parse('a', LettersOrNumber))
print(parse('b:c', LettersOrNumber))
#print(parse('b:c:d', LettersOrNumber))
print()

class Key(str):
    grammar = name(), '=', attr('value', LettersOrNumber), endl # not ok

k = parse("name=1", Key)
print(k.value)
k = parse("name=hello\n", Key)
print(k.value)
print()


# Symbols and tuple grammar def
class Key:
    grammar = name(), "=", attr('value', Symbol), endl

k = Key()
k.name = Symbol("give me")
k.value = Symbol('a value')
print(compose(k))

the_key = parse("this    = something", Key)
print(the_key.name)
print(the_key.value)

print()




def main():
    pass
    #workspace()
    #online_example()
    


def workspace():
    the_string2 = \
    """{
        do this;
        do_that;
    }"""


    # an instruction
    # using lookahead to not match ';'
    # lookahead not working
    # line = re.compile('.+?(?=(;|$))')

    class Instruction(str):
        grammar = LINE, ';', optional(endl)

    text = 'myvar = hello!;\n'
    f = parse(text, Instruction)

    class InstructionBlock(List):
        grammar = "{", maybe_some(Instruction), "}"
        print(grammar)

    text = '{\ndo this;\n do_this2;\n do this3;\n}'
    aaaa = parse(the_string2, InstructionBlock)
    print()


def online_example():
    the_string = \
    """int f(int a, long b)
    {
        do this;
        do_that;
    }"""

    # pyPEG is like regex with recursion
    #K is abbreviation for 'Keyword' class

    class Type(Keyword):
        grammar = Enum( K("int"), K("long") )

    # each parameter has a Type (our class) and a name (pyPEG class)
    # we are just setting the Type to an attribute called 'typing' on the Parameter class
    # name() is just a shortcut for attr("name", Symbol)
    class Parameter:
        grammar = attr("typing", Type), name()

    # Parameters has to be a collection. Namespace is a premade collection we can use 
    # maybe_some() turns it into a comma separated list. represents '*' cardinality
    # both grammar defs are the same below.
    # optional() represents the '?' cardinality
    class Parameters(Namespace):
        #grammar = Parameter, maybe_some(",", Parameter)
        grammar = optional(csl(Parameter))

    # INSTRUCTION BLOCK
    line = re.compile(".*?(?=[;\n])")


    # defining an instruction block
    class Instruction(str):
        grammar = line, ';', optional(endl)

    block = "{", maybe_some(Instruction), "}"

    # pyPEG has indentation system to handle indentation
    # can improve our parser above's abilities using this system. 


    # FUNCTION CLASS

    # each function has a return Type, a name (premade class 'name' from pyPEG we can use)
    # the parameters will be inside parenthesis.
    # functions consist of an instruction block that can be multiline, so we can make Function() a list
    # this puts the type, name, and parameters into that list.
    # need to set them as attributes to avoid this behaviour
    # finally the instruction block sits between curly braces. we don't store this as an attribute. 

    class Function(List):
        grammar =   attr('typing', Type), \
                    name(), \
                    "(", attr("parms", Parameters), ")", \
                    block

    # parse the function def as a Function()! 
    f = parse(the_string, Function)
    #f = parse("int f(int a, long b) { do_this you hoe; do_that yeah; }", Function)

    print()

if __name__ == '__main__':
    main()




"""


shlex --------------------------------------------------

import shlex

#the_string = "\tif [ 'something' ] \nthen \n #im just a comment \n don't_do_this \t\nfi\n fi "

with open('test.txt', 'r') as fp:
    the_string = fp.read()

out = shlex.split(the_string)
for line in out:
    print(line)


lexer = shlex.shlex(the_string)
lexer.wordchars += '.#-[];$\/&*=:\'\"`\{\}'
lexer.whitespace = ' \t\r\n'
#lexer.whitespace_split = True
lexer.commenters = ['##']

for token in lexer:
    print(token)

print()




regex --------------------------------------------------


import re


#the_string = ' if [ ____ ] \nthen \n    ____ \nfi '
the_string = '\tif [ ____ ] \nthen \n    ____ \t\nfi\n fi '

print(len(the_string))
pattern = '\sif\s.*?(?=\sfi\s)'
hits = [(m.start(0), m.end(0)) for m in re.finditer(pattern, the_string, flags=re.DOTALL)]

print(hits)

"""