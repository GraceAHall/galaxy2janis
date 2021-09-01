

import sys 


# load required janis modules on the fly. EG:
# if "something":
#     from janis_core import InputSelector

from janis_core import (
    CommandToolBuilder,
    ToolInput,
    ToolOutput
)

from classes.XMLToolReader import XMLToolReader


def main(argv):
    tool_dir = argv[0]
    tool_xml = argv[1]
    xml_reader = XMLToolReader(tool_dir, tool_xml)
    xml_reader.expand_macros()



if __name__ == '__main__':
    main(sys.argv[1:])



# expanding macros




# inputs

# load inputs from xml
# xml_inputs = read_inputs()

# tool_inputs = []

# for inp in xml_inputs:
#     new_input = ToolInput(
#         inp.name,
#         inp.type,
#         position = inp.position,
#         prefix = inp.prefix,
#         separate_value_from_prefix = inp.is_prefix_separated,
#         prefix_applies_to_all_elements = inp.is_array,
#         shell_quote = inp.should_quote,
#         separator = inp.separator,
#         localise_file = inp.should_localise,
#         default = inp.default,
#         doc = inp.help,
#     )



