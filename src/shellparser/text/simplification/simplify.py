

from typing import Callable
from shellparser.text.simplification.filters import (
    flatten_multiline_strings,
    translate_variable_markers,
    standardise_variable_format,
    simplify_sh_constructs,
    simplify_galaxy_static_vars,
    simplify_galaxy_dynamic_vars,
    remove_cheetah_comments,
    replace_function_calls,
    replace_backticks,
    remove_empty_quotes,
    interpret_raw
)

from shellparser.text.simplification.aliases import resolve_aliases

# module entry points

def simplify_test(cmdstr: str) -> str:
    simplifier = TestSimplifier()
    return simplifier.simplify(cmdstr)

def simplify_xml(cmdstr: str) -> str:
    simplifier = XMLSimplifier()
    cmdstr = simplifier.simplify(cmdstr)
    cmdstr = resolve_aliases(cmdstr)
    return cmdstr

def simplify_xml_cheetah_eval(cmdstr: str) -> str:
    simplifier = PartialCheetahEvalSimplifier()
    cmdstr = simplifier.simplify(cmdstr)
    return cmdstr



# classes 

class CommandSimplifier:
    filters: list[Callable[[str], str]] = []

    def simplify(self, cmdstr: str) -> str:
        return self.map_filters(cmdstr)

    def map_filters(self, cmdstr: str) -> str:
        for filter_func in self.filters:
            cmdstr = filter_func(cmdstr)
        return cmdstr


class PartialCheetahEvalSimplifier(CommandSimplifier):
    filters: list[Callable[[str], str]] = [
        remove_cheetah_comments,
        simplify_galaxy_static_vars,
        simplify_galaxy_dynamic_vars,
    ]


class TestSimplifier(CommandSimplifier):
    filters: list[Callable[[str], str]] = [
        translate_variable_markers,
        standardise_variable_format,
        simplify_galaxy_dynamic_vars,
        simplify_sh_constructs,
        replace_backticks,
        remove_empty_quotes,
    ]


class XMLSimplifier(CommandSimplifier):
    filters: list[Callable[[str], str]] = [
        remove_cheetah_comments,
        flatten_multiline_strings,
        replace_function_calls,
        replace_backticks,
        standardise_variable_format,
        simplify_sh_constructs,
        simplify_galaxy_static_vars,
        simplify_galaxy_dynamic_vars,
        remove_empty_quotes,
        interpret_raw
    ]

