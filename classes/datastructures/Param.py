
# pyright: strict

# Optional[str] means the type can be str or None. 

from classes.PrefixCollector import PrefixCollector


class Param:
    def __init__(self, tree_path: list[str]):
        self.name: str = ""
        self.tree_path = tree_path
        self.gx_var: str = ""
        self.type: str = ""
        self.default_value: str = ""
        self.options: list[str] = []
        self.prefix_collector = PrefixCollector()
        self.prefix: str = ""
        self.help_text: str = ""
        self.is_optional: bool = False
        self.is_argument: bool = False   
        self.is_array: bool = False  
        self.is_ui_param: bool = False  
        self.appears_in_conditional: bool = False
        self.located_in_command: bool = False


    def get_tree_path(self) -> str:
        tree_path = '.'.join(self.tree_path)
        if tree_path == '':
            return self.name
        else:
            return tree_path + f'.{self.name}'


    def resolve_multiple_prefixes(self) -> None:
        if len(self.prefix_collector.prefixes) > 1:
            self.prefix_collector.user_select_prefix()
            

    def set_prefix_from_collector(self) -> None:
        assert(len(self.prefix_collector.prefixes) in [0, 1])

        if len(self.prefix_collector.prefixes) == 1:
            if self.prefix != '':  # no idea if this would happen 
                raise Exception('prefix is set but trying to set from PrefixCollector')
            else:
                self.prefix = self.prefix_collector.prefixes[0].text
          

    def __str__(self):
        out_str = ''
        out_str += '\nparam --------------\n'
        out_str += f'variable name: {self.gx_var}\n'
        out_str += f'type: {self.type}\n'
        out_str += f'prefix: {self.prefix}\n'
        out_str += f'default: {self.default_value}\n'
        out_str += f'help_text: {self.help_text}\n'
        out_str += f'is_optional: {self.is_optional}\n'
        out_str += f'is_argument: {self.is_argument}\n'
        out_str += f'is_array: {self.is_array}\n'
        out_str += f'is_ui_param: {self.is_ui_param}\n'
        out_str += f'appears_in_conditional: {self.appears_in_conditional}\n'
        out_str += f'located_in_command: {self.located_in_command}\n'
        return out_str