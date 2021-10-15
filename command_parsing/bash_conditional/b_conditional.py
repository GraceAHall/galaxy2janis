

from lark import Lark
from lark import Transformer

with open('command_parsing/bash_conditional/b_conditional2.txt', 'r') as fp:
    text = fp.read()

with open('command_parsing/bash_conditional/b_conditional.lark', 'r') as fp:
    ruleset = fp.read()


class BConditionalTransformer(Transformer):
    def condition(self, string_list):
        return ' '.join(string_list)
    
    def instruction(self, string_list):
        return ' '.join(string_list)


#text = 'if [ "$stringvar" == "tux" ] ; then'
#text = 'if [ "$stringvar" == "tux" ] ; then'
#text = 'if [ -z "\$AUGUSTUS_CONFIG_PATH" ] ; \n then'
#text = 'if [[ -f "\$GNM2TAB_PATH" ]] ; then'

if_text = """
if [ -b there ] ; then 
    if [ -b there ] ; then 
        die ;
    fi
    die chafit;
fi
"""

elif_text = """
elif [ -b there ] ; then 
    die hitmap ;
"""

else_text = """
else
    die hitmap ;
"""

cond_text = """
if [ -b there ] ; then
    spam the chafit;
else 
    die hitmap;
fi
"""


parser = Lark(ruleset, start='if_block')
print('\n', parser.parse(if_text).pretty())
print()

parser = Lark(ruleset, start='elif_block')
print('\n', parser.parse(elif_text).pretty())
print()

parser = Lark(ruleset, start='else_block')
print('\n', parser.parse(else_text).pretty())
print()

parser = Lark(ruleset, start='conditional')
print('\n', parser.parse(cond_text).pretty())
print()


print('\n', parser.parse(text).pretty())
conditional = BConditionalTransformer().transform(tree)
print(BConditionalTransformer().transform(tree).pretty())

print()