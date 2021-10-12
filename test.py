



from pypeg2 import *
import re

# patterns -----------------
pattern1 = '.+?(;|$)'

# string -------------------
the_string1 = 'hello;'
the_string2 = \
"""int f(int a, long b)
{
    do_this;
    do_that;
}"""


pattern = pattern1
the_string = the_string2
hits = [(m.start(0), m.end(0)) for m in re.finditer(pattern, the_string, flags=re.DOTALL)]
"""
for hit in hits:
    print(the_string[hit[0]:hit[1]])
    print('--------------')
"""


# an instruction
line = re.compile('.+?(;|$)')
# using lookahead to not match ';'
# lookahead not working
# line = re.compile('.+?(?=(;|$))')

class Instruction(str):
    grammar = line, optional(endl)

text = 'myvar = "hello!";\n'
f = parse(text, Instruction)

class InstructionBlock(List):
    grammar = "{", maybe_some(Instruction), "}"
    print(grammar)

text = '{do this; do_this2; do this3;}'
aaaa = parse(text, InstructionBlock)

print()


"""
myst = \
int f(int a, long b)
{
    do_this;
    do_that;
}


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
    grammar = csl(Parameter)


# INSTRUCTION BLOCK

line = re.compile(r".*[;\n]")

# defining an instruction block
class Instruction(str):
    grammar = line, ";", optional(endl)

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
f = parse("int f(int a, long b) { do_this asodj;\n do_that;\n }", Function)
#f = parse("int f(int a, long b) { do_this you hoe; do_that yeah; }", Function)




print()


"""

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