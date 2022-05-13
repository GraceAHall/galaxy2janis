



from typing import Any
from galaxy_interaction import GalaxyManager
from startup.ExeSettings import ToolExeSettings

from xmltool.param.InputParam import BoolParam

from xmltool.load import load_xmltool
from xmltool.tool_definition import XMLToolDefinition


def resolve_values(esettings: ToolExeSettings, gxstep: dict[str, Any]) -> dict[str, Any]:
    manager = GalaxyManager(esettings)
    xmltool = load_xmltool(manager)
    resolver = StepValueResolver(gxstep, xmltool)
    return resolver.resolve()



class StepValueResolver:
    def __init__(self, gxstep: dict[str, Any], xmltool: XMLToolDefinition):
        self.gxstep = gxstep
        self.xmltool = xmltool
        self.tool_state: dict[str, Any] = {}

    def resolve(self) -> dict[str, Any]:
        for key, val in self.gxstep['tool_state'].items(): 
            self.tool_state[key] = self.resolve_value(key, val)
        return self.tool_state
    
    def resolve_value(self, gxvarname: str, val: Any) -> Any:
        param = self.xmltool.get_input(gxvarname)
        match param:
            case BoolParam():
                if val == 'false':
                    return param.falsevalue
                else:
                    return param.truevalue
            case _:
                return val



