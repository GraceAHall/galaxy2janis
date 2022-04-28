


from typing import Any
#from Cheetah.NameMapper import NotFound
#from Cheeta/h.Parser import ParseError
from Cheetah.Template import Template

def sectional_template(cmdstr: str, inputs: dict[str, Any]) -> str:
    templator = SectionalCheetahTemplator(inputs)
    templator.template(cmdstr)
    raise NotImplementedError()


class SectionalCheetahTemplator:
    def __init__(self, input_dict: dict[str, Any]):
        self.input_dict = input_dict
    
    def template(self, cmdstr: str) -> str:
        text = Template(cmdstr, searchList=[nameSpace])
        print(text)
