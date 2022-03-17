
import shlex


mystr = "hello, 'this is\n a crime' and I don't like it"

sh = shlex.shlex(mystr)
sh.whitespace = ' \t\n\r'
sh.whitespace_split = True
sp_text = list(sh)
print(sp_text)

