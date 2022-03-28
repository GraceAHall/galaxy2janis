
# NOTE
# This is an automated translation of the 'Unicycler training (imported from uploaded file)' version '1' workflow. 
# Translation was performed by the gxtool2janis program (in-development)

import sys
sys.path.append('/home/grace/work/pp/gxtool2janis')

from janis_core import WorkflowBuilder
from janis_core import WorkflowMetadata

from janis_core.types.common_data_types import File
from data.datatypes.galaxy import Html
from janis_unix.data_types.text import TextFile

from super_simple_workflow.tools.step3_fastqc.step3_fastqc import fastqc


metadata = WorkflowMetadata(
    short_documentation="Unicycler Assembly",
    contributors=['gxtool2janis'],
    keywords=['assembly'],
    dateCreated="2022-03-28",
    dateUpdated="2022-03-28",
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
w.input(
	"forward_reads0",
	File,
	doc="Forward reads"
)
w.input(
	"reverse_reads1",
	File,
	doc="Reverse Reads"
)
w.input(
	"long_reads2",
	File,
	doc="Long Reads"
)

# STEPS
w.step(
	"step3_fastqc",
	fastqc(
		quiet=True,
		extract=True,
		nogroup=False,
		outdir="$html_file.files_path",
		contaminants="RUNTIMEVALUE",
		adapters="RUNTIMEVALUE",
		limits="RUNTIMEVALUE",
		min_length=None,
		kmers=7,
		f_file="fastq html_file",
	)
)

# OUTPUTS
w.output(
	"fastqc_html_file",
	Html,
	source=(w.step3_fastqc, "html_file")
)
w.output(
	"fastqc_text_file",
	TextFile,
	source=(w.step3_fastqc, "text_file")
)

