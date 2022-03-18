


from logging import basicConfig
from janis_core import WorkflowBuilder, String
from janis_bioinformatics.data_types import FastqGzPairedEnd, FastaWithDict
from janis_bioinformatics.tools.bwa import BwaMemLatest
from janis_bioinformatics.tools.samtools import SamToolsView_1_9
from janis_bioinformatics.tools.gatk4 import Gatk4SortSam_4_1_2


w = WorkflowBuilder("myWorkflow")


HTML_FILE_FILES_PATH = 'USER SET VALUE'
LIMITS = 'PLEASE SET THIS' 
"""
evidence:
#if $limits.dataset and str($limits) > ''
    --limits '${limits}'
#end if
"""


w.input('steps_fastqc_min_length', Int)
w.input('steps_fastqc_f_file', File)


w.step(
    preprocesfastqc
)

# basic
w.step(
    "fastqc", 
    fastqc( 
        quiet=True, 
		extract=True,
		nogroup=NOGROUP,
		outdir=RUNTIMEVALUE,
		contaminants=preprocesfastqc.out.contaminants,
		adapters=RUNTIMEVALUE,
		limits=RUNTIMEVALUE,
		threads=,
		min_length=w.steps_fastqc_min_length,
		kmers=7,
		f_file=w.steps_fastqc_f_file,
    )
)



# step runtime values
w.input('steps_fastqc_min_length', Int)
w.input('steps_fastqc_f_file', File)

# basic
w.step(
    "fastqc", 
    fastqc( 
        quiet=True, 
		extract=True,
		nogroup=NOGROUP,
		outdir=RUNTIMEVALUE,
		contaminants=RUNTIMEVALUE,
		adapters=RUNTIMEVALUE,
		limits=RUNTIMEVALUE,
		threads=2,
		min_length=w.steps_fastqc_min_length,
		kmers=7,
		f_file=w.steps_fastqc_f_file,
    )
)

# segmented cheetah template evaulation
"""
$contaminants = None
$min_length = 1000
$nogroup = checked
$format = 'sam' (because $input_file was a samfile)
"""
w.step(
    "fastqc", 
    fastqc( 
        quiet=True, 
		extract=True,
		nogroup=True,
		outdir=RUNTIMEVALUE,
		contaminants=RUNTIMEVALUE,
		adapters=RUNTIMEVALUE,
		limits=RUNTIMEVALUE,
		threads=2,
		min_length=1000,
		kmers=7,
		f_file='sam',
    )
)

# runtime values supplied
w.step(
    "fastqc", 
    fastqc( 
        quiet=True, 
		extract=True,
		nogroup=True,
		outdir=RUNTIMEVALUE, # just current issue
		#contaminants=None,
		adapters='dataset.dat',
		limits='limits.dat',
		threads=2,
		min_length=1000,
		kmers=7,
		f_file='sam',
    )
)