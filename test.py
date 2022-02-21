

import sys
sys.path.append('src')

from command.components.Positional import Positional

myposit1 = Positional('hello')
myposit1.cmd_pos = 1
myposit2 = Positional('there')

print(myposit1.value_record.record, myposit1.cmd_pos)
print(myposit2.value_record.record, myposit2.cmd_pos)