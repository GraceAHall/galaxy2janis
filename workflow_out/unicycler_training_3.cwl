#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: forward_reads
  type: File
- id: reverse_reads
  type: File
- id: long_reads
  type: File
- id: fastqc1_adapters
  type: File
- id: fastqc1_contaminants
  type: File
- id: fastqc1_html_file
  type: File
- id: fastqc1_limits
  type: File
- id: fastqc1_outdir
  type: File
- id: fastqc2_adapters
  type: File
- id: fastqc2_contaminants
  type: File
- id: fastqc2_html_file
  type: File
- id: fastqc2_limits
  type: File
- id: fastqc2_outdir
  type: File
- id: unicycler_contamination
  type: File
- id: unicycler_fq11
  type: File
- id: unicycler_fq12
  type: File
- id: unicycler_l_file
  type: File
- id: unicycler_pilon_path
  type: File
- id: unicycler_start_genes
  type: File
- id: unicycler_start_gene_cov
  doc: The minimum required BLAST percent coverage for a start gene search
  type: float
  default: 95.0
- id: unicycler_start_gene_id
  doc: The minimum required BLAST percent identity for a start gene search
  type: float
  default: 90.0
- id: multiqc_multiqc_config
  type: File
- id: quast_labels
  type: File
- id: quast_references_list2
  type: File
- id: quast_skip_unaligned_mis_contigs
  doc: |-
    Distinguish contigs with more than 50% unaligned bases as a separate group of contigs? By default, QUAST breaks contigs only at extensive misassemblies (not local ones).. possible values: --skip-unaligned-mis-contigs
  type: boolean
  default: true
- id: prokka_proteins
  type: File
- id: prokka_genus
  doc: Genus name (--genus) May be used to aid annotation, see --usegenus below
  type: string
  default: Escherichia
- id: prokka_gcode
  doc: Genetic code (transl_table)
  type: int
  default: 11
- id: prokka_strain
  doc: Strain name (--strain)
  type: string
  default: C-1
- id: prokka_increment
  doc: Locus tag counter increment (--increment)
  type: int
  default: 10
- id: prokka_locustag
  doc: Locus tag prefix (--locustag)
  type: string
  default: PROKKA
- id: prokka_species
  doc: Species name (--species)
  type: string
  default: Coli

outputs:
- id: fastqc1_html_file_out
  type: File
  outputSource: fastqc1/html_file
- id: fastqc1_text_file_out
  type: File
  outputSource: fastqc1/text_file
- id: fastqc2_html_file_out
  type: File
  outputSource: fastqc2/html_file
- id: fastqc2_text_file_out
  type: File
  outputSource: fastqc2/text_file
- id: unicycler_assembly_out
  type: File
  outputSource: unicycler/assembly
- id: multiqc_stats_out
  type: File
  outputSource: multiqc/stats
- id: multiqc_html_report_out
  type: File
  outputSource: multiqc/html_report
- id: quast_report_html_out
  type: File
  outputSource: quast/report_html
- id: prokka_out_gff_out
  type: File
  outputSource: prokka/out_gff
- id: prokka_out_gbk_out
  type: File
  outputSource: prokka/out_gbk
- id: prokka_out_fna_out
  type: File
  outputSource: prokka/out_fna
- id: prokka_out_faa_out
  type: File
  outputSource: prokka/out_faa
- id: prokka_out_ffn_out
  type: File
  outputSource: prokka/out_ffn
- id: prokka_out_sqn_out
  type: File
  outputSource: prokka/out_sqn
- id: prokka_out_fsa_out
  type: File
  outputSource: prokka/out_fsa
- id: prokka_out_tbl_out
  type: File
  outputSource: prokka/out_tbl
- id: prokka_out_err_out
  type: File
  outputSource: prokka/out_err
- id: prokka_out_txt_out
  type: File
  outputSource: prokka/out_txt
- id: prokka_out_log_out
  type: File
  outputSource: prokka/out_log

steps:
- id: fastqc1
  in:
  - id: html_file
    source: fastqc1_html_file
  - id: adapters
    source: fastqc1_adapters
  - id: outdir
    source: fastqc1_outdir
  - id: contaminants
    source: fastqc1_contaminants
  - id: limits
    source: fastqc1_limits
  run: tools/fastqc_0_72.cwl
  out:
  - id: html_file
  - id: text_file
- id: fastqc2
  in:
  - id: html_file
    source: fastqc2_html_file
  - id: adapters
    source: fastqc2_adapters
  - id: outdir
    source: fastqc2_outdir
  - id: contaminants
    source: fastqc2_contaminants
  - id: limits
    source: fastqc2_limits
  run: tools/fastqc_0_72.cwl
  out:
  - id: html_file
  - id: text_file
- id: unicycler
  in:
  - id: fq11
    source: unicycler_fq11
  - id: fq12
    source: unicycler_fq12
  - id: s_FastqSanger
    source: forward_reads
  - id: FastqSanger_2
    source: reverse_reads
  - id: long
    source: long_reads
  - id: start_genes
    source: unicycler_start_genes
  - id: start_gene_id
    source: unicycler_start_gene_id
  - id: start_gene_cov
    source: unicycler_start_gene_cov
  - id: contamination
    source: unicycler_contamination
  - id: pilon_path
    source: unicycler_pilon_path
  - id: l_File
    source: unicycler_l_file
  run: tools/unicycler_0_4_8_0.cwl
  out:
  - id: assembly_graph
  - id: assembly
- id: multiqc
  in:
  - id: multiqc_config
    source: multiqc_multiqc_config
  run: tools/multiqc_1_7.cwl
  out:
  - id: stats
  - id: html_report
  - id: log
- id: quast
  in:
  - id: skip_unaligned_mis_contigs
    source: quast_skip_unaligned_mis_contigs
  - id: references_list2
    source: quast_references_list2
  - id: labels
    source: quast_labels
  run: tools/quast_5_0_2.cwl
  out:
  - id: quast_tabular
  - id: report_html
  - id: report_pdf
  - id: log
  - id: mis_ass
  - id: unalign
  - id: kmers
- id: prokka
  in:
  - id: locustag
    source: prokka_locustag
  - id: increment
    source: prokka_increment
  - id: genus
    source: prokka_genus
  - id: species
    source: prokka_species
  - id: strain
    source: prokka_strain
  - id: gcode
    source: prokka_gcode
  - id: proteins
    source: prokka_proteins
  - id: notrna
    source: unicycler/assembly
  run: tools/prokka_1_14_5.cwl
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
id: unicycler_training
