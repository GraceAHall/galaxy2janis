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
- id: fastqc1_adapters
  type: File
- id: fastqc1_contaminants
  type: File
- id: fastqc1_html_file
  type: File
- id: fastqc1_limits
  type: File
- id: fastqc1_nogroup
  doc: |-
    Disable grouping of bases for reads >50bp. Using this option will cause fastqc to crash and burn if you use it on really long reads, and your plots may end up a ridiculous size. You have been warned!. possible values: --nogroup
  type: boolean
  default: false
- id: fastqc2_adapters
  type: File
- id: fastqc2_contaminants
  type: File
- id: fastqc2_html_file
  type: File
- id: fastqc2_limits
  type: File
- id: fastqc2_nogroup
  doc: |-
    Disable grouping of bases for reads >50bp. Using this option will cause fastqc to crash and burn if you use it on really long reads, and your plots may end up a ridiculous size. You have been warned!. possible values: --nogroup
  type: boolean
  default: false
- id: unicycler_contamination
  type: File
- id: unicycler_input_l_file
  type: File
- id: unicycler_pilon_path
  type: File
- id: unicycler_start_genes
  type: File
- id: unicycler_no_rotate
  doc: |-
    Do not rotate completed replicons to start at a standard gene.. Unicycler uses TBLASTN to search for dnaA or repA alleles in each completed replicon. If one is found, the sequence is rotated and/or flipped so that it begins with that gene encoded on the forward strand. This provides consistently oriented assemblies and reduces the risk that a gene will be split across the start and end of the sequence.. possible values: --no_rotate
  type: boolean
  default: false
- id: unicycler_no_correct
  doc: |-
    Skip SPAdes error correction step. This option turns off SPAdes error correction. Generally it is highly recommended to use correction.. possible values: --no_correct
  type: boolean
  default: false
- id: unicycler_no_pilon
  doc: |-
    Do not use Pilon to polish the final assembly.. Unicycler uses Pilon tool for polishing final assembly.. possible values: --no_pilon
  type: boolean
  default: false
- id: unicycler_largest_component
  doc: |-
    Only keep the largest connected component of the assembly graph. possible values: false, true
  type: boolean
  default: false
- id: unicycler_start_gene_id
  doc: The minimum required BLAST percent identity for a start gene search
  type: float
  default: 90.0
- id: unicycler_start_gene_cov
  doc: The minimum required BLAST percent coverage for a start gene search
  type: float
  default: 95.0
- id: multiqc_config
  type: File
- id: quast_labels
  type: File
- id: quast_references_list2
  type: File
- id: quast_use_all_alignments
  doc: |-
    Use all alignments as in QUAST v.1.*. to compute genome fraction, # genomic features, # operons metrics?. By default, QUAST v.2.0 and higher filters out ambiguous and redundant alignments, keeping only one alignment per contig (or one set of non-overlapping or slightly overlapping alignments). possible values: --use-all-alignments
  type: boolean
  default: false
- id: quast_fragmented
  doc: |-
    Use all alignments as in QUAST v.1.*. to compute genome fraction, # genomic features, # operons metrics?. By default, QUAST v.2.0 and higher filters out ambiguous and redundant alignments, keeping only one alignment per contig (or one set of non-overlapping or slightly overlapping alignments). possible values: --fragmented
  type: boolean
  default: false
- id: quast_large
  doc: |-
    Is genome large (> 100 Mbp)?. Use optimal parameters for evaluation of large genomes. Affects speed and accuracy. In particular, imposes --eukaryote --min-contig 3000 --min-alignment 500 --extensive-mis-size 7000 (can be overridden manually with the corresponding options). In addition, this mode tries to identify misassemblies caused by transposable elements and exclude them from the number of misassemblies.. possible values: --large
  type: boolean
  default: false
- id: quast_skip_unaligned_mis_contigs
  doc: |-
    Distinguish contigs with more than 50% unaligned bases as a separate group of contigs?. By default, QUAST breaks contigs only at extensive misassemblies (not local ones).. possible values: --skip-unaligned-mis-contigs
  type: boolean
  default: true
- id: quast_upper_bound_assembly
  doc: |-
    Simulate upper bound assembly based on the reference genome and a given set reads?. Mate-pairs or long reads, such as Pacbio SMRT/Oxford Nanopore, are REQUIRED. This assembly is added to the comparison and could be useful for estimating the upper bounds of completeness and contiguity that theoretically can be reached by assembly software from this particular set of reads. The concept is based on the fact that the reference genome cannot be completely reconstructed from raw reads due to long genomic repeats and low covered regions. See Mikheenko et al., 2018 for more details. . possible values: --upper-bound-assembly
  type: boolean
  default: false
- id: quast_split_scaffolds
  doc: |-
    Are assemblies scaffolds rather than contigs?. QUAST will add split versions of assemblies to the comparison. Assemblies are split by continuous fragments of N's of length >= 10. If broken version is equal to the original assembly (i.e. nothing was split) it is not included in the comparison.. possible values: --split-scaffolds
  type: boolean
  default: false
- id: quast_circos
  doc: 'Draw Circos plot?. possible values: --circos'
  type: boolean
  default: false
- id: quast_conserved_genes_finding
  doc: |-
    Enables search for Universal Single-Copy Orthologs using BUSCO?. By default, we assume that the genome is prokaryotic, and BUSCO uses the bacterial database of orthologs. If the genome is eukaryotic (fungal), use --eukaryote (--fungus) option to force BUSCO to work with the eukaryotic (fungal) database. . possible values: --conserved-genes-finding
  type: boolean
  default: false
- id: quast_strict_na
  doc: |-
    Break contigs at every misassembly event (including local ones) to compute NAx and NGAx statistics?. By default, QUAST breaks contigs only at extensive misassemblies (not local ones).. possible values: --strict-NA
  type: boolean
  default: false
- id: quast_rna_finding
  doc: |-
    Enables ribosomal RNA gene finding?. By default, we assume that the genome is prokaryotic, and Barrnap uses the bacterial database for rRNA prediction. If the genome is eukaryotic (fungal), use --eukaryote (--fungus) option to force Barrnap to work with the eukaryotic (fungal) database. . possible values: --rna-finding
  type: boolean
  default: false
- id: prokka_proteins
  type: File
- id: prokka_species
  doc: Species name (--species)
  type: string
  default: Coli
- id: prokka_genus
  doc: Genus name (--genus). May be used to aid annotation, see --usegenus below
  type: string
  default: Escherichia
- id: prokka_strain
  doc: Strain name (--strain)
  type: string
  default: C-1
- id: prokka_locustag
  doc: Locus tag prefix (--locustag)
  type: string
  default: PROKKA
- id: prokka_increment
  doc: Locus tag counter increment (--increment)
  type: int
  default: 10

outputs:
- id: fastqc1_out_html_file
  type: File
  outputSource: fastqc1/out_html_file
- id: fastqc1_out_text_file
  type: File
  outputSource: fastqc1/out_text_file
- id: fastqc2_out_html_file
  type: File
  outputSource: fastqc2/out_html_file
- id: fastqc2_out_text_file
  type: File
  outputSource: fastqc2/out_text_file
- id: unicycler_out_assembly
  type: File
  outputSource: unicycler/out_assembly
- id: multiqc_out_stats
  type: File
  outputSource: multiqc/out_stats
- id: multiqc_out_html_report
  type: File
  outputSource: multiqc/out_html_report
- id: quast_out_report_html
  type: File
  outputSource: quast/out_report_html
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
  type: File
  outputSource: prokka/out_sqn
- id: prokka_out_fsa
  type: File
  outputSource: prokka/out_fsa
- id: prokka_out_tbl
  type: File
  outputSource: prokka/out_tbl
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
- id: fastqc1
  in:
  - id: html_file
    source: fastqc1_html_file
  - id: nogroup
    source: fastqc1_nogroup
  - id: adapters
    source: fastqc1_adapters
  - id: contaminants
    source: fastqc1_contaminants
  - id: limits
    source: fastqc1_limits
  run: tools/fastqc_0_72.cwl
  out:
  - id: out_html_file
  - id: out_text_file
- id: fastqc2
  in:
  - id: html_file
    source: fastqc2_html_file
  - id: nogroup
    source: fastqc2_nogroup
  - id: adapters
    source: fastqc2_adapters
  - id: contaminants
    source: fastqc2_contaminants
  - id: limits
    source: fastqc2_limits
  run: tools/fastqc_0_72.cwl
  out:
  - id: out_html_file
  - id: out_text_file
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
  - id: fastq_input1
    source: in_forward_reads
  - id: fastq_input2
    source: in_reverse_reads
  - id: input_l_file
    source: unicycler_input_l_file
  - id: input_s_fastqsanger
    source: in_forward_reads
  - id: long
    source: in_long_reads
  - id: pilon_path
    source: unicycler_pilon_path
  - id: start_gene_cov
    source: unicycler_start_gene_cov
  - id: start_gene_id
    source: unicycler_start_gene_id
  - id: start_genes
    source: unicycler_start_genes
  run: tools/unicycler_0_4_8_0.cwl
  out:
  - id: out_assembly_graph
  - id: out_assembly
- id: multiqc
  in:
  - id: config
    source: multiqc_config
  run: tools/multiqc_1_7.cwl
  out:
  - id: out_stats
  - id: out_html_report
  - id: out_log
- id: quast
  in:
  - id: circos
    source: quast_circos
  - id: conserved_genes_finding
    source: quast_conserved_genes_finding
  - id: fragmented
    source: quast_fragmented
  - id: large
    source: quast_large
  - id: rna_finding
    source: quast_rna_finding
  - id: skip_unaligned_mis_contigs
    source: quast_skip_unaligned_mis_contigs
  - id: split_scaffolds
    source: quast_split_scaffolds
  - id: strict_na
    source: quast_strict_na
  - id: upper_bound_assembly
    source: quast_upper_bound_assembly
  - id: use_all_alignments
    source: quast_use_all_alignments
  - id: labels
    source: quast_labels
  - id: references_list2
    source: quast_references_list2
  run: tools/quast_5_0_2.cwl
  out:
  - id: out_quast_tabular
  - id: out_report_html
  - id: out_report_pdf
  - id: out_log
  - id: out_mis_ass
  - id: out_unalign
  - id: out_kmers
- id: prokka
  in:
  - id: genus
    source: prokka_genus
  - id: increment
    source: prokka_increment
  - id: locustag
    source: prokka_locustag
  - id: notrna
    source: unicycler/out_assembly
  - id: proteins
    source: prokka_proteins
  - id: species
    source: prokka_species
  - id: strain
    source: prokka_strain
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
id: unicycler_training_imported_from_uploaded_file
