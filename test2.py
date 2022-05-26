
from Cheetah.Template import Template


templateDef = """
<HTML>
<HEAD><TITLE>\$input.reference</TITLE></HEAD>
<BODY>
$contents
## this is a single-line Cheetah comment and won't appear in the output
#* This is a multi-line comment and won't appear in the output
   blah, blah, blah
*#
</BODY>
</HTML>"""

nameSpace = {
    'input' : {
        'reference': 'WTFFF'
    },
    'contents': 'Hello World!'
}

t = Template(templateDef, searchList=[nameSpace])
print(t)
