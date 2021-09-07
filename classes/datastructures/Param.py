
# pyright: strict

# Optional[str] means the type can be str or None. 

class Param:
    def __init__(self):
        self.name: str = ""
        self.local_path: list[str] = []
        self.type: str = ""
        self.default_value: str = ""
        self.prefix: str = ""
        self.help_text: str = ""
        self.is_optional: bool = False
        self.is_argument: bool = False
        self.is_ui_param: bool = False      


    def get_local_path(self) -> str:
        local_path = '.'.join(self.local_path)
        if local_path == '':
            return self.name
        else:
            return local_path + f'.{self.name}'


    def __str__(self):
        out_str = ''
        out_str += '\nclass: param\n'
        out_str += f'name: {self.name}\n'
        out_str += f'local_path: {self.local_path}\n'
        out_str += f'type: {self.type}\n'
        out_str += f'prefix: {self.prefix}\n'
        out_str += f'default: {self.default_value}\n'
        out_str += f'help_text: {self.help_text}\n'
        out_str += f'is_optional: {self.is_optional}\n'
        out_str += f'is_argument: {self.is_argument}\n'
        out_str += f'is_ui_param: {self.is_ui_param}\n'
        return out_str