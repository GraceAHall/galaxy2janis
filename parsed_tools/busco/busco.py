from janis_core import (
            CommandToolBuilder,
            InputSelector,
            ToolInput,
            ToolOutput
        )

        
inputs = [
ToolInput(
"input",
Fasta,
prefix="--in",
default="",
doc="Can be an assembled genome or transcriptome (DNA), or protein sequences from an annotated gene set."
)
,
ToolInput(
"mode",
String,
prefix="--mode",
default="",
doc="Mode  example values: geno, tran, prot"
)
,
ToolInput(
"use_augustus_selector",
String,
prefix="None",
default="",
doc="Use Augustus instead of Metaeuk  example values: yes, no"
)
,
ToolInput(
"augustus_mode",
String,
prefix="None",
default="",
doc="Augustus species model  example values: no, builtin, history"
)
,
ToolInput(
"augustus_model",
none,
prefix="-xzf",
default="",
doc="Augustus model"
)
,
ToolInput(
"augustus_species",
String,
prefix="--augustus_species",
default="",
doc="Augustus species model  example values: human, fly, arabidopsis, brugia , aedes..."
)
,
ToolInput(
"long",
Boolean,
prefix="",
default="",
doc="Adds considerably to run time, but can improve results for some non-model organisms"
)
,
ToolInput(
"lineage_mode",
String,
prefix="None",
default="",
doc="Auto-detect or select lineage?  example values: auto_detect, select_lineage"
)
,
ToolInput(
"auto_lineage",
Boolean,
prefix="",
default="",
doc="Run auto-lineage to find optimum lineage path"
)
,
ToolInput(
"lineage_dataset",
String,
prefix="--lineage_dataset",
default="",
doc="Lineage  example values: acidobacteria_odb10, aconoidasida_odb10, actinobacteria_class_odb10, actinobacteria_phylum_odb10, actinopterygii_odb10..."
)
,
ToolInput(
"evalue",
Float,
prefix="--evalue",
default="0.001",
doc="E-value cutoff for BLAST searches."
)
,
ToolInput(
"limit",
Integer,
prefix="--limit",
default="3",
doc="How many candidate regions to consider"
)
,
ToolInput(
"outputs",
String,
prefix="None",
default="",
doc="Which outputs should be generated  example values: short_summary, missing, image"
)
,
]
outputs = [
ToolOutput(
"busco_sum",
TextFile,
selector="WildcardSelector(busco_galaxy/run_*/short_summary.txt)",
doc="short summary"
)
,
ToolOutput(
"busco_table",
tsv,
selector="WildcardSelector(busco_galaxy/run_*/full_table.tsv)",
doc="full table"
)
,
ToolOutput(
"busco_missing",
tsv,
selector="WildcardSelector(busco_galaxy/run_*/missing_busco_list.tsv)",
doc="missing buscos"
)
,
ToolOutput(
"summary_image",
none,
selector="WildcardSelector(BUSCO_summaries/busco_figure.png)",
doc="summary image"
)
,
]
busco = CommandToolBuilder(
tool="busco"
base_command=[""]
inputs=inputs
outputs=outputs
)

