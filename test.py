
import shlex
from command.components.CommandComponent import CommandComponent


mystr = "hello, 'this is\n a crime' and I don't like it"

sh = shlex.shlex(mystr)
sh.whitespace = ' \t\n\r'
sh.whitespace_split = True
sp_text = list(sh)
print(sp_text)





from command.components.inputs import Positional, Flag, Option

def myfunc(component: CommandComponent) -> None:
    pass

myposit = Positional('', 0)
myflag = Flag('')
myopt = Option('', [], 0)

myfunc(myposit)
myfunc(myflag)
myfunc(myopt)