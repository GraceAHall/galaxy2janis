
# pyright: strict


class Prefix:
    def __init__(self, pos: int, command_list: list[str], text: str, gx_var: str):
        self.pos = pos
        self.command_list = command_list
        self.text = text
        self.gx_var = gx_var


class PrefixCollector:
    def __init__(self):
        self.prefixes: list[Prefix] = []


    def add(self, varpos: int, command_list: list[str], gx_var: str) -> None:
        # get the prefix if valid
        text = self.fetch_prefix(varpos, command_list)
        
        # create new Prefix
        new_prefix = Prefix(varpos - 1, command_list, text, gx_var)

        # check identical prefix doesn't exist
        for prefix in self.prefixes:
            if new_prefix.text == prefix.text and new_prefix.gx_var == prefix.gx_var:
                return        

        self.prefixes.append(new_prefix)


    def fetch_prefix(self, varpos: int, command_list: list[str]) -> str:
        """
        checks if the previous word looks like a valid parameter prefix
        maybe here I will ban common linux terms
        """
        if varpos != 0:
            prev_word = command_list[varpos - 1]
            if prev_word.startswith('-'):
                return prev_word
        return ''


    def user_select_prefix(self):
        assert(len(self.prefixes) > 1)

        # print basics
        print(f'var: {self.prefixes[0].gx_var}')
        print('possible prefixes:')

        # print each candidate prefix
        for i, prefix in enumerate(self.prefixes):
            print(f'{i}:\t{prefix.text}')
            print(f'command:\t{" ".join(prefix.command_list)}')
            print()
        
        selected_elem = int(input('correct prefix (num)'))
        self.prefixes = [self.prefixes[selected_elem + 1]]
