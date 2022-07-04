


from typing import Tuple

from shellparser.components.inputs.Flag import Flag
from shellparser.components.inputs.Option import Option
from shellparser.components.inputs.Positional import Positional

import tags


def order_positionals(positionals: list[Positional]) -> list[Positional]:
    positionals.sort(key=lambda x: x.cmd_pos)
    return positionals

def order_flags(flags: list[Flag]) -> list[Flag]:
    flags.sort(key=lambda x: tags.tool.get(x.uuid))
    return flags

def order_options(options: list[Option]) -> list[Option]:
    options.sort(key=lambda x: tags.tool.get(x.uuid))
    return options

def order_imports(imports: list[Tuple[str, str]]) -> list[Tuple[str, str]]:
    imports = _order_imports_alphabetical(imports)
    imports = _order_imports_length(imports)
    return imports

def _order_imports_length(imports: list[Tuple[str, str]]) -> list[Tuple[str, str]]:
    imports.sort(key=lambda x: len(x[0] + x[1]), reverse=True)
    return imports

def _order_imports_alphabetical(imports: list[Tuple[str, str]]) -> list[Tuple[str, str]]:
    imports.sort(key=lambda x: f'from {x[0]} import {x[1]}')
    return imports