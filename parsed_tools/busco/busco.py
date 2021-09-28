
from janis_core import CommandToolBuilder, ToolOutput, ToolInput, WildcardSelector

from janis_bioinformatics.data_types import Fasta

from janis_core.types.common_data_types import Integer, String, File, Float, Boolean

from janis_unix.data_types.text import TextFile
from janis_unix.data_types.tsv import tsv


inputs = [
	ToolInput(
		"input",
		Fasta,
		prefix="--in",
		default="",
		doc="Can be an assembled genome or transcriptome (DNA), or protein sequences from an annotated gene set."
	),
	ToolInput(
		"mode",
		String,
		prefix="--mode",
		default="",
		doc="Mode  example values: geno, tran, prot"
	),
	ToolInput(
		"augustus_model",
		File,
		prefix="-xzf",
		default="",
		doc="Augustus model"
	),
	ToolInput(
		"augustus_species",
		String,
		prefix="--augustus_species",
		default="",
		doc="Augustus species model  example values: human, fly, arabidopsis, brugia , aedes..."
	),
	ToolInput(
		"long",
		Boolean,
		prefix="--long",
		default="",
		doc="Adds considerably to run time, but can improve results for some non-model organisms"
	),
	ToolInput(
		"auto_lineage",
		Boolean,
		prefix="--auto-lineage",
		default="",
		doc="Run auto-lineage to find optimum lineage path"
	),
	ToolInput(
		"auto_lineage",
		Boolean,
		prefix="--auto-lineage-prok",
		default="",
		doc="Run auto-lineage just on non-eukaryote trees to find optimum lineage path"
	),
	ToolInput(
		"auto_lineage",
		Boolean,
		prefix="--auto-lineage-euk",
		default="",
		doc="Run auto-placement just on eukaryote tree to find optimum lineage path"
	),
	ToolInput(
		"lineage_dataset",
		String,
		prefix="--lineage_dataset",
		default="",
		doc="Lineage  example values: acidobacteria_odb10, aconoidasida_odb10, actinobacteria_class_odb10, actinobacteria_phylum_odb10, actinopterygii_odb10..."
	),
	ToolInput(
		"evalue",
		Float,
		prefix="--evalue",
		default="0.001",
		doc="E-value cutoff for BLAST searches."
	),
	ToolInput(
		"limit",
		Integer,
		prefix="--limit",
		default="3",
		doc="How many candidate regions to consider"
	),
]

outputs = [
	ToolOutput(
		"busco_sum",
		TextFile,
		selector=WildcardSelector("busco_galaxy/run_*/short_summary.txt"),
		doc="short summary"
	),
	ToolOutput(
		"busco_table",
		tsv,
		selector=WildcardSelector("busco_galaxy/run_*/full_table.tsv"),
		doc="full table"
	),
	ToolOutput(
		"busco_missing",
		tsv,
		selector=WildcardSelector("busco_galaxy/run_*/missing_busco_list.tsv"),
		doc="missing buscos"
	),
	ToolOutput(
		"summary_image",
		File,
		selector=WildcardSelector("BUSCO_summaries/busco_figure.png"),
		doc="summary image"
	),
]


Busco = CommandToolBuilder(
	tool="Busco",
	base_command=["busco"],
	inputs=inputs,
	outputs=outputs,
	container="quay.io/biocontainers/busco",
	version="5.2.2",
)


if __name__ == "__main__":
	Busco().translate(
		"wdl", to_console=True
	)
