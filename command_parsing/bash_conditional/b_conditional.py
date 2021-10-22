

from lark import Lark
from lark import Transformer




#text = 'if [ "$stringvar" == "tux" ] ; then'
#text = 'if [ "$stringvar" == "tux" ] ; then'
#text = 'if [ -z "\$AUGUSTUS_CONFIG_PATH" ] ; \n then'
#text = 'if [[ -f "\$GNM2TAB_PATH" ]] ; then'


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

if_text1 = """
if [ -b there ] ; then 
    die chafit;
fi
"""

if_text2 = """
if [ -b there ] ; then die chafit ; fi
"""

if_text3 = """
if [ -b there ] ; then 
    if [ -b there ] ; then 
        die ;
    fi
    die chafit;
fi
"""

if_text4 = """
if [ -b there ] ; then if [ -b there ] ; then die ; fi die chafit; fi
"""

with open('command_parsing/bash_conditional/b_conditional3.txt', 'r') as fp:
    loaded_text = fp.read()

with open('command_parsing/bash_conditional/b_conditional.lark', 'r') as fp:
    ruleset = fp.read()

parser = Lark(ruleset, start='conditional')
print('before transformation')
print('\n', parser.parse(loaded_text).pretty())
tree = parser.parse(loaded_text)

class BConditionalTransformer(Transformer):
    def condition(self, string_list):
        return 'condition: ' + ' '.join(string_list)
    
    def statement(self, string_list):
        return ' '.join(string_list)

conditional = BConditionalTransformer().transform(tree)

print('\nafter transformation\n')
print(BConditionalTransformer().transform(tree).pretty())
print()
