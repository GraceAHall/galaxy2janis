

from xml.etree import ElementTree as et

# parse macros
macros_xml = et.parse('tools/fastp/macros.xml')
macros_root = macros_xml.getroot()
macros = macros_root.findall('xml')

macro_list = []
for macro in macros:
    macro_list.append(macro)

print()

# need to handle <expand macro='name'> tags as a preprocessing step:
# - load macros from macros.xml
# - expand any macros in macros.xml
# - load macros from expanded macros.xml
# - iterate through every element in tool.xml
# - expand any <expand macro> tag

# none of the above requires writing. Should be able to inject a new element as a child of current element in memory 



# parse tool inputs
tool_xml = et.parse('tools/fastp/fastp.xml')
tool_root = tool_xml.getroot()

command = tool_root.find('command')

for node in tool_root.iter():
    if node.tag == 'param':
        print(node.get('name'))
        for child in node:
            print()