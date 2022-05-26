#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_forward_reads
  type: string
- id: in_reverse_reads
  type: string
- id: in_long_reads
  type: string
- id: unicycler_start_genes
  type: File
- id: unicycler_contamination
  type: File
- id: unicycler_largest_component
  doc: |-
    Only keep the largest connected component of the assembly graph. possible values: false, true
  type: boolean
  default: false
- id: unicycler_no_correct
  doc: None
  type: boolean
  default: false
- id: unicycler_no_pilon
  doc: None
  type: boolean
  default: false
- id: unicycler_no_rotate
  doc: None
  type: boolean
  default: false
- id: unicycler_kmers
  doc: Exact k-mers to use for SPAdes assembly, comma-separated
  type:
  - string
  - 'null'
- id: unicycler_low_score
  doc: |-
    Score threshold - alignments below this are considered poor. default = set automatically
  type:
  - int
  - 'null'
- id: unicycler_min_anchor_seg_len
  doc: Unicycler will not use segments shorter than this as scaffolding anchors
  type:
  - int
  - 'null'
- id: unicycler_option_o
  doc: None
  type: string
- id: unicycler_option_s
  doc: Select unpaired reads. Specify dataset with unpaired reads
  type: File
- id: unicycler_pilon_path
  doc: None
  type: string
  default: "{'no_pilon':"
- id: unicycler_scores
  doc: |-
    Comma-delimited string of alignment scores: match, mismatch, gap open, gap extend
  type: string
- id: unicycler_start_gene_cov
  doc: The minimum required BLAST percent coverage for a start gene search
  type: float
  default: 95.0
- id: unicycler_start_gene_id
  doc: The minimum required BLAST percent identity for a start gene search
  type: float
  default: 90.0
- id: unicycler_depth_filter
  doc: |-
    Filter out contigs lower than this fraction of the chromosomal depth. It is done if does not result in graph dead ends
  type: float
  default: 0.25
- id: unicycler_kmer_count
  doc: Number of k-mer steps to use in SPAdes assembly
  type: int
  default: 10
- id: unicycler_linear_seqs
  doc: The expected number of linear (i.e. non-circular) sequences in the assembly
  type: int
  default: 0
- id: unicycler_max_kmer_frac
  doc: |-
    Highest k-mer size for SPAdes assembly, expressed as a fraction of the read length
  type: float
  default: 0.95
- id: unicycler_min_component_size
  doc: |-
    Unbridged graph components smaller than this size will be removed from the final graph
  type: int
  default: 1000
- id: unicycler_min_dead_end_size
  doc: Graph dead ends smaller than this size will be removed from the final graph
  type: int
  default: 1000
- id: unicycler_min_fasta_length
  doc: Exclude contigs from the FASTA file which are shorter than this length (bp)
  type: int
  default: 100
- id: unicycler_min_kmer_frac
  doc: |-
    Lowest k-mer size for SPAdes assembly, expressed as a fraction of the read length
  type: float
  default: 0.2
- id: unicycler_min_polish_size
  doc: Contigs shorter than this value (bp) will not be polished using Pilon
  type: int
  default: 1000
- id: unicycler_mode
  doc: 'Select Bridging mode. possible values: bold, conservative, normal'
  type: string
  default: normal
- id: unicycler_option_t
  doc: None
  type: int
  default: 4
- id: unicycler_verbosity
  doc: None
  type: int
  default: 3

outputs:
- id: unicycler_out_assembly
  type: File
  outputSource: unicycler/out_assembly

steps:
- id: unicycler
  in:
  - id: largest_component
    source: unicycler_largest_component
  - id: no_correct
    source: unicycler_no_correct
  - id: no_pilon
    source: unicycler_no_pilon
  - id: no_rotate
    source: unicycler_no_rotate
  - id: contamination
    source: unicycler_contamination
  - id: depth_filter
    source: unicycler_depth_filter
  - id: fastq_input1
    source: in_forward_reads
  - id: fastq_input2
    source: in_reverse_reads
  - id: kmer_count
    source: unicycler_kmer_count
  - id: kmers
    source: unicycler_kmers
  - id: linear_seqs
    source: unicycler_linear_seqs
  - id: low_score
    source: unicycler_low_score
  - id: max_kmer_frac
    source: unicycler_max_kmer_frac
  - id: min_anchor_seg_len
    source: unicycler_min_anchor_seg_len
  - id: min_component_size
    source: unicycler_min_component_size
  - id: min_dead_end_size
    source: unicycler_min_dead_end_size
  - id: min_fasta_length
    source: unicycler_min_fasta_length
  - id: min_kmer_frac
    source: unicycler_min_kmer_frac
  - id: min_polish_size
    source: unicycler_min_polish_size
  - id: mode
    source: unicycler_mode
  - id: option_l
    source: in_long_reads
  - id: option_o
    source: unicycler_option_o
  - id: option_s
    source: unicycler_option_s
  - id: option_t
    source: unicycler_option_t
  - id: pilon_path
    source: unicycler_pilon_path
  - id: scores
    source: unicycler_scores
  - id: start_gene_cov
    source: unicycler_start_gene_cov
  - id: start_gene_id
    source: unicycler_start_gene_id
  - id: start_genes
    source: unicycler_start_genes
  - id: verbosity
    source: unicycler_verbosity
  run: tools/unicycler_0_4_8_0.cwl
  out:
  - id: out_assembly_graph
  - id: out_assembly
id: unicycler_training_imported_from_uploaded_file
