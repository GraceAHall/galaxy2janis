
# NOTE
# This is an automated translation of the 'Unicycler training (imported from uploaded file)' version '1' workflow. 
# Translation was performed by the gxtool2janis program (in-development)

import sys
sys.path.append('/home/grace/work/pp/gxtool2janis')

from janis_core import WorkflowBuilder
from janis_core import WorkflowMetadata

from janis_core.types.common_data_types import File
from janis_unix.data_types.text import TextFile
from data.datatypes.galaxy import Html

from super_simple_workflow.tools.fastqc.fastqc import fastqc


metadata = WorkflowMetadata(
    short_documentation="Unicycler Assembly",
    contributors=['gxtool2janis'],
    keywords=['assembly'],
    dateCreated="2022-04-05",
    dateUpdated="2022-04-05",
    version=1,
    doi=None,
    citation=None
)

# WORKFLOW DECLARATION
w = WorkflowBuilder(
	"Unicycler training (imported from uploaded file)",
	version="1",
	doc="Unicycler Assembly"
)

# INPUTS
w.input("forward_reads", File)
w.input("reverse_reads", File)
w.input("long_reads", File)

# STEPS
w.input("fastqc_limits", TextFile)
w.input("fastqc_outdir", File)
w.input("fastqc_contaminants", Tabular)
w.input("fastqc_html_file", File)
w.input("fastqc_adapters", Tabular)

w.step(
	"fastqc",
	fastqc(
		#UNKNOWN=w.forward_reads,
		limits=w.fastqc_limits,
		outdir=w.fastqc_outdir,
		contaminants=w.fastqc_contaminants,
		html_file=w.fastqc_html_file,
		adapters=w.fastqc_adapters,
	)
)

# OUTPUTS
w.output(
	"fastqc_html_file",
	Html,
	source=(w.fastqc, "html_file")
)
w.output(
	"fastqc_text_file",
	TextFile,
	source=(w.fastqc, "text_file")
)

