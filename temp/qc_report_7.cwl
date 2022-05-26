#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_reference_genes
  type: string
- id: in_bam_files
  type: string
- id: rseqc_infer_experiment_mapq
  doc: |-
    Minimum mapping quality. Minimum mapping quality for an alignment to be considered as 'uniquely mapped' (--mapq)
  type: int
  default: 30
- id: rseqc_infer_experiment_sample_size
  doc: Number of reads sampled from SAM/BAM file (default = 200000). (--sample-size)
  type: int
  default: 200000
- id: picard_markduplicates_assume_sorted
  doc: None
  type: string
- id: picard_markduplicates_barcode_tag
  doc: |-
    Barcode Tag. Barcode SAM tag. This tag can be utilized when you have data from an assay that includes Unique Molecular Indices. Typically 'RX' 
  type:
  - string
  - 'null'
- id: picard_markduplicates_duplicate_scoring_strategy
  doc: None
  type: string
- id: picard_markduplicates_input_bam
  doc: |-
    Select SAM/BAM dataset or dataset collection. If empty, upload or import a SAM/BAM dataset
  type: File
- id: picard_markduplicates_metrics_file
  doc: MarkDuplicate metrics
  type: File
- id: picard_markduplicates_optical_duplicate_pixel_distance
  doc: |-
    The maximum offset between two duplicte clusters in order to consider them optical duplicates. OPTICAL_DUPLICATE_PIXEL_DISTANCE; default=100
  type: int
- id: picard_markduplicates_output_bam
  doc: MarkDuplicates BAM output
  type: File
- id: picard_markduplicates_quiet
  doc: None
  type: string
- id: picard_markduplicates_remove_duplicates
  doc: None
  type: string
- id: picard_markduplicates_validation_stringency
  doc: None
  type: string
- id: picard_markduplicates_verbosity
  doc: None
  type: string
- id: picard_markduplicates_positional
  doc: None
  type: string
- id: samtools_idxstats_at
  doc: None
  type: string
- id: multiqc_flat
  doc: None
  type: boolean
  default: false
- id: multiqc_comment
  doc: Custom comment. It will be printed at the top of the report
  type:
  - string
  - 'null'
- id: multiqc_title
  doc: Report title. It is printed as page header
  type:
  - string
  - 'null'
- id: multiqc_config
  doc: None
  type: string
- id: multiqc_filename
  doc: None
  type: string
  default: report

outputs:
- id: rseqc_infer_experiment_output_textfile
  type: File
  outputSource: rseqc_infer_experiment/output_textfile
- id: picard_markduplicates_out_metrics_file
  type: File
  outputSource: picard_markduplicates/out_metrics_file
- id: picard_markduplicates_outfile
  type: File
  outputSource: picard_markduplicates/outfile
- id: samtools_idxstats_output_tabular
  type: File
  outputSource: samtools_idxstats/output_tabular
- id: multiqc_out_stats
  type: string
  outputSource: multiqc/out_stats
- id: multiqc_out_html_report
  type: File
  outputSource: multiqc/out_html_report

steps:
- id: rseqc_infer_experiment
  in:
  - id: mapq
    source: rseqc_infer_experiment_mapq
  - id: option_i
    source: in_bam_files
  - id: option_r
    source: in_reference_genes
  - id: sample_size
    source: rseqc_infer_experiment_sample_size
  run: tools/rseqc_infer_experiment_2_6_4_1.cwl
  out:
  - id: output_textfile
- id: picard_markduplicates
  in:
  - id: positional
    source: picard_markduplicates_positional
  - id: assume_sorted
    source: picard_markduplicates_assume_sorted
  - id: barcode_tag
    source: picard_markduplicates_barcode_tag
  - id: duplicate_scoring_strategy
    source: picard_markduplicates_duplicate_scoring_strategy
  - id: input_bam
    source: picard_markduplicates_input_bam
  - id: metrics_file
    source: picard_markduplicates_metrics_file
  - id: optical_duplicate_pixel_distance
    source: picard_markduplicates_optical_duplicate_pixel_distance
  - id: output_bam
    source: picard_markduplicates_output_bam
  - id: quiet
    source: picard_markduplicates_quiet
  - id: remove_duplicates
    source: picard_markduplicates_remove_duplicates
  - id: validation_stringency
    source: picard_markduplicates_validation_stringency
  - id: verbosity
    source: picard_markduplicates_verbosity
  run: tools/picard_MarkDuplicates_2_18_2_2.cwl
  out:
  - id: outfile
  - id: out_metrics_file
- id: samtools_idxstats
  in:
  - id: input_bam
    source: in_bam_files
  - id: at
    source: samtools_idxstats_at
  run: tools/samtools_idxstats_2_0_3.cwl
  out:
  - id: output_tabular
- id: multiqc
  in:
  - id: flat
    source: multiqc_flat
  - id: comment
    source: multiqc_comment
  - id: config
    source: multiqc_config
  - id: filename
    source: multiqc_filename
  - id: title
    source: multiqc_title
  run: tools/multiqc_1_8.cwl
  out:
  - id: out_stats
  - id: out_plots
  - id: out_html_report
  - id: out_log
id: qc_report
