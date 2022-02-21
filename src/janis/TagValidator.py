




class TagValidator:
    def __init__(self):
        self.prohibited_keys = {
            "identifier",
            "tool",
            "scatter",
            "ignore_missing",
            "output",
            "input",
            "inputs"
        }

    def format_tool_name(self, name: str) -> str:
        return name.replace('-', '_').lower()


        