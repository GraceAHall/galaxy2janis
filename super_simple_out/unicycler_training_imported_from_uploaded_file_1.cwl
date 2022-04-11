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
- id: fastqc_html_file
  type: File
- id: fastqc_limits
  type: File
- id: fastqc_outdir
  type: File
- id: fastqc_nogroup
  doc: |-
    Disable grouping of bases for reads >50bp Using this option will cause fastqc to crash and burn if you use it on really long reads, and your plots may end up a ridiculous size. You have been warned!. possible values: --nogroup
  type: boolean
  default: false

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
  - id: html_file
    source: fastqc_html_file
  - id: nogroup
    source: fastqc_nogroup
  - id: adapters
    source: fastqc_adapters
  - id: outdir
    source: fastqc_outdir
  - id: contaminants
    source: fastqc_contaminants
  - id: limits
    source: fastqc_limits
  run: tools/fastqc_0_72.cwl
  out:
  - id: out_html_file
  - id: out_text_file
id: unicycler_training_imported_from_uploaded_file
