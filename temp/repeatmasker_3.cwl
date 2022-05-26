#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_raw_genome_sequence
  type: string
- id: repeatmasker_wrapper_ali
  doc: 'Output alignments file. possible values: -ali'
  type: boolean
  default: false
- id: repeatmasker_wrapper_alu
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_div
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_flag_q
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_flag_s
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_flag_x
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_gcccalc
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_gff
  doc: 'Output annotation of repeats in GFF format. possible values: -gff'
  type: boolean
  default: false
- id: repeatmasker_wrapper_inv
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_is_clip
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_is_only
  doc: 'Only clip E coli insertion elements. possible values: -is_only'
  type: boolean
  default: false
- id: repeatmasker_wrapper_no_is
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_nocut
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_noint
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_nolow
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_norna
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_poly
  doc: 'Output list of potentially polymorphic microsatellites. possible values: -poly'
  type: boolean
  default: false
- id: repeatmasker_wrapper_primspec
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_qq
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_rodspec
  doc: None
  type: boolean
  default: false
- id: repeatmasker_wrapper_cutoff
  doc: Cutoff score for masking repeats
  type: int
- id: repeatmasker_wrapper_dir
  doc: None
  type: string
- id: repeatmasker_wrapper_gc
  doc: |-
    Select matrices for this GC%. Valid values are a percentage or -1 to choose the default
  type:
  - int
  - 'null'
- id: repeatmasker_wrapper_lib
  doc: Custom library of repeats
  type: File
- id: repeatmasker_wrapper_human
  doc: None
  type: string
  default: human
- id: repeatmasker_wrapper_excln
  doc: None
  type: boolean
  default: true
- id: repeatmasker_wrapper_xsmall
  doc: None
  type: boolean
  default: true
- id: repeatmasker_wrapper_frag
  doc: |-
    Maximum contiguous sequence searched. Maximum length of sequencing that is search without fragmenting
  type: int
  default: 40000
- id: repeatmasker_wrapper_libdir
  doc: None
  type: string
- id: repeatmasker_wrapper_parallel
  doc: None
  type: int
  default: 1
- id: repeatmasker_wrapper_species
  doc: |-
    Repeat source species. Source species (or clade name) used to select repeats from DFam
  type: string
  default: human

outputs:
- id: repeatmasker_wrapper_output_masked_genome
  type: File
  outputSource: repeatmasker_wrapper/output_masked_genome
- id: repeatmasker_wrapper_output_log
  type: File
  outputSource: repeatmasker_wrapper/output_log
- id: repeatmasker_wrapper_output_table
  type: File
  outputSource: repeatmasker_wrapper/output_table
- id: repeatmasker_wrapper_output_repeat_catalog
  type: File
  outputSource: repeatmasker_wrapper/output_repeat_catalog

steps:
- id: repeatmasker_wrapper
  in:
  - id: human
    source: repeatmasker_wrapper_human
  - id: ali
    source: repeatmasker_wrapper_ali
  - id: alu
    source: repeatmasker_wrapper_alu
  - id: div
    source: repeatmasker_wrapper_div
  - id: excln
    source: repeatmasker_wrapper_excln
  - id: flag_q
    source: repeatmasker_wrapper_flag_q
  - id: flag_s
    source: repeatmasker_wrapper_flag_s
  - id: flag_x
    source: repeatmasker_wrapper_flag_x
  - id: gcccalc
    source: repeatmasker_wrapper_gcccalc
  - id: gff
    source: repeatmasker_wrapper_gff
  - id: inv
    source: repeatmasker_wrapper_inv
  - id: is_clip
    source: repeatmasker_wrapper_is_clip
  - id: is_only
    source: repeatmasker_wrapper_is_only
  - id: no_is
    source: repeatmasker_wrapper_no_is
  - id: nocut
    source: repeatmasker_wrapper_nocut
  - id: noint
    source: repeatmasker_wrapper_noint
  - id: nolow
    source: repeatmasker_wrapper_nolow
  - id: norna
    source: repeatmasker_wrapper_norna
  - id: poly
    source: repeatmasker_wrapper_poly
  - id: primspec
    source: repeatmasker_wrapper_primspec
  - id: qq
    source: repeatmasker_wrapper_qq
  - id: rodspec
    source: repeatmasker_wrapper_rodspec
  - id: xsmall
    source: repeatmasker_wrapper_xsmall
  - id: cutoff
    source: repeatmasker_wrapper_cutoff
  - id: dir
    source: repeatmasker_wrapper_dir
  - id: frag
    source: repeatmasker_wrapper_frag
  - id: gc
    source: repeatmasker_wrapper_gc
  - id: lib
    source: repeatmasker_wrapper_lib
  - id: libdir
    source: repeatmasker_wrapper_libdir
  - id: parallel
    source: repeatmasker_wrapper_parallel
  - id: species
    source: repeatmasker_wrapper_species
  run: tools/repeatmasker_wrapper_4_1_2_p1.cwl
  out:
  - id: output_masked_genome
  - id: output_log
  - id: output_table
  - id: output_repeat_catalog
  - id: output_alignment
  - id: output_polymorphic
  - id: output_gff
id: repeatmasker
