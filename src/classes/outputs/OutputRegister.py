


from typing import Optional, Tuple
from xml.etree import ElementTree as et
from classes.deprecated.Outputs import Output


from galaxy.tool_util.parser.output_objects import ToolOutput
from copy import deepcopy


#from classes.outputs.Outputs import Output, WorkdirOutput


class OutputRegister:
    def __init__(self, outputs: dict) -> None:
        self.outputs: dict[str, str] = {}
        self.add_from_dict(outputs)


    def add_from_dict(self, incoming: dict) -> None:
        self.outputs = self.outputs | incoming


    # def add_from_dict(self, outputs: dict, levels: list[str]) -> None:
    #     for label, obj in outputs.items():
    #         if hasattr(obj, 'outputs'):
    #             next_levels = deepcopy(levels)
    #             next_levels.append(obj.name)
    #             self.add_from_dict(obj.outputs, next_levels)
    #         else:
    #             if len(levels) == 0:
    #                 key = label
    #             else:
    #                 key = '.'.join(levels) + '.' + label
    #             if key not in self.outputs:
    #                 self.outputs[key] = obj


    def get_outputs(self) -> list[ToolOutput]:
        return list(self.outputs.values())


    def get(self, query_key: str, allow_lca=False) -> Tuple[Optional[str], Optional[ToolOutput]]:
        # quick check if the full key is present
        if query_key in self.outputs:
            return (query_key, self.outputs[query_key])

        # otherwise, get the param with best match (LCA)
        if allow_lca:
            return self.get_lca(query_key)

        return (None, None)


    def get_lca(self, query_key: str) -> Tuple[Optional[str], Optional[ToolOutput]]:
        """
        see classes.params.ParamRegister.get_lca() for explanation
        """
        query_path = query_key.split('.')
        out_scores: list[Tuple[int, str, ToolOutput]] = []

        for output_var, output in self.outputs.items():
            var_path = output_var.split('.')
            score = 0
            for i in range(1, len(query_path) + 1):
                if var_path[-i] == query_path[-i]:
                    score += 1
                else:
                    break
            out_scores.append((score, output_var, output))
        out_scores.sort(key=lambda x: x[0], reverse=True)

        if out_scores[0][0] >= 1:
            return out_scores[0][1,2]
        return (None, None)


    def get_by_filepath(self, filepath: str, allow_nopath: bool=False, allow_anywhere: bool=False) -> Tuple[Optional[str], Optional[ToolOutput]]:
        # try to match the whole path
        for output_var, output in self.outputs.items():
            if hasattr(output, 'from_work_dir'):
                if output.from_work_dir == filepath:
                    return (output_var, output)
        
        # # no success, try to match the end of the path
        # if allow_nopath:
        #     for output_var, output in self.outputs.items():
        #         if output.selector_contents.endswith(filepath):
        #             return (output_var, output)

        # # again no success, try to match the filepath anywhere in the selector contents
        # if allow_anywhere:
        #     for output_var, output in self.outputs.items():
        #         if filepath in output.selector_contents:
        #             return (output_var, output)

        return (None, None)


    def create_output_from_text(self, text: str) -> None:
        """
        creates a new output using a dummy et.Element
        the new et.Element node is populated with some default details
        then is parsed as normal created the new output. 
        the output is added to our collection of outputs. 
        """
        # TODO 
        raise Exception('TODO: make galaxy ToolOutput not old Output')
        # create dummy node
        name = text.split('.', 1)[0]
        dummy_node = et.Element('data', attrib={'name': name, 'format': 'file', 'from_work_dir': text})
        
        # create and parse output
        new_output = ToolOutput(dummy_node)
        new_output.parse()

        # add to collection
        self.add([new_output])




