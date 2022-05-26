#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_genome_assembly
  type: File
- id: prokka_proteins
  type: File
- id: prokka_addgenes
  doc: None
  type: boolean
  default: false
- id: prokka_compliant
  doc: None
  type: boolean
  default: false
- id: prokka_fast
  doc: 'Fast mode. Skip CDS /product searching. possible values: false, true'
  type: boolean
  default: false
- id: prokka_metagenome
  doc: |-
    Improve gene predictions for highly fragmented genomes. Will set --meta option for Prodigal. possible values: false, true
  type: boolean
  default: false
- id: prokka_norrna
  doc: "Don't run rRNA search with Barrnap. possible values: false, true"
  type: boolean
  default: false
- id: prokka_notrna
  doc: "Don't run tRNA search with Aragorn. possible values: false, true"
  type: boolean
  default: false
- id: prokka_rfam
  doc: |-
    Enable searching for ncRNAs with Infernal+Rfam (SLOW!). possible values: false, true
  type: boolean
  default: false
- id: prokka_usegenus
  doc: |-
    Use genus-specific BLAST database. Will use the BLAST database for the genus specified above, if installed. possible values: false, true
  type: boolean
  default: false
- id: prokka_centre
  doc: Sequencing centre ID
  type: string
- id: prokka_genus
  doc: Genus name. May be used to aid annotation, see --usegenus below
  type: string
- id: prokka_kingdom
  doc: None
  type: string
  default: Bacteria
- id: prokka_locustag
  doc: Locus tag prefix
  type: string
- id: prokka_plasmid
  doc: Plasmid name or identifier
  type: string
- id: prokka_species
  doc: Species name
  type: string
- id: prokka_strain
  doc: Strain name
  type: string
- id: prokka_quiet
  doc: None
  type: boolean
  default: true
- id: prokka_cpus
  doc: None
  type: int
  default: 8
- id: prokka_evalue
  doc: Similarity e-value cut-off
  type: float
  default: 1e-06
- id: prokka_gcode
  doc: Genetic code (transl_table)
  type: int
  default: 11
- id: prokka_gffver
  doc: 'GFF version. possible values: 1, 2, 3'
  type: string
  default: '3'
- id: prokka_increment
  doc: Locus tag counter increment
  type: int
  default: 1
- id: prokka_mincontig
  doc: Minimum contig size (--mincontiglen). NCBI needs 200
  type: int
  default: 200
- id: prokka_outdir
  doc: None
  type: string
  default: outdir
- id: prokka_prefix
  doc: None
  type: string
  default: prokka

outputs:
- id: prokka_out_gff
  type: File
  outputSource: prokka/out_gff
- id: prokka_out_gbk
  type: File
  outputSource: prokka/out_gbk
- id: prokka_out_fna
  type: File
  outputSource: prokka/out_fna
- id: prokka_out_faa
  type: File
  outputSource: prokka/out_faa
- id: prokka_out_ffn
  type: File
  outputSource: prokka/out_ffn
- id: prokka_out_sqn
  type: string
  outputSource: prokka/out_sqn
- id: prokka_out_fsa
  type: File
  outputSource: prokka/out_fsa
- id: prokka_out_tbl
  type: File
  outputSource: prokka/out_tbl
- id: prokka_out_tsv
  type: File
  outputSource: prokka/out_tsv
- id: prokka_out_err
  type: File
  outputSource: prokka/out_err
- id: prokka_out_txt
  type: File
  outputSource: prokka/out_txt
- id: prokka_out_log
  type: File
  outputSource: prokka/out_log

steps:
- id: prokka
  in:
  - id: input_fasta
    source: in_genome_assembly
  - id: addgenes
    source: prokka_addgenes
  - id: compliant
    source: prokka_compliant
  - id: fast
    source: prokka_fast
  - id: metagenome
    source: prokka_metagenome
  - id: norrna
    source: prokka_norrna
  - id: notrna
    source: prokka_notrna
  - id: quiet
    source: prokka_quiet
  - id: rfam
    source: prokka_rfam
  - id: usegenus
    source: prokka_usegenus
  - id: centre
    source: prokka_centre
  - id: cpus
    source: prokka_cpus
  - id: evalue
    source: prokka_evalue
  - id: gcode
    source: prokka_gcode
  - id: genus
    source: prokka_genus
  - id: gffver
    source: prokka_gffver
  - id: increment
    source: prokka_increment
  - id: kingdom
    source: prokka_kingdom
  - id: locustag
    source: prokka_locustag
  - id: mincontig
    source: prokka_mincontig
  - id: outdir
    source: prokka_outdir
  - id: plasmid
    source: prokka_plasmid
  - id: prefix
    source: prokka_prefix
  - id: proteins
    source: prokka_proteins
  - id: species
    source: prokka_species
  - id: strain
    source: prokka_strain
  run: tools/prokka_1_14_6.cwl
  out:
  - id: out_gff
  - id: out_gbk
  - id: out_fna
  - id: out_faa
  - id: out_ffn
  - id: out_sqn
  - id: out_fsa
  - id: out_tbl
  - id: out_tsv
  - id: out_err
  - id: out_txt
  - id: out_log
id: prokka_test
