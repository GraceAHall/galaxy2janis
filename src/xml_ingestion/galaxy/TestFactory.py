



from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Optional

from logger.errors import AttributeNotSupportedError
from galaxy.tool_util.verify.interactor import ToolTestDescription
from janis_core.tool.test_classes import (
    TTestCase,
    TTestExpectedOutput,
    TTestPreprocessor
)

"""
for each galaxy test, need to translate into a janis TTestCase. 
inputs are easy, but outputs are more complex. 
for each output, need to specify the TTestExpectedOutput.
this TTestExpectedOutput has a TTestPreprocessor, which obtains the value of the
"""



def unsupported_strategy(gxout: ToolTestDescription) -> TTestExpectedOutput:
    raise AttributeNotSupportedError()

def has_size_strategy(gxout: ToolTestDescription) -> TTestExpectedOutput:
    pass
    # return TTestExpectedOutput(
    #     gxout.name,
    #     TTestPreprocessor.FileSize
    #     ...
    # )



strategy_map: dict[str, Callable[..., TTestExpectedOutput]] = {
    'lines_diff': has_size_strategy,
    'ftype': has_size_strategy,
    'has_size': has_size_strategy,
    'has_text': has_size_strategy,
    'not_has_text': has_size_strategy,
    'has_text_matching': has_size_strategy,
    'has_line': has_size_strategy,
    'has_line_matching': has_size_strategy,
    'has_n_lines': has_size_strategy,
    'has_n_columns': has_size_strategy,

    're_match': unsupported_strategy,
    're_match_multiline': unsupported_strategy,

    'has_archive_member': unsupported_strategy,
    'is_valid_xml': unsupported_strategy,
    'xml_element': unsupported_strategy,
    'has_element_with_path': unsupported_strategy,
    'has_n_elements_with_path': unsupported_strategy,
    'element_text_matches': unsupported_strategy,
    'element_text_is': unsupported_strategy,
    'attribute_matches': unsupported_strategy,
    'attribute_is': unsupported_strategy,
    'element_text': unsupported_strategy,
    'has_h5_keys': unsupported_strategy,
    'has_h5_attribute': unsupported_strategy
}



@dataclass
class ValidCheck:
    name: str
    value: Any


class TestFactory:
    def produce(self, gxtest: ToolTestDescription) -> TTestCase:
        return TTestCase(
            gxtest.name,
            self.prepare_inputs(gxtest),
            self.prepare_outputs(gxtest)
        )

    def prepare_inputs(self, gxtest: ToolTestDescription) -> dict[str, Any]:
        pass
        
    def prepare_outputs(self, gxtest: ToolTestDescription) -> list[TTestExpectedOutput]:
        for gxout in gxtest.outputs:
            checks = self.gather_checks(gxout)
            print()

    # TODO here
    def gather_checks(self, gxout: dict[str, Any]) -> list[ValidCheck]:
        checks: list[ValidCheck] = []
        
        # file diff
        if gxout['value']:
            checks.append(ValidCheck('lines_diff', gxout['attributes']['lines_diff']))

        match gxout['attributes']['compare']:
            case 'diff':
                pass
            case 're_match' | 're_match_multiline':
                pass
            case 'sim_size':
                pass
            case 'contains':
                pass
            case _:
                pass
        
        # file fingerprint
        for attname, attval in gxout['attributes'].items():
            if attname in ['ftype', 'md5', 'checksum'] and attval:
                checks.append(ValidCheck(attname, attval))

        # file contents
        if gxout['attributes']['assert_list']:
            for assertcheck in gxout['attributes']['assert_list']:
                checks.append(
                    ValidCheck(
                        assertcheck['tag'], assertcheck['attributes']
                    )
                )

        return checks


        





            





    #     # get the right map object 
    #     ttestouts = []
    #     for out in gxtest.outputs:
    #         ttestouts += self.init_file_diff_outputs(out)
    #         ttestouts += self.init_file_check_outputs(out)
    #     return ttestouts

    # def init_file_diff_outputs(self, gx_test_out: dict[str, Any]) -> list[TTestExpectedOutput]:
    #     outs = []
    #     if gx_test_out['value']:
    #         self.init_diff_outputs(gx_test_out)
    #     return outs

    # def init_file_check_outputs(self, gx_test_out: dict[str, Any]) -> list[TTestExpectedOutput]:
    #     outs = []
    #     outs += self.init_fingerprint_outputs(gx_test_out)
    #     outs += self.init_rematch_outputs(gx_test_out)
    #     outs += self.init_simsize_outputs(gx_test_out)
    #     outs += self.init_assert_outputs(gx_test_out)
    #     return outs

    # def init_fingerprint_outputs(self, gx_test_out: dict[str, Any]) -> list[TTestExpectedOutput]:
    #     pass

    # def init_fingerprint_outputs(self, gx_test_out: dict[str, Any]) -> list[TTestExpectedOutput]:
    #     if gx_test_out['attributes']['compare'] in ['re_match', 're_match_multiline']:
    #         raise AttributeNotSupportedError('re_match and re_match_multiline output checks not supported')

    # def init_simsize_outputs(self, gx_test_out: dict[str, Any]) -> list[TTestExpectedOutput]:
    #     outchecks = ['']
    #     outs = []
    #     for check in outchecks:
    #         outs += strategy_map[check](gx_test_out)
    #     return outs

    # def init_assert_outputs(self, gx_test_out: dict[str, Any]) -> list[TTestExpectedOutput]:
    #      if gx_test_out['attributes']['assert_list']:
    #         for out_check in gx_test_out['attributes']['assert_list']:
    #             self.map_assert_output()





"""
COMPARE FILE NEEDED -> may need decompression if decompress="true"
compare="diff":
- lines_diff
- ftype

compare="sim_size":
do filesize check with the following info
- delta
maximum allowed absolute size difference (in bytes) between the data set that is generated in the test and the file in test-data/ that is referenced by the file attribute. Default value is 10000 bytes. Can be combined with delta_frac.
- delta_frac
If compare is set to sim_size, this is the maximum allowed relative size difference between the data set that is generated in the test and the file in test-data/ that is referenced by the file attribute. A value of 0.1 means that the file that is generated in the test can differ by at most 10% of the file in test-data. The default is not to check for relative size difference. Can be combined with delta.


FILE NOT NEEDED
md5
checksum
assert_list has elems



"""





    # def init_output(self):
    #     pass
    #     for output in gxtest.outputs:
    #         self.
    #     if gxtest.outputs
    #     #preprocessor_map = self.
    #     compare_method = gxtest.output_data['compare']
    #     return TTestExpectedOutput(
    #         gxtest.name,
    #         preprocessor_map[compare_method],
    #     )
        
        



