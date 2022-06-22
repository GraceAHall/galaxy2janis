

def myfunc(tool_path: str) -> str:
    if '/' not in tool_path:
        return './'
    return tool_path.rsplit('/', 1)[0]

print(myfunc('abricate/abricate.xml'))
print(myfunc('/abricate.xml'))
print(myfunc('abricate.xml'))