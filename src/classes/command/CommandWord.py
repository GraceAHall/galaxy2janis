

class CommandWord:
    def __init__(self, text: str, statement_block: int):
        self.text = text
        self.statement_block = statement_block
        self.in_loop = False
        self.in_conditional = False
        self.expanded_text: list[str] = []