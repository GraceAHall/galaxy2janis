


from tool.Tool import Tool


def write_definition(path: str, tool: Tool) -> None:
    janis_definition = tool.to_janis_definition()
    with open(path, 'w') as fp:
        fp.write(janis_definition)
