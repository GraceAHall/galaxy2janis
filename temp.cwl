#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_forward_reads
  type: File
- id: in_reverse_reads
  type: File
- id: in_long_reads
  type: File
- id: fastqc_adapters
  type: File
- id: fastqc_contaminants
  type: File
- id: fastqc_limits
  type: File
- id: fastqc_outdir
  type: File
- id: fastqc_option_f
  type: File
- id: fastqc_nogroup
  doc: None
  type: boolean
  default: false
- id: fastqc_min_length
  doc: |-
    Lower limit on the length of the sequence to be shown in the report.  As long as you set this to a value greater or equal to your longest read length then this will be the sequence length used to create your read groups.  This can be useful for making directly comaparable statistics from datasets with somewhat variable read lengths.
  type:
  - int
  - 'null'
- id: fastqc_extract
  doc: None
  type: boolean
  default: true
- id: fastqc_quiet
  doc: None
  type: boolean
  default: true
- id: fastqc_kmers
  doc: |-
    length of Kmer to look for. note: the Kmer test is disabled and needs to be enabled using a custom Submodule and limits file
  type: int
  default: 7

outputs:
- id: fastqc_out_html_file
  type: File
  outputSource: fastqc/out_html_file
- id: fastqc_out_text_file
  type: File
  outputSource: fastqc/out_text_file

steps:
- id: fastqc
  in:
  - id: input_file
    source: in_forward_reads
  - id: extract
    source: fastqc_extract
  - id: nogroup
    source: fastqc_nogroup
  - id: quiet
    source: fastqc_quiet
  - id: adapters
    source: fastqc_adapters
  - id: contaminants
    source: fastqc_contaminants
  - id: kmers
    source: fastqc_kmers
  - id: limits
    source: fastqc_limits
  - id: min_length
    source: fastqc_min_length
  - id: option_f
    source: fastqc_option_f
  - id: outdir
    source: fastqc_outdir
  run: tools/fastqc_0_72.cwl
  out:
  - id: out_html_file
  - id: out_text_file
id: unicycler_training_imported_from_uploaded_file

