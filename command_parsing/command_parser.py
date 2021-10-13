

import sys
import re 
import ast
from pypeg2 import *


"""

elements:
    - bash conditional
    - bash loop
    - cheetah conditional (make this allows nested conditionals)
    - cheetah loop
    - cheetah func
    - cheetah set
    - cheetah comment
"""

################################################
###################  regex  ####################
################################################ 

# general
TEXT = re.compile(".*", flags=re.DOTALL)
LINE = re.compile(".*")

# cheetah
CHEETAH_COMMENT = re.compile("\#\#.*")
CHEETAH_MULTILINE_COMMENT = re.compile("#/*.*/*#", flags=re.DOTALL)

# tests
out = re.findall(CHEETAH_MULTILINE_COMMENT, '#* hello *#')
print()


################################################
##################  classes  ###################
################################################ 

# basic

"""
# cheetah conditional
    # if [ logic ] ; then statements(multiline) ;
    # (OPTIONAL) elif ; then statements(multiline) ;
    # (OPTIONAL) else statements(multiline) ;
    # fi
"""

# cheetah if line

#class CheetahConditional:
#    grammar = ...



# cheetah comments ---------------
class CheetahComment:
    grammar = CHEETAH_COMMENT, endl

class CheetahMultilineComment(str):
    grammar = CHEETAH_MULTILINE_COMMENT

#out = parse('#* here\nis\nthe\nmultiline\ncomment *#', CheetahMultilineComment)
out = parse('#* here\ncomment *#', CheetahMultilineComment)
print(''.join(ast.literal_eval(out)))
print()


 
# command string -----------------
class CommandString(str):
    grammar = attr('comments', maybe_some(CHEETAH_COMMENT))


################################################
###################  tests  ####################
################################################ 


out = parse()

out = parse('##comment 1 ## asdas\n## comment 2 \n', CommandString)
for comment in out.comments:
    print(comment)
print()






def main(argv):
    filepath = argv[0]
    command_string = read_file(filepath)
    print()



def read_file(filepath):
    with open(filepath, 'r') as fp:
        return fp.read()



if __name__ == '__main__':
    main(sys.argv[1:])