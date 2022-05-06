


from Cheetah.Template import Template
from galaxy.util import unicodify

template_text = """
#if $min_length:
    hello
#end if
#if $not_min_length:
    there
#end if
"""

context = {
    'min_length': True,
    'not_min_length': True,
}

print(template_text)

# klass = Template.compile(source=template_text)
# t = klass(searchList=[context])


print(myvar)
myvar = str(t)
print(myvar)
print()