

from typing import Callable

from command.simplify.filters import (
    flatten_multiline_strings,
    translate_variable_markers,
    standardise_variable_format,
    simplify_sh_constructs,
    simplify_galaxy_static_vars,
    simplify_galaxy_dynamic_vars,
    remove_cheetah_comments,
    replace_backticks,
    interpret_raw
)


class CommandSimplifier:
    filters: list[Callable[[str], str]] = []

    def simplify(self, cmdstr: str) -> str:
        return self.map_filters(cmdstr)

    def map_filters(self, cmdstr: str) -> str:
        for filter_func in self.filters:
            cmdstr = filter_func(cmdstr)
        print(cmdstr)
        return cmdstr


class TestCommandSimplifier(CommandSimplifier):
    filters: list[Callable[[str], str]] = [
        translate_variable_markers,
        standardise_variable_format,
        simplify_galaxy_dynamic_vars,
        simplify_sh_constructs,
        replace_backticks,
        interpret_raw
    ]


class XMLCommandSimplifier(CommandSimplifier):
    filters: list[Callable[[str], str]] = [
        flatten_multiline_strings,
        standardise_variable_format,
        simplify_sh_constructs,
        simplify_galaxy_static_vars,
        simplify_galaxy_dynamic_vars,
        remove_cheetah_comments,
        replace_backticks,
        interpret_raw
    ]

