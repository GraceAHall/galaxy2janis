




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

    def format_name(self, name: str) -> str:
        """
        to satisfy janis tag requirements
        to avoid janis reserved keywords
        """
        name = name.lower()
        name = name.strip('\\/')
        name = name.replace('-', '_')
        name = name.replace('/', '_')
        name = name.replace('\\', '_')
        if name in self.prohibited_keys or len(name) == 1:
            name += '_janis'
        return name
    
    def format_prefix(self, prefix: str) -> str:
        name = prefix.strip('-')
        return self.format_name(name)



        