
import sys
sys.path.append('/home/grace/work/pp/gxtool2janis')

from janis_core import (
    CommandToolBuilder, 
    ToolInput, 
    ToolOutput,
    Array,
    Optional,
    UnionType,
    Stdout
)
from janis_core.types.common_data_types import Float
from datatypes.galaxy import Tabular
from janis_core.types.common_data_types import File
from janis_core.types.common_data_types import Boolean
from janis_core.types.common_data_types import String
from janis_core import InputSelector

inputs = [
	# Positionals
	ToolInput(
		'sample_name',
		File,
		position=1,
		doc="examples: $sample_name, report",
	),
	# Flags
	ToolInput(
		'noheader',
		Boolean(optional=True),
		prefix='--noheader',
		position=2,
		doc="Suppress header Suppress output file's column headings. possible values: --noheader",
	),
	# Options
	ToolInput(
		'minid',
		Float,
		prefix='--minid=',
		separate_value_from_prefix=False,
		position=2,
		default=80,
		doc="Minimum DNA %identity",
	),
	ToolInput(
		'mincov',
		Float,
		prefix='--mincov=',
		separate_value_from_prefix=False,
		position=2,
		default=80,
		doc="Minimum DNA %coverage",
	),
	ToolInput(
		'db',
		String,
		prefix='--db=',
		separate_value_from_prefix=False,
		position=2,
		default="resfinder",
		doc="Database to use - default is 'resfinder' Option to switch to other AMR/other database. possible values: argannot, card, ecoh, ecoli_vf, megares",
	),
]

outputs = [
	ToolOutput(
		'report',
		Stdout(Tabular),
		doc="report file",
	),
]

abricate = CommandToolBuilder(
    tool="abricate",
    base_command=['abricate'],
    inputs=inputs,
    outputs=outputs,
    container="quay.io/biocontainers/abricate:1.0.1--h1341992_0",
    version="1.0.1",
    doc="""
**abricate help**
 """
)

if __name__ == "__main__":
    abricate().translate(
        "wdl", to_console=True
    )

