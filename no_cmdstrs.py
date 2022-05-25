
# NOTE
# This is an automated translation of the 'Unicycler training (imported from uploaded file)' version '3' workflow. 
# Translation was performed by the gxtool2janis program (in-development)

import sys
sys.path.append('/home/grace/work/pp/gxtool2janis')

from janis_core.types.common_data_types import String
from janis_unix.data_types.text import TextFile
from data.datatypes.galaxy import Tabular
from data.datatypes.galaxy import Fasta
from data.datatypes.galaxy import Html
from data.datatypes.galaxy import Gff

from janis_core import WorkflowMetadata
from janis_core import WorkflowBuilder

from parsed.workflows.simple_workflow.tools.unicycler.unicycler import unicycler
from parsed.workflows.simple_workflow.tools.multiqc.multiqc import multiqc
from parsed.workflows.simple_workflow.tools.fastqc.fastqc import fastqc
from parsed.workflows.simple_workflow.tools.prokka.prokka import prokka
from parsed.workflows.simple_workflow.tools.quast.quast import quast

metadata = WorkflowMetadata(
    short_documentation="Unicycler Assembly",
    contributors=['gxtool2janis'],
    keywords=['assembly'],
    dateCreated="2022-05-25",
    dateUpdated="2022-05-25",
    version=3,
    doi=None,
    citation=None
)

# WORKFLOW DECLARATION
w = WorkflowBuilder(
	"unicycler_training_imported_from_uploaded_file",
	version="3",
	doc="Unicycler Assembly"
)

# INPUTS
w.input("in_forward_reads", String)
w.input("in_reverse_reads", String)
w.input("in_long_reads", String)

# STEPS
# =============
# STEP1: FASTQC
# =============

w.input("fastqc1_adapters", Tabular)
w.input("fastqc1_contaminants", Tabular)
w.input("fastqc1_limits", TextFile)
w.step(
	"fastqc1",
	fastqc(
		input_file=w.in_forward_reads,        # positional [Fastq]
		adapters=w.fastqc1_adapters,          # RUNTIME VALUE --adapters [Tabular]
		contaminants=w.fastqc1_contaminants,  # RUNTIME VALUE --contaminants [Tabular]
		limits=w.fastqc1_limits,              # RUNTIME VALUE --limits [TextFile]
		nogroup=False,                        # --nogroup [Boolean]
		min_length=None,                      # --min_length [Int]
		extract=True,   # --extract [Boolean] [GALAXY DEFAULT]
		quiet=True,     # --quiet [Boolean] [GALAXY DEFAULT]
		kmers=7,        # --kmers [Int] [GALAXY DEFAULT]
		option_f=None,  # -f [String] [GALAXY DEFAULT]
		outdir=None,    # --outdir [String] [GALAXY DEFAULT]
	)
)

# =============
# STEP2: FASTQC
# =============

w.input("fastqc2_adapters", Tabular)
w.input("fastqc2_contaminants", Tabular)
w.input("fastqc2_limits", TextFile)
w.step(
	"fastqc2",
	fastqc(
		input_file=w.in_reverse_reads,        # positional [Fastq]
		adapters=w.fastqc2_adapters,          # RUNTIME VALUE --adapters [Tabular]
		contaminants=w.fastqc2_contaminants,  # RUNTIME VALUE --contaminants [Tabular]
		limits=w.fastqc2_limits,              # RUNTIME VALUE --limits [TextFile]
		nogroup=False,                        # --nogroup [Boolean]
		min_length=None,                      # --min_length [Int]
		extract=True,   # --extract [Boolean] [GALAXY DEFAULT]
		quiet=True,     # --quiet [Boolean] [GALAXY DEFAULT]
		kmers=7,        # --kmers [Int] [GALAXY DEFAULT]
		option_f=None,  # -f [String] [GALAXY DEFAULT]
		outdir=None,    # --outdir [String] [GALAXY DEFAULT]
	)
)

# ================
# STEP3: UNICYCLER
# ================

w.input("unicycler_start_genes", Fasta)
w.input("unicycler_contamination", Fasta)
w.step(
	"unicycler",
	unicycler(
		contamination=w.unicycler_contamination,  # RUNTIME VALUE --contamination [Fasta]
		fastq_input1=w.in_forward_reads,          # -1 [FastqSanger]
		fastq_input2=w.in_reverse_reads,          # -2 [FastqSanger]
		option_l=w.in_long_reads,                 # -l [FastqSanger]
		start_genes=w.unicycler_start_genes,      # RUNTIME VALUE --start_genes [Fasta]
		largest_component=False,                  # --largest_component [Boolean]
		no_correct=False,                         # --no_correct [Boolean]
		no_pilon=False,                           # --no_pilon [Boolean]
		no_rotate=False,                          # --no_rotate [Boolean]
		kmers=None,                               # --kmers [String]
		low_score=None,                           # --low_score [Int]
		min_anchor_seg_len=None,                  # --min_anchor_seg_len [Int]
		option_o=None,                            # -o [String]
		option_s=None,                            # -s [FastqSanger]
		pilon_path="{'no_pilon':",                # --pilon_path [String]
		scores=None,                              # --scores [String]
		start_gene_cov=95.0,                      # --start_gene_cov [Float]
		start_gene_id=90.0,                       # --start_gene_id [Float]
		depth_filter=0.25,        # --depth_filter [Float] [GALAXY DEFAULT]
		kmer_count=10,            # --kmer_count [Int] [GALAXY DEFAULT]
		linear_seqs=0,            # --linear_seqs [Int] [GALAXY DEFAULT]
		max_kmer_frac=0.95,       # --max_kmer_frac [Float] [GALAXY DEFAULT]
		min_component_size=1000,  # --min_component_size [Int] [GALAXY DEFAULT]
		min_dead_end_size=1000,   # --min_dead_end_size [Int] [GALAXY DEFAULT]
		min_fasta_length=100,     # --min_fasta_length [Int] [GALAXY DEFAULT]
		min_kmer_frac=0.2,        # --min_kmer_frac [Float] [GALAXY DEFAULT]
		min_polish_size=1000,     # --min_polish_size [Int] [GALAXY DEFAULT]
		mode="normal",            # --mode [String] [GALAXY DEFAULT]
		option_t=4,               # -t [Int] [GALAXY DEFAULT]
		verbosity=3,              # --verbosity [Int] [GALAXY DEFAULT]
	)
)

# ==============
# STEP4: MULTIQC
# ==============

w.step(
	"multiqc",
	multiqc(
		#UNKNOWN=w.fastqc1.out_text_file,  # UNLINKED INPUT (step 3 text_file) [TextFile]
		#UNKNOWN=w.fastqc2.out_text_file,  # UNLINKED INPUT (step 4 text_file) [TextFile]
		comment=None,  # --comment [String]
		title=None,    # --title [String]
		config=None,        # --config [String] [GALAXY DEFAULT]
		filename="report",  # --filename [String] [GALAXY DEFAULT]
	)
)

# ============
# STEP5: QUAST
# ============

w.step(
	"quast",
	quast(
		#UNKNOWN=w.unicycler.out_assembly,  # UNLINKED INPUT (step 5 assembly) [Fasta]
		circos=False,                      # --circos [Boolean]
		conserved_genes_finding=False,     # --conserved-genes-finding [Boolean]
		eukaryote=False,                   # --eukaryote [Boolean]
		fragmented=False,                  # --fragmented [Boolean]
		fungus=False,                      # --fungus [Boolean]
		gene_finding=False,                # --gene-finding [Boolean]
		glimmer=False,                     # --glimmer [Boolean]
		k_mer_stats=False,                 # --k-mer-stats [Boolean]
		large=False,                       # --large [Boolean]
		mgm=False,                         # --mgm [Boolean]
		rna_finding=False,                 # --rna-finding [Boolean]
		skip_unaligned_mis_contigs=False,  # --skip-unaligned-mis-contigs [Boolean]
		split_scaffolds=False,             # --split-scaffolds [Boolean]
		strict_na=False,                   # --strict-NA [Boolean]
		test_no_ref=False,                 # --test-no-ref [Boolean]
		use_all_alignments=False,          # --use-all-alignments [Boolean]
		contig_thresholds=None,            # --contig-thresholds [String]
		est_ref_size=None,                 # --est-ref-size [Int]
		gene_thresholds=None,              # --gene-thresholds [String]
		k_mer_size=None,                   # --k-mer-size [Int]
		max_ref_num=None,                  # --max-ref-num [Int]
		references_list=None,              # --references-list [String]
		ambiguity_usage="one",       # --ambiguity-usage [String] [GALAXY DEFAULT]
		extensive_mis_size=1000,     # --extensive-mis-size [Int] [GALAXY DEFAULT]
		features=None,               # --features [Gff] [GALAXY DEFAULT]
		labels=None,                 # --labels [String] [GALAXY DEFAULT]
		min_alignment=65,            # --min-alignment [Int] [GALAXY DEFAULT]
		min_contig=500,              # --min-contig [Int] [GALAXY DEFAULT]
		min_identity=95.0,           # --min-identity [Float] [GALAXY DEFAULT]
		operons=None,                # --operons [Gff] [GALAXY DEFAULT]
		option_o="outputdir",        # -o [String] [GALAXY DEFAULT]
		option_r=None,               # -r [Fasta] [GALAXY DEFAULT]
		scaffold_gap_max_size=1000,  # --scaffold-gap-max-size [Int] [GALAXY DEFAULT]
		threads=1,                   # --threads [Int] [GALAXY DEFAULT]
		unaligned_part_size=500,     # --unaligned-part-size [Int] [GALAXY DEFAULT]
	)
)

# =============
# STEP6: PROKKA
# =============

w.input("prokka_proteins", Fasta)
w.step(
	"prokka",
	prokka(
		input_fasta=w.unicycler.out_assembly,  # INPUT CONNECTION positional [Fasta]
		proteins=w.prokka_proteins,            # RUNTIME VALUE --proteins [Fasta]
		addgenes=False,                        # --addgenes [Boolean]
		compliant=False,                       # --compliant [Boolean]
		fast=False,                            # --fast [Boolean]
		metagenome=False,                      # --metagenome [Boolean]
		norrna=False,                          # --norrna [Boolean]
		rfam=False,                            # --rfam [Boolean]
		centre=None,                           # --centre [String]
		genus="Escherichia",                   # --genus [String]
		increment=10,                          # --increment [Int]
		kingdom="Bacteria",                    # --kingdom [String]
		locustag="PROKKA",                     # --locustag [String]
		plasmid=None,                          # --plasmid [String]
		species="Coli",                        # --species [String]
		strain="C-1",                          # --strain [String]
		quiet=True,       # --quiet [Boolean] [GALAXY DEFAULT]
		usegenus=True,    # --usegenus [Boolean] [GALAXY DEFAULT]
		cpus=8,           # --cpus [Int] [GALAXY DEFAULT]
		evalue=1e-06,     # --evalue [Float] [GALAXY DEFAULT]
		gcode=11,         # --gcode [Int] [GALAXY DEFAULT]
		gffver=3,         # --gffver [Int] [GALAXY DEFAULT]
		mincontig=200,    # --mincontig [Int] [GALAXY DEFAULT]
		outdir="outdir",  # --outdir [String] [GALAXY DEFAULT]
		prefix="prokka",  # --prefix [String] [GALAXY DEFAULT]
	)
)

# OUTPUTS
w.output(
	"fastqc1_out_html_file",
	Html,
	source=(w.fastqc1, "out_html_file")
)
w.output(
	"fastqc1_out_text_file",
	TextFile,
	source=(w.fastqc1, "out_text_file")
)
w.output(
	"fastqc2_out_html_file",
	Html,
	source=(w.fastqc2, "out_html_file")
)
w.output(
	"fastqc2_out_text_file",
	TextFile,
	source=(w.fastqc2, "out_text_file")
)
w.output(
	"unicycler_out_assembly",
	Fasta,
	source=(w.unicycler, "out_assembly")
)
w.output(
	"multiqc_out_stats",
	String,
	source=(w.multiqc, "out_stats")
)
w.output(
	"multiqc_out_html_report",
	Html,
	source=(w.multiqc, "out_html_report")
)
w.output(
	"quast_out_report_html",
	Html,
	source=(w.quast, "out_report_html")
)
w.output(
	"prokka_out_gff",
	Gff,
	source=(w.prokka, "out_gff")
)
w.output(
	"prokka_out_gbk",
	TextFile,
	source=(w.prokka, "out_gbk")
)
w.output(
	"prokka_out_fna",
	Fasta,
	source=(w.prokka, "out_fna")
)
w.output(
	"prokka_out_faa",
	Fasta,
	source=(w.prokka, "out_faa")
)
w.output(
	"prokka_out_ffn",
	Fasta,
	source=(w.prokka, "out_ffn")
)
w.output(
	"prokka_out_sqn",
	String,
	source=(w.prokka, "out_sqn")
)
w.output(
	"prokka_out_fsa",
	Fasta,
	source=(w.prokka, "out_fsa")
)
w.output(
	"prokka_out_tbl",
	TextFile,
	source=(w.prokka, "out_tbl")
)
w.output(
	"prokka_out_err",
	TextFile,
	source=(w.prokka, "out_err")
)
w.output(
	"prokka_out_txt",
	TextFile,
	source=(w.prokka, "out_txt")
)
w.output(
	"prokka_out_log",
	TextFile,
	source=(w.prokka, "out_log")
)

