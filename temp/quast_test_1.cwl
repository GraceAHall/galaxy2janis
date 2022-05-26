#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_genome_assembly
  type: File
- id: quast_circos
  doc: None
  type: boolean
  default: false
- id: quast_conserved_genes_finding
  doc: None
  type: boolean
  default: false
- id: quast_eukaryote
  doc: None
  type: boolean
  default: false
- id: quast_fragmented
  doc: |-
    Fragmented reference genome. Reference genome is fragmented (e.g. a scaffold reference). QUAST will try to detect misassemblies caused by the fragmentation and mark them fake (will be excluded from misassemblies). Note: QUAST will not detect misassemblies caused by the linear representation of circular genome . possible values: --fragmented
  type: boolean
  default: false
- id: quast_fungus
  doc: None
  type: boolean
  default: false
- id: quast_gene_finding
  doc: None
  type: boolean
  default: false
- id: quast_glimmer
  doc: None
  type: boolean
  default: false
- id: quast_k_mer_stats
  doc: None
  type: boolean
  default: false
- id: quast_large
  doc: None
  type: boolean
  default: false
- id: quast_mgm
  doc: None
  type: boolean
  default: false
- id: quast_rna_finding
  doc: None
  type: boolean
  default: false
- id: quast_skip_unaligned_mis_contigs
  doc: None
  type: boolean
  default: false
- id: quast_split_scaffolds
  doc: None
  type: boolean
  default: false
- id: quast_strict_na
  doc: None
  type: boolean
  default: false
- id: quast_test_no_ref
  doc: None
  type: boolean
  default: false
- id: quast_upper_bound_assembly
  doc: None
  type: boolean
  default: false
- id: quast_use_all_alignments
  doc: None
  type: boolean
  default: false
- id: quast_est_ref_size
  doc: Estimated reference genome size (in bp) for computing NGx statistics
  type:
  - int
  - 'null'
- id: quast_fragmented_max_indent
  doc: |-
    Fragment max indent. Mark translocation as fake if both alignments are located no further than N bases from the ends of the reference fragments. The value should be less than extensive misassembly size.Default value is 50. Note: requires --fragmented option
  type:
  - int
  - 'null'
- id: quast_gene_thresholds
  doc: |-
    Comma-separated list of thresholds (in bp) for gene lengths to find with a finding tool
  type:
  - string
  - 'null'
- id: quast_max_ref_num
  doc: |-
    Maximum number of reference genomes (per each assembly) to download after searching in the SILVA databa
  type:
  - int
  - 'null'
- id: quast_references_list
  doc: |-
    Comma-separated list of reference genomes. MetaQUAST will search for these references in the NCBI database and will download the found ones
  type:
  - string
  - 'null'
- id: quast_upper_bound_min_con
  doc: |-
    Minimal number of 'connecting reads' needed for joining upper bound contigs into a scaffold. This is important for a realistic estimation of genome assembly fragmentation due to long repeats. The default values is 2 for mate-pairs and 1 for long reads (PacBio or Nanopore libraries)
  type:
  - int
  - 'null'
- id: quast_metaquast
  doc: None
  type: string
  default: metaquast
- id: quast_quast2
  doc: None
  type: string
  default: quast
- id: quast_ambiguity_score
  doc: |-
    Score S for defining equally good alignments of a single contig. All alignments are sorted by decreasing LEN × IDY% value. All alignments with LEN × IDY% less than S × best(LEN × IDY%) are discarded. 
  type: float
  default: 0.99
- id: quast_ambiguity_usage
  doc: |-
    How processing equally good alignments of a contig (probably repeats)?. possible values: all, none, one
  type: string
  default: one
- id: quast_contig_thresholds
  doc: |-
    Comma-separated list of contig length thresholds (in bp). Used in # contigs ≥ x and total length (≥ x) metrics
  type: string
  default: 0,1000
- id: quast_extensive_mis_size
  doc: |-
    Lower threshold for the relocation size (gap or overlap size between left and right flanking sequence). Shorter relocations are considered as local misassemblies. It does not affect other types of extensive misassemblies (inversions and translocations). The default value is 1000 bp. Note that the threshold should be greater than maximum indel length which is 85 bp.
  type: int
  default: 1000
- id: quast_features
  doc: |-
    Genomic feature positions in the reference genome. Gene coordinates for the reference genome
  type:
  - File
  - 'null'
- id: quast_k_mer_size
  doc: Size of k
  type: int
  default: 101
- id: quast_labels
  doc: None
  type: string
  default: log_meta
- id: quast_min_alignment
  doc: |-
    Minimum length of alignment. Alignments shorter than this value will be filtered. Note that all alignments shorter than 65 bp will be filtered regardless of this threshold.
  type: int
  default: 65
- id: quast_min_contig
  doc: |-
    Lower threshold for a contig length (in bp). Shorter contigs won't be taken into account
  type: int
  default: 500
- id: quast_min_identity
  doc: |-
    Minimum IDY% considered as proper alignment. Alignments with IDY% worse than this value will be filtered. ote that all alignments with IDY% less than 80.0% will be filtered regardless of this threshold. 
  type: float
  default: 95.0
- id: quast_operons
  doc: |-
    Operon positions in the reference genome. Operon coordinates for the reference genome
  type:
  - File
  - 'null'
- id: quast_option_o
  doc: None
  type: string
  default: outputdir
- id: quast_option_r
  doc: Reference genome
  type:
  - File
  - 'null'
- id: quast_scaffold_gap_max_size
  doc: |-
    Max allowed scaffold gap length difference for detecting corresponding type of misassemblies. Longer inconsistencies are considered as relocations and thus, counted as extensive misassemblies. The default value is 10000 bp. Note that the threshold make sense only if it is greater than extensive misassembly size
  type: int
  default: 1000
- id: quast_threads
  doc: None
  type: int
  default: 1
- id: quast_unaligned_part_size
  doc: Lower threshold for detecting partially unaligned contigs
  type: int
  default: 500

outputs:
- id: quast_out_report_html
  type: File
  outputSource: quast/out_report_html

steps:
- id: quast
  in:
  - id: quast2
    source: quast_quast2
  - id: metaquast
    source: quast_metaquast
  - id: circos
    source: quast_circos
  - id: conserved_genes_finding
    source: quast_conserved_genes_finding
  - id: eukaryote
    source: quast_eukaryote
  - id: fragmented
    source: quast_fragmented
  - id: fungus
    source: quast_fungus
  - id: gene_finding
    source: quast_gene_finding
  - id: glimmer
    source: quast_glimmer
  - id: k_mer_stats
    source: quast_k_mer_stats
  - id: large
    source: quast_large
  - id: mgm
    source: quast_mgm
  - id: rna_finding
    source: quast_rna_finding
  - id: skip_unaligned_mis_contigs
    source: quast_skip_unaligned_mis_contigs
  - id: split_scaffolds
    source: quast_split_scaffolds
  - id: strict_na
    source: quast_strict_na
  - id: test_no_ref
    source: quast_test_no_ref
  - id: upper_bound_assembly
    source: quast_upper_bound_assembly
  - id: use_all_alignments
    source: quast_use_all_alignments
  - id: ambiguity_score
    source: quast_ambiguity_score
  - id: ambiguity_usage
    source: quast_ambiguity_usage
  - id: contig_thresholds
    source: quast_contig_thresholds
  - id: est_ref_size
    source: quast_est_ref_size
  - id: extensive_mis_size
    source: quast_extensive_mis_size
  - id: features
    source: quast_features
  - id: fragmented_max_indent
    source: quast_fragmented_max_indent
  - id: gene_thresholds
    source: quast_gene_thresholds
  - id: k_mer_size
    source: quast_k_mer_size
  - id: labels
    source: quast_labels
  - id: max_ref_num
    source: quast_max_ref_num
  - id: min_alignment
    source: quast_min_alignment
  - id: min_contig
    source: quast_min_contig
  - id: min_identity
    source: quast_min_identity
  - id: operons
    source: quast_operons
  - id: option_o
    source: quast_option_o
  - id: option_r
    source: quast_option_r
  - id: references_list
    source: quast_references_list
  - id: scaffold_gap_max_size
    source: quast_scaffold_gap_max_size
  - id: threads
    source: quast_threads
  - id: unaligned_part_size
    source: quast_unaligned_part_size
  - id: upper_bound_min_con
    source: quast_upper_bound_min_con
  run: tools/quast1_5_0_2.cwl
  out:
  - id: out_metrics_tabular
  - id: out_metrics_pdf
  - id: out_report_tabular
  - id: out_report_tabular_meta
  - id: out_report_html
  - id: out_report_html_meta
  - id: out_report_pdf
  - id: out_log
  - id: out_log_meta
  - id: out_mis_ass
  - id: out_unalign
  - id: out_kmers
  - id: out_circos_output
  - id: out_krona
id: quast_test
