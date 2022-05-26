#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_foward_reads
  type: string
- id: in_reverse_reads
  type: string
- id: shovill_r1
  type: string
- id: shovill_r2
  type: string
- id: shovill_trim
  doc: None
  type: boolean
  default: false
- id: shovill_gsize
  doc: |-
    Estimated genome size. An estimate of the final genome size, it will autodetect if this is blank. (default: '')
  type:
  - string
  - 'null'
- id: shovill_kmers
  doc: |-
    List of kmer sizes to use. List of K-mer sizes to use in SPAdes. Blank is AUTO. default: ''
  type:
  - string
  - 'null'
- id: shovill_namefmt
  doc: |-
    Contig name format. Format of contig FASTA IDs in 'printf' style (default: 'contig%05d')
  type: string
- id: shovill_opts
  doc: "Extra SPAdes options. eg. --plasmid --sc ... (default: '')"
  type:
  - string
  - 'null'
- id: shovill_nocorr
  doc: None
  type: boolean
  default: true
- id: shovill_assembler
  doc: |-
    Assembler to use. Which assembler would you like shovill to use, default is Spades. possible values: megahit, skesa, spades, velvet
  type: string
  default: spades
- id: shovill_cpus
  doc: None
  type: int
  default: 1
- id: shovill_depth
  doc: 'Depth. Sub-sample --R1/--R2 to this depth. Disable with --depth 0 (default:
    100)'
  type: int
  default: 100
- id: shovill_mincov
  doc: |-
    Minimum contig coverage. Minimum coverage to call part of a contig. 0 is AUTO (default: 2)
  type: int
  default: 2
- id: shovill_minlen
  doc: |-
    Minimum contig length. Minimum length of contig to be output. 0 is AUTO (default: 0)
  type: int
  default: 0
- id: shovill_outdir
  doc: None
  type: string
  default: out
- id: shovill_ram
  doc: None
  type: int
  default: 4

outputs:
- id: shovill_out_shovill_std_log
  type: File
  outputSource: shovill/out_shovill_std_log
- id: shovill_out_contigs
  type: File
  outputSource: shovill/out_contigs
- id: shovill_out_contigs_graph
  type: File
  outputSource: shovill/out_contigs_graph

steps:
- id: shovill
  in:
  - id: nocorr
    source: shovill_nocorr
  - id: trim
    source: shovill_trim
  - id: assembler
    source: shovill_assembler
  - id: cpus
    source: shovill_cpus
  - id: depth
    source: shovill_depth
  - id: gsize
    source: shovill_gsize
  - id: kmers
    source: shovill_kmers
  - id: mincov
    source: shovill_mincov
  - id: minlen
    source: shovill_minlen
  - id: namefmt
    source: shovill_namefmt
  - id: opts
    source: shovill_opts
  - id: outdir
    source: shovill_outdir
  - id: r1
    source: shovill_r1
  - id: r2
    source: shovill_r2
  - id: ram
    source: shovill_ram
  run: tools/shovill_1_1_0.cwl
  out:
  - id: out_shovill_std_log
  - id: out_contigs
  - id: out_contigs_graph
id: shovill_test
