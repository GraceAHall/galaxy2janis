


import regex as re

def get_stdout_constructs(the_string):
    pattern = r'(?<=\s|^)(2>\&1 )?>(?=\s)|(\|&?)\stee(?=\s|$)'
    matches = re.finditer(pattern, the_string)
    return [m[0] for m in matches]


print(get_stdout_constructs("> '$report'"))
print(get_stdout_constructs("2>&1 > $file_stderr"))
print(get_stdout_constructs("'$out_result' | tee '$out_log'"))
print(get_stdout_constructs("--verbose 3 |& tee '$out_log'"))
print(get_stdout_constructs("|& tee '$out_log'"))
print(get_stdout_constructs("| tee"))
print(get_stdout_constructs("| tee1"))
print(get_stdout_constructs(" |& tee 1daasd"))
print(get_stdout_constructs(" | & tee"))




def simplify_stdio(command_string):
    command_string = command_string.replace("&amp;", "&")
    command_string = command_string.replace(">>", ">")

    command_string = command_string.replace("| tee ", "> ")
    command_string = command_string.replace("| tee\n", "> ")
    command_string = command_string.replace("|& tee ", "> ")
    command_string = command_string.replace("|& tee\n", "> ")
    command_string = command_string.replace("2>&1", "")
    command_string = command_string.replace("1>&2", "")
    command_string = command_string.replace(">&2", "")

    return command_string


cmd_string = """
  > '$report'
2>&1 > $file_stderr
'$out_result' | tee '$out_log'
--verbose 3 |& tee '$out_log'
|& tee '$out_log'
| tee
| tee1
 | & tee 1daasd
"""

print(simplify_stdio(cmd_string))

