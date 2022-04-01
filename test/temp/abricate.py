
# NOTE
# This is an automated translation of the 'abricate' version '1.0.1' tool from a Galaxy XML tool wrapper.  
# Translation was performed by the gxtool2janis program (in-development)


import sys
sys.path.append('/home/grace/work/pp/gxtool2janis')


from janis_core import (
    CommandToolBuilder, 
    ToolMetadata,
    ToolInput, 
    ToolOutput,
    Array,
    Optional,
    UnionType,
    Stdout
)
from janis_core.types.common_data_types import File
from janis_core.types.common_data_types import String
from janis_core.types.common_data_types import Boolean
from janis_core.types.common_data_types import Float
from data.datatypes.galaxy import Tabular


metadata = ToolMetadata(
    short_documentation="Mass screening of contigs for antimicrobial and virulence genes",
    keywords=[],
    contributors=['gxtool2janis'],
    dateCreated="2022-04-01",
    dateUpdated="2022-04-01",
    version="1.0.1",
    doi=None,
    citation="tool xml missing citation",
    documentationUrl=None,
    documentation="""
**abricate help**
 """
)

inputs = [
	# Positionals
	ToolInput(
		'sample_name',
		File,
		position=1,
		default=None,
		doc="",
	),
	# Flags
	ToolInput(
		'noheader',
		Boolean(optional=True),
		prefix='--noheader',
		position=2,
		default=False,
		doc="Suppress header Suppress output file's column headings. possible values: --noheader",
	),
	# Options
	ToolInput(
		'minid',
		Float(optional=True),
		prefix='--minid=',
		separate_value_from_prefix=False,
		position=2,
		default=80,
		doc="Minimum DNA %identity",
	),
	ToolInput(
		'mincov',
		Float(optional=True),
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
    version="1.0.1",
    metadata=metadata,
    container="quay.io/biocontainers/abricate:1.0.1--h1341992_0",
    base_command=['abricate'],
    inputs=inputs,
    outputs=outputs
)


if __name__ == "__main__":
    abricate().translate(
        "wdl", to_console=True
    )

