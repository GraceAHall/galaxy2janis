



from xmltool.param.InputParam import (
    BoolParam,
    FloatParam,
    SelectOption,
    SelectParam
)
from xmltool.param.OutputParam import OutputParam
from command.components.outputs.Selector import Selector, SelectorType

MOCK_BOOLPARAM1 = BoolParam('adv.no_header')
MOCK_BOOLPARAM1.argument = '--noheader'
MOCK_BOOLPARAM1.checked = False
MOCK_BOOLPARAM1.datatypes = ['Boolean']
MOCK_BOOLPARAM1.truevalue = '--noheader'
MOCK_BOOLPARAM1.falsevalue = ''
MOCK_BOOLPARAM1.helptext = "Suppress output file's column headings"
MOCK_BOOLPARAM1.label = 'Suppress header'
MOCK_BOOLPARAM1.optional = False

MOCK_FLOATPARAM1 = FloatParam('adv.min_dna_id')
MOCK_FLOATPARAM1.argument = '--minid'
MOCK_FLOATPARAM1.datatypes = ['Float']
MOCK_FLOATPARAM1.helptext = ''
MOCK_FLOATPARAM1.label = 'Minimum DNA %identity'
MOCK_FLOATPARAM1.optional = True
MOCK_FLOATPARAM1.value = '80'
MOCK_FLOATPARAM1.min = '0.0'
MOCK_FLOATPARAM1.max = '100.0'

MOCK_FLOATPARAM2 = FloatParam('adv.min_cov')
MOCK_FLOATPARAM2.argument = '--mincov'
MOCK_FLOATPARAM2.datatypes = ['Float']
MOCK_FLOATPARAM2.helptext = ''
MOCK_FLOATPARAM2.label = 'Minimum DNA %coverage'
MOCK_FLOATPARAM2.optional = True
MOCK_FLOATPARAM2.value = '80'
MOCK_FLOATPARAM2.min = '0.0'
MOCK_FLOATPARAM2.max = '100.0'

MOCK_SELECTPARAM1 = SelectParam('adv.db')
MOCK_SELECTPARAM1.argument = '--db'
MOCK_SELECTPARAM1.datatypes = ['String']
MOCK_SELECTPARAM1.helptext = 'Option to switch to other AMR/other database'
MOCK_SELECTPARAM1.label = "Database to use - default is 'resfinder'"
MOCK_SELECTPARAM1.optional = False
MOCK_SELECTPARAM1.multiple = False
MOCK_SELECTPARAM1.options = [
    SelectOption('argannot', False, 'ARG-ANNOT'),
    SelectOption('card', False, 'CARD'),
    SelectOption('ecoh', False, 'EcOH'),
    SelectOption('ncbi', False, 'NCBI Bacterial Antimicrobial Resistance Reference Gene Database'),
    SelectOption('resfinder', True, 'Resfinder'),
    SelectOption('plasmidfinder', False, 'PlasmidFinder'),
    SelectOption('vfdb', False, 'VFDB'),
    SelectOption('megares', False, 'megares'),
    SelectOption('ecoli_vf', False, 'Ecoli_VF')
]

MOCK_OUTPARAM1 = OutputParam('report')
MOCK_OUTPARAM1.datatypes = ['tabular'] 
MOCK_OUTPARAM1.label = 'report file'
MOCK_OUTPARAM1.selector = Selector(
    SelectorType.INPUT_SELECTOR, 
    contents='report'
)

