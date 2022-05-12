


from Cheetah.Template import Template

template_text = """hell this is an 
$input"""

context = {
    'input': 
}


# klass = Template.compile(source=template_text)
# t = klass(searchList=[context])

t = Template(template_text, searchList=[context])
myvar = str(t)
print(myvar)
print()