#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_broadgpp_brunello_library_contents_csv
  type: string
- id: in_calabrese_seta_guides_reference_csv
  type: string
- id: in_input_dataset_collection
  type: string
- id: fastqc_nogroup
  doc: None
  type: boolean
  default: false
- id: fastqc_adapters
  doc: |-
    Adapter list. list of adapters adapter sequences which will be explicity searched against the library. tab delimited file with 2 columns: name and sequence.
  type:
  - File
  - 'null'
- id: fastqc_contaminants
  doc: |-
    Contaminant list. tab delimited file with 2 columns: name and sequence.  For example: Illumina Small RNA RT Primer CAAGCAGAAGACGGCATACGA
  type:
  - File
  - 'null'
- id: fastqc_limits
  doc: |-
    Submodule and Limit specifing file. a file that specifies which submodules are to be executed (default=all) and also specifies the thresholds for the each submodules warning parameter
  type:
  - File
  - 'null'
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
- id: fastqc_option_f
  doc: None
  type: string
  default: fastq
- id: fastqc_outdir
  doc: None
  type: string
  default: /tmp/tmpj9z4i9vv/working/dataset_3_files
- id: cutadapt_read2
  type: string
- id: cutadapt_discard_trimmed
  doc: None
  type: boolean
  default: false
- id: cutadapt_discard_untrimmed
  doc: None
  type: boolean
  default: false
- id: cutadapt_match_read_wildcards
  doc: None
  type: boolean
  default: false
- id: cutadapt_no_indels
  doc: None
  type: boolean
  default: false
- id: cutadapt_no_match_adapter_wildcards
  doc: None
  type: boolean
  default: false
- id: cutadapt_revcomp
  doc: None
  type: boolean
  default: false
- id: cutadapt_trim_n
  doc: None
  type: boolean
  default: false
- id: cutadapt_action
  doc: None
  type: string
- id: cutadapt_error_rate
  doc: |-
    Maximum error rate. Maximum allowed error rate (no. of errors divided by the length of the matching region).
  type: float
- id: cutadapt_info_file
  doc: Info File
  type: File
- id: cutadapt_length
  doc: |-
    Length. Shorten reads to this length. This modification is applied after adapter trimming.
  type: int
- id: cutadapt_length_tag
  doc: |-
    Length tag. Search for TAG followed by a decimal number in the name of the read (description/comment field of the FASTA or FASTQ file). Replace the decimal number with the correct length of the trimmed read. For example, use --length-tag 'length=' to search for fields like 'length=123'.
  type:
  - string
  - 'null'
- id: cutadapt_max_expected_errors
  doc: |-
    Max expected errors. Discard reads whose expected number of errors (computed from quality values) exceeds this value.
  type:
  - int
  - 'null'
- id: cutadapt_max_n
  doc: |-
    Max N. Discard reads with more than this number of 'N' bases. A number between 0 and 1 is interpreted as a fraction of the read length.
  type:
  - float
  - 'null'
- id: cutadapt_maximum_length
  doc: |-
    Maximum length (R1). Discard trimmed reads that are longer than LENGTH.  Reads that are too long even before adapter removal are also discarded.
  type:
  - int
  - 'null'
- id: cutadapt_minimum_length
  doc: |-
    Minimum length (R1). Discard trimmed reads that are shorter than LENGTH.  Reads that are too short even before adapter removal are also discarded.
  type:
  - int
  - 'null'
- id: cutadapt_nextseq_trim
  doc: |-
    NextSeq trimming. Experimental option for quality trimming of NextSeq data. This is necessary because that machine cannot distinguish between G and reaching the end of the fragment (it encodes G as ‘black’). This option works like regular quality trimming (where one would use -q 20 instead), except that the qualities of G bases are ignored.
  type: int
- id: cutadapt_option_j
  doc: None
  type: int
- id: cutadapt_option_u1
  doc: |-
    Cut bases from the second read in each pair.. Remove bases from the beginning or end of each read before trimming adapters. If positive, the bases are removed from the beginning of each read. If negative, the bases are removed from the end of each read.
  type:
  - int
  - 'null'
- id: cutadapt_option_u2
  doc: |-
    Cut bases from reads before adapter trimming. Remove bases from each read (first read only if paired). If positive, remove bases from the beginning. If negative, remove bases from the end. This is applied *before* adapter trimming.
  type:
  - int
  - 'null'
- id: cutadapt_output_fastqsanger
  doc: Read 1 Output
  type: File
- id: cutadapt_overlap
  doc: |-
    Minimum overlap length. Minimum overlap length. If the overlap between the adapter and the sequence is shorter than LENGTH, the read is not modified. This reduces the number of bases trimmed purely due to short random adapter matches.
  type: int
- id: cutadapt_pair_filter
  doc: |-
    Pair filter. Which of the reads in a paired-end read have to match the filtering criterion in order for the pair to be filtered. Default: any. possible values: any, both, first
  type:
  - string
  - 'null'
- id: cutadapt_paired_output
  doc: Read 2 Output
  type: File
- id: cutadapt_quality_cutoff
  doc: |-
    Quality cutoff.  Trim low-quality bases from 5' and/or 3' ends of each read before adapter removal. Applied to both reads if data is paired. If one value is given, only the 3' end is trimmed. If two comma-separated cutoffs are given, the 5' end is trimmed with the first cutoff, the 3' end with the second.
  type: string
- id: cutadapt_rename
  doc: |-
    Rename reads. This option can be used to rename both single-end and paired-end reads. 
  type:
  - string
  - 'null'
- id: cutadapt_rest_file
  doc: Rest of Reads (R1 only)
  type: File
- id: cutadapt_times
  doc: |-
    Match times. Try to remove adapters at most COUNT times. Useful when an adapter gets appended multiple times.
  type: int
- id: cutadapt_too_long_output
  doc: Too Long Read 1
  type: File
- id: cutadapt_too_long_paired_output
  doc: Too Long Read 2
  type: File
- id: cutadapt_too_short_output
  doc: Too Short Read 1
  type: File
- id: cutadapt_too_short_paired_output
  doc: Too Short Read 2
  type: File
- id: cutadapt_untrimmed_output
  doc: Untrimmed Read 1
  type: File
- id: cutadapt_untrimmed_paired_output
  doc: Untrimmed Read 2
  type: File
- id: cutadapt_wildcard_file
  doc: Wildcard File
  type: File
- id: cutadapt_zero_cap
  doc: None
  type: string
- id: multiqc_export
  doc: None
  type: boolean
  default: false
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
- id: mageck_count_count_n
  doc: None
  type: boolean
  default: false
- id: mageck_count_reverse_complement
  doc: None
  type: boolean
  default: false
- id: mageck_count_test_run
  doc: None
  type: boolean
  default: false
- id: mageck_count_unmapped_to_file
  doc: None
  type: boolean
  default: false
- id: mageck_count_control_sgrna
  doc: |-
    Control sgRNAs file. A file of control sgRNA IDs for normalization and for generating the null distribution of RRA
  type:
  - File
  - 'null'
- id: mageck_count_gmt_file
  doc: |-
    Pathway file for QC. The pathway file used for QC, in GMT format. By default it will use the GMT file provided by MAGeCK
  type:
  - File
  - 'null'
- id: mageck_count_option_k
  doc: |-
    Counts Table. Alternatively, a tab-separated file of read counts can be used as input. See Help below for format
  type:
  - File
  - 'null'
- id: mageck_count_option_l
  doc: |-
    sgRNA library file. A library file must be provided with three columns containing the sgRNA ID, sequence, and gene it is targeting, see Help below for more information.
  type: File
- id: mageck_count_sample_label
  doc: |-
    Specify sample labels. By default, the input filenames will be used as the sample labels. Optionally you can specify different sample labels to use which must be separated by comma (,). Must be equal to the number of samples provided in --fastq option.
  type: string
  default: ''
- id: mageck_count_sgrna_len
  doc: |-
    Length of the sgRNA. The program will automatically determine the sgRNA length from the library file, so only use this if you turn on the --unmapped-to-file option. Default: autodetected
  type:
  - int
  - 'null'
- id: mageck_count_trim_5
  doc: "5' Trim length. Length of trimming the 5' of the reads. Default: 0"
  type:
  - int
  - 'null'
- id: mageck_count_total
  doc: None
  type: string
  default: total
- id: mageck_count_keep_tmp
  doc: None
  type: boolean
  default: true
- id: mageck_count_pdf_report
  doc: None
  type: boolean
  default: true
- id: mageck_count_norm_method
  doc: |-
    Method for normalization. Methods include: None (no normalization), Median (median normalization), Total (normalization by total read counts), Control (normalization by control sgRNAs specified by the --control-sgrna option). Default: Median. possible values: control, median, none, total
  type: string
  default: median
- id: mageck_count_option_n
  doc: None
  type: string
  default: output
- id: mageck_test_variance_estimation_samples
  doc: None
  type: boolean
  default: false
- id: mageck_test_cell_line
  doc: |-
    Cell line column. Name of the column from the CNV profile file to use. See Help below for more information
  type:
  - string
  - 'null'
- id: mageck_test_cnv_norm
  doc: |-
    CNV profile file. A tab-delimited file containing the CNV status for each gene. See Help below for more information and format.
  type:
  - File
  - 'null'
- id: mageck_test_control_sgrna
  doc: |-
    Control sgRNAs file. A list of control sgRNAs for normalization and for generating the null distribution of RRA
  type:
  - File
  - 'null'
- id: mageck_test_day0_label
  doc: |-
    Control Sample Label. Specify the label for the control sample. For every other sample label, the module will treat it as a treatment condition and compare with control sample (usually day 0 or plasmid)
  type:
  - string
  - 'null'
- id: mageck_test_gene_test_fdr_threshold
  doc: 'Gene test FDR-adjusted Threshold. FDR threshold for gene test. Default: 0.25'
  type:
  - float
  - 'null'
- id: mageck_test_norm_method
  doc: |-
    Method for normalization. If control is specified, the size factor will be estimated using control sgRNAs specified in --control-sgrna option. Default: Median. possible values: control, median, none, total
  type: string
  default: total
- id: mageck_test_option_c
  doc: |-
    Control Sample Labels (or Indexes). If sample label is provided, the labels must match the labels in the first line of the count table, separated by comma (,). Default is all the samples not specified in treatment experiments. See Help below for a detailed description.
  type: string
  default: '1'
- id: mageck_test_option_t
  doc: |-
    Treated Sample Labels (or Indexes). If sample label is provided, the labels must match the labels in the first line of the count table, separated by comma (,); for example, HL60.final,KBM7.final. For sample index, 0,2 means the 1st and 3rd samples are treatment experiments. See Help below for a detailed description.
  type: string
  default: '0'
- id: mageck_test_remove_zero_threshold
  doc: |-
    Remove zero Threshold. sgRNA normalized count threshold to be considered removed in the --remove-zero option. Default: 0
  type:
  - float
  - 'null'
- id: mageck_test_control
  doc: None
  type: string
  default: control
- id: mageck_test_fdr
  doc: None
  type: string
  default: fdr
- id: mageck_test_median1
  doc: None
  type: string
  default: median
- id: mageck_test_median2
  doc: None
  type: string
  default: median
- id: mageck_test_neg
  doc: None
  type: string
  default: neg
- id: mageck_test_normcounts_to_file
  doc: None
  type: boolean
  default: true
- id: mageck_test_pdf_report
  doc: None
  type: boolean
  default: true
- id: mageck_test_adjust_method
  doc: |-
    P-Value Adjustment Method. Method for sgRNA-level p-value adjustment, including False Discovery Rate (FDR), Holm's method (Holm), or Pounds's method (Pounds). Default: FDR. possible values: fdr, holm, pounds
  type: string
  default: fdr
- id: mageck_test_gene_lfc_method
  doc: |-
    Gene Log-Fold Change Method.. Method to calculate gene log fold changes (LFC) from sgRNA LFCs. Available methods include the median/mean of all sgRNAs (median/mean), or the median/mean sgRNAs that are ranked in front of the alpha cutoff in RRA (alphamedian/alphamean), or the sgRNA that has the second strongest LFC (secondbest). In the alphamedian/alphamean case, the number of sgRNAs correspond to the goodsgrna column in the output, and the gene LFC will be set to 0 if no sgRNA is in front of the alpha cutoff. Default: Median. (new since v0.5.5). possible values: alphamean, alphamedian, mean, median, secondbest
  type: string
  default: median
- id: mageck_test_option_n
  doc: None
  type: string
  default: output
- id: mageck_test_remove_zero
  doc: |-
    Remove zero. Remove sgRNAs whose mean value is zero in Control, Treatment, Both control/treatment, or Any control/treatment sample. Default: Both (remove those sgRNAs that are zero in both control and treatment samples). possible values: any, both, control, none, treatment
  type: string
  default: both
- id: mageck_test_sort_criteria
  doc: 'Sorting criteria. possible values: neg, pos'
  type: string
  default: neg

outputs:
- id: fastqc_out_html_file
  type: File
  outputSource: fastqc/out_html_file
- id: fastqc_out_text_file
  type: File
  outputSource: fastqc/out_text_file
- id: cutadapt_out1
  type: File
  outputSource: cutadapt/out1
- id: cutadapt_out_report
  type: File
  outputSource: cutadapt/out_report
- id: multiqc_out_stats
  type: string
  outputSource: multiqc/out_stats
- id: multiqc_out_html_report
  type: File
  outputSource: multiqc/out_html_report
- id: mageck_count_out_counts
  type: File
  outputSource: mageck_count/out_counts
- id: mageck_count_out_countsummary
  type: File
  outputSource: mageck_count/out_countsummary
- id: mageck_count_out_pdfreport
  type: File
  outputSource: mageck_count/out_pdfreport
- id: mageck_test_out_gene_summary
  type: File
  outputSource: mageck_test/out_gene_summary
- id: mageck_test_out_sgrna_summary
  type: File
  outputSource: mageck_test/out_sgrna_summary
- id: mageck_test_out_normcounts
  type: File
  outputSource: mageck_test/out_normcounts
- id: mageck_test_out_plots
  type: File
  outputSource: mageck_test/out_plots

steps:
- id: fastqc
  in:
  - id: input_file
    source: in_input_dataset_collection
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
- id: cutadapt
  in:
  - id: read2
    source: cutadapt_read2
  - id: discard_trimmed
    source: cutadapt_discard_trimmed
  - id: discard_untrimmed
    source: cutadapt_discard_untrimmed
  - id: match_read_wildcards
    source: cutadapt_match_read_wildcards
  - id: no_indels
    source: cutadapt_no_indels
  - id: no_match_adapter_wildcards
    source: cutadapt_no_match_adapter_wildcards
  - id: revcomp
    source: cutadapt_revcomp
  - id: trim_n
    source: cutadapt_trim_n
  - id: action
    source: cutadapt_action
  - id: error_rate
    source: cutadapt_error_rate
  - id: info_file
    source: cutadapt_info_file
  - id: length
    source: cutadapt_length
  - id: length_tag
    source: cutadapt_length_tag
  - id: max_expected_errors
    source: cutadapt_max_expected_errors
  - id: max_n
    source: cutadapt_max_n
  - id: maximum_length
    source: cutadapt_maximum_length
  - id: minimum_length
    source: cutadapt_minimum_length
  - id: nextseq_trim
    source: cutadapt_nextseq_trim
  - id: option_j
    source: cutadapt_option_j
  - id: option_u1
    source: cutadapt_option_u1
  - id: option_u2
    source: cutadapt_option_u2
  - id: output_fastqsanger
    source: cutadapt_output_fastqsanger
  - id: overlap
    source: cutadapt_overlap
  - id: pair_filter
    source: cutadapt_pair_filter
  - id: paired_output
    source: cutadapt_paired_output
  - id: quality_cutoff
    source: cutadapt_quality_cutoff
  - id: rename
    source: cutadapt_rename
  - id: rest_file
    source: cutadapt_rest_file
  - id: times
    source: cutadapt_times
  - id: too_long_output
    source: cutadapt_too_long_output
  - id: too_long_paired_output
    source: cutadapt_too_long_paired_output
  - id: too_short_output
    source: cutadapt_too_short_output
  - id: too_short_paired_output
    source: cutadapt_too_short_paired_output
  - id: untrimmed_output
    source: cutadapt_untrimmed_output
  - id: untrimmed_paired_output
    source: cutadapt_untrimmed_paired_output
  - id: wildcard_file
    source: cutadapt_wildcard_file
  - id: zero_cap
    source: cutadapt_zero_cap
  run: tools/cutadapt_3_4.cwl
  out:
  - id: out_report
  - id: out_info_file
  - id: out_rest_output
  - id: out_wild_output
  - id: out_too_short_output
  - id: out_too_long_output
  - id: out_untrimmed_output
  - id: out1
  - id: out_too_short_paired_output
  - id: out_too_long_paired_output
  - id: out_untrimmed_paired_output
  - id: out2
  - id: out_split_output
  - id: out_pairs
- id: multiqc
  in:
  - id: export
    source: multiqc_export
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
  run: tools/multiqc_1_9.cwl
  out:
  - id: out_stats
  - id: out_plots
  - id: out_html_report
  - id: out_log
- id: mageck_count
  in:
  - id: total
    source: mageck_count_total
  - id: count_n
    source: mageck_count_count_n
  - id: keep_tmp
    source: mageck_count_keep_tmp
  - id: pdf_report
    source: mageck_count_pdf_report
  - id: reverse_complement
    source: mageck_count_reverse_complement
  - id: test_run
    source: mageck_count_test_run
  - id: unmapped_to_file
    source: mageck_count_unmapped_to_file
  - id: control_sgrna
    source: mageck_count_control_sgrna
  - id: fastq
    source: cutadapt/out1
  - id: gmt_file
    source: mageck_count_gmt_file
  - id: norm_method
    source: mageck_count_norm_method
  - id: option_k
    source: mageck_count_option_k
  - id: option_l
    source: mageck_count_option_l
  - id: option_n
    source: mageck_count_option_n
  - id: sample_label
    source: mageck_count_sample_label
  - id: sgrna_len
    source: mageck_count_sgrna_len
  - id: trim_5
    source: mageck_count_trim_5
  run: tools/mageck_count_0_5_9_2_4.cwl
  out:
  - id: out_counts
  - id: out_countsummary
  - id: out_normcounts
  - id: out_unmapped
  - id: out_pdfreport
  - id: out_log
  - id: out_rscript
  - id: out_rnwfile
- id: mageck_test
  in:
  - id: median1
    source: mageck_test_median1
  - id: fdr
    source: mageck_test_fdr
  - id: neg
    source: mageck_test_neg
  - id: control
    source: mageck_test_control
  - id: median2
    source: mageck_test_median2
  - id: normcounts_to_file
    source: mageck_test_normcounts_to_file
  - id: pdf_report
    source: mageck_test_pdf_report
  - id: variance_estimation_samples
    source: mageck_test_variance_estimation_samples
  - id: adjust_method
    source: mageck_test_adjust_method
  - id: cell_line
    source: mageck_test_cell_line
  - id: cnv_norm
    source: mageck_test_cnv_norm
  - id: control_sgrna
    source: mageck_test_control_sgrna
  - id: day0_label
    source: mageck_test_day0_label
  - id: gene_lfc_method
    source: mageck_test_gene_lfc_method
  - id: gene_test_fdr_threshold
    source: mageck_test_gene_test_fdr_threshold
  - id: norm_method
    source: mageck_test_norm_method
  - id: option_c
    source: mageck_test_option_c
  - id: option_k
    source: mageck_count/out_counts
  - id: option_n
    source: mageck_test_option_n
  - id: option_t
    source: mageck_test_option_t
  - id: remove_zero
    source: mageck_test_remove_zero
  - id: remove_zero_threshold
    source: mageck_test_remove_zero_threshold
  - id: sort_criteria
    source: mageck_test_sort_criteria
  run: tools/mageck_test_0_5_9_2_1.cwl
  out:
  - id: out_gene_summary
  - id: out_sgrna_summary
  - id: out_log
  - id: out_normcounts
  - id: out_plots
  - id: out_rscript
  - id: out_rnwfile
id: workflow_constructed_from_history_crispr_tutorial_kenji
