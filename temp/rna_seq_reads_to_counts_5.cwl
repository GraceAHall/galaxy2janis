#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_input_fastqs_collection
  type: string
- id: in_input_reference_gene_bed
  type: string
- id: fastqc1_contaminants
  type: File
- id: fastqc1_limits
  type: File
- id: fastqc1_extract
  doc: None
  type: boolean
  default: true
- id: fastqc1_quiet
  doc: None
  type: boolean
  default: true
- id: fastqc1_option_f
  doc: None
  type: string
  default: fastq
- id: fastqc1_outdir
  doc: None
  type: string
  default: /tmp/tmp6gmk4gl_/working/dataset_4_files
- id: cutadapt_info_file
  doc: |-
    Info File. Write information about each read and its adapter matches to a file.. possible values: false, true
  type: boolean
  default: false
- id: cutadapt_rest_file
  doc: |-
    Rest of Read. When the adapter matches in the middle of a read, write the rest (after the adapter) into a file.. possible values: false, true
  type: boolean
  default: false
- id: cutadapt_too_long_output
  doc: |-
    Too Long Reads. Write reads that are too long (according to maximum length specified) to a file. (default: discard reads). possible values: false, true
  type: boolean
  default: false
- id: cutadapt_too_short_output
  doc: |-
    Too Short Reads. Write reads that are too short (according to minimum length specified) to a file. (default: discard reads). possible values: false, true
  type: boolean
  default: false
- id: cutadapt_untrimmed_output
  doc: |-
    Untrimmed Reads. Write reads that do not contain the adapter to a separate file, instead of writing them to the regular output file.  (default: output to same file as trimmed). possible values: false, true
  type: boolean
  default: false
- id: cutadapt_wildcard_file
  doc: |-
    Wildcard File. When the adapter has wildcard bases ('N's) write adapter bases matching wildcard positions to file.. possible values: false, true
  type: boolean
  default: false
- id: cutadapt_error_rate
  doc: |-
    Maximum error rate. Maximum allowed error rate (no. of errors divided by the length of the matching region).
  type:
  - float
  - 'null'
- id: cutadapt_length
  doc: |-
    Length. Shorten reads to this length. This modification is applied after adapter trimming.
  type:
  - int
  - 'null'
- id: cutadapt_length_tag
  doc: |-
    Length Tag. Search for TAG followed by a decimal number in the name of the read (description/comment field of the FASTA or FASTQ file). Replace the decimal number with the correct length of the trimmed read. For example, use --length-tag 'length=' to search for fields like 'length=123'.
  type:
  - string
  - 'null'
- id: cutadapt_max_n
  doc: |-
    Max N. Discard reads with more than this number of 'N' bases. A number between 0 and 1 is interpreted as a fraction of the read length.
  type:
  - float
  - 'null'
- id: cutadapt_maximum_length
  doc: |-
    Maximum length. Discard trimmed reads that are longer than LENGTH.  Reads that are too long even before adapter removal are also discarded. In colorspace, an initial primer is not counted. Value of 0 means no maximum length.
  type:
  - int
  - 'null'
- id: cutadapt_minimum_length
  doc: |-
    Minimum length. Discard trimmed reads that are shorter than LENGTH.  Reads that are too short even before adapter removal are also discarded. In colorspace, an initial primer is not counted. Value of 0 means no minimum length.
  type:
  - int
  - 'null'
- id: cutadapt_nextseq_trim
  doc: |-
    NextSeq trimming. Experimental option for quality trimming of NextSeq data. This is necessary because that machine cannot distinguish between G and reaching the end of the fragment (it encodes G as ‘black’). This option works like regular quality trimming (where one would use -q 20 instead), except that the qualities of G bases are ignored.
  type:
  - int
  - 'null'
- id: cutadapt_option_u2
  doc: |-
    Cut bases from the second read in each pair.. Remove bases from the beginning or end of each read before trimming adapters. If positive, the bases are removed from the beginning of each read. If negative, the bases are removed from the end of each read.
  type:
  - int
  - 'null'
- id: cutadapt_overlap
  doc: |-
    Minimum overlap length. Minimum overlap length. If the overlap between the adapter and the sequence is shorter than LENGTH, the read is not modified. This reduces the number of bases trimmed purely due to short random adapter matches.
  type:
  - int
  - 'null'
- id: cutadapt_pair_filter
  doc: |-
    Pair filter. Which of the reads in a paired-end read have to match the filtering criterion in order for the pair to be filtered. Default: any. possible values: any, both
  type:
  - string
  - 'null'
- id: cutadapt_prefix
  doc: Prefix. Add this prefix to read names
  type:
  - string
  - 'null'
- id: cutadapt_quality_cutoff
  doc: |-
    Quality cutoff.  Trim low-quality bases from 5' and/or 3' ends of each read before adapter removal. Applied to both reads if data is paired. If one value is given, only the 3' end is trimmed. If two comma-separated cutoffs are given, the 5' end is trimmed with the first cutoff, the 3' end with the second.
  type:
  - string
  - 'null'
- id: cutadapt_suffix
  doc: Suffix. Add this suffix to read names
  type:
  - string
  - 'null'
- id: cutadapt_times
  doc: |-
    Match times. Try to remove adapters at most COUNT times. Useful when an adapter gets appended multiple times.
  type:
  - int
  - 'null'
- id: cutadapt_option_u1
  doc: |-
    Cut bases from reads before adapter trimming. Remove bases from each read (first read only if paired). If positive, remove bases from the beginning. If negative, remove bases from the end. This is applied *before* adapter trimming.
  type: int
  default: 0
- id: fastqc2_contaminants
  type: File
- id: fastqc2_limits
  type: File
- id: fastqc2_extract
  doc: None
  type: boolean
  default: true
- id: fastqc2_quiet
  doc: None
  type: boolean
  default: true
- id: fastqc2_option_f
  doc: None
  type: string
  default: fastq
- id: fastqc2_outdir
  doc: None
  type: string
  default: /tmp/tmpzkpjpyfv/working/dataset_4_files
- id: hisat2_dta
  doc: None
  type: boolean
  default: false
- id: hisat2_dta_cufflinks
  doc: None
  type: boolean
  default: false
- id: hisat2_ff
  doc: None
  type: boolean
  default: false
- id: hisat2_fr
  doc: None
  type: boolean
  default: false
- id: hisat2_ignore_quals
  doc: None
  type: boolean
  default: false
- id: hisat2_int_quals
  doc: None
  type: boolean
  default: false
- id: hisat2_new_summary
  doc: |-
    Output alignment summary in a more machine-friendly style.. Select this option for compatibility with MultiQC. possible values: false, true
  type: boolean
  default: false
- id: hisat2_no_discordant
  doc: None
  type: boolean
  default: false
- id: hisat2_no_mixed
  doc: None
  type: boolean
  default: false
- id: hisat2_no_softclip
  doc: None
  type: boolean
  default: false
- id: hisat2_no_spliced_alignment
  doc: None
  type: boolean
  default: false
- id: hisat2_no_templatelen_adjustment
  doc: None
  type: boolean
  default: false
- id: hisat2_nofw
  doc: None
  type: boolean
  default: false
- id: hisat2_non_deterministic
  doc: None
  type: boolean
  default: false
- id: hisat2_norc
  doc: None
  type: boolean
  default: false
- id: hisat2_phred33
  doc: None
  type: boolean
  default: false
- id: hisat2_phred64
  doc: None
  type: boolean
  default: false
- id: hisat2_rf
  doc: None
  type: boolean
  default: false
- id: hisat2_solexa_quals
  doc: None
  type: boolean
  default: false
- id: hisat2_summary_file
  doc: |-
    Print alignment summary to a file.. Output alignment summary to a file in addition to stderr.. possible values: false, true
  type: boolean
  default: false
- id: hisat2_tmo
  doc: None
  type: boolean
  default: false
- id: hisat2_al
  doc: aligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_al_bz2
  doc: aligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_al_conc
  doc: aligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_al_conc_bz2
  doc: aligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_al_conc_gz
  doc: aligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_al_gz
  doc: aligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_known_splicesite_infile
  doc: None
  type:
  - string
  - 'null'
- id: hisat2_max_intronlen
  doc: Maximum intron length
  type:
  - int
  - 'null'
- id: hisat2_min_intronlen
  doc: Minimum intron length
  type:
  - int
  - 'null'
- id: hisat2_mp
  doc: |-
    Maximum mismatch penalty. Sets the maximum mismatch penalty. A number less than or equal to MX and greater than or equal to MN is subtracted from the alignment score for each position where a read character aligns to a reference character, the characters do not match, and neither is an N. If --ignore-quals is specified, the number subtracted quals MX. Otherwise, the number subtracted is MN + floor( (MX-MN)(MIN(Q, 40.0)/40.0) ) where Q is the Phred quality value
  type:
  - int
  - 'null'
- id: hisat2_n_ceil
  doc: |-
    Function governing the maximum number of ambiguous characters (usually Ns and/or .s) allowed in a read as a function of read length. Reads exceeding this ceiling are filtered out. possible values: C, G, L, S
  type:
  - string
  - 'null'
- id: hisat2_np
  doc: |-
    Ambiguous read penalty. Sets penalty for positions where the read, reference, or both, contain an ambiguous character such as N
  type:
  - int
  - 'null'
- id: hisat2_option_1
  doc: None
  type: string
- id: hisat2_option_2
  doc: None
  type: string
- id: hisat2_option_i
  doc: |-
    Minimum fragment length for valid paired-end alignments. E.g. if -I 60 is specified and a paired-end alignment consists of two 20-bp alignments in the appropriate orientation with a 20-bp gap between them, that alignment is considered valid (as long as -X is also satisfied). A 19-bp gap would not be valid in that case. If trimming options -3 or -5 are also used, the -I constraint is applied with respect to the untrimmed mates. The larger the difference between -I and -X, the slower HISAT2 will run. This is because larger differences between -I and -X require that HISAT2 scan a larger window to determine if a concordant alignment exists. For typical fragment length ranges (200 to 400 nucleotides), HISAT2 is very efficient
  type:
  - int
  - 'null'
- id: hisat2_option_k
  doc: |-
    Primary alignments. Search for at most K distinct, primary alignments for each read. Primary alignments mean alignments whose alignment score is equal or higher than any other alignments. The search terminates when it can't find more distinct valid alignments, or when it finds K, whichever happens first. The alignment score for a paired-end alignment equals the sum of the alignment scores of the individual mates. Each reported read or pair alignment beyond the first has the SAM 'secondary' bit (which equals 256) set in its FLAGS field. For reads that have more than K distinct, valid alignments, HISAT2 does not guarantee that the K alignments reported are the best possible in terms of alignment score. HISAT2 is not designed with large values for -k in mind, so when aligning reads to long repetitive genomes, a large K can be very, very slow. Default: 5 (HFM) or 10 (HGFM)
  type:
  - int
  - 'null'
- id: hisat2_option_s
  doc: 'Skip the first N reads or pairs in the input. default: 0'
  type:
  - int
  - 'null'
- id: hisat2_option_u1
  doc: |-
    Align the first N reads or read pairs from the input (after the first N reads or pairs have been skipped), then stop. default: no limit
  type:
  - int
  - 'null'
- id: hisat2_option_x1
  doc: |-
    Maximum fragment length for valid paired-end alignments. E.g. if -X 100 is specified and a paired-end alignment consists of two 20-bp alignments in the proper orientation with a 60-bp gap between them, that alignment is considered valid (as long as -I is also satisfied). A 61-bp gap would not be valid in that case. If trimming options -3 or -5 are also used, the -X constraint is applied with respect to the untrimmed mates, not the trimmed mates. The larger the difference between -I and -X, the slower HISAT2 will run. This is because larger differences between -I and -X require that HISAT2 scan a larger window to determine if a concordant alignment exists. For typical fragment length ranges (200 to 400 nucleotides), HISAT2 is very efficient
  type:
  - int
  - 'null'
- id: hisat2_pen_canintronlen
  doc: |-
    Penalty function for long introns with canonical splice sites. Alignments with shorter introns are preferred to those with longer ones. possible values: C, G, L, S
  type:
  - string
  - 'null'
- id: hisat2_pen_cansplice
  doc: Penalty for canonical splice sites
  type:
  - int
  - 'null'
- id: hisat2_pen_noncanintronlen
  doc: |-
    Penalty function for long introns with non-canonical splice sites. Alignments with shorter introns are preferred to those with longer ones. possible values: C, G, L, S
  type:
  - string
  - 'null'
- id: hisat2_pen_noncansplice
  doc: Penalty for non-canonical splice sites
  type:
  - int
  - 'null'
- id: hisat2_qupto
  doc: |-
    Align the first N reads or read pairs from the input (after the first N reads or pairs have been skipped), then stop. default: no limit
  type:
  - int
  - 'null'
- id: hisat2_rdg
  doc: |-
    Read gap open penalty. A read gap of length N gets a penalty of [open_penalty] + N * [extend_penalty]
  type:
  - int
  - 'null'
- id: hisat2_rfg
  doc: |-
    Reference gap open penalty. A reference gap of length N gets a penalty of [open_penalty] + N * [extend_penalty]
  type:
  - int
  - 'null'
- id: hisat2_rna_strandness
  doc: |-
    Specify strand information. 'F' means a read corresponds to a transcript. 'R' means a read corresponds to the reverse complemented counterpart of a transcript. With this option being used, every read alignment will have an XS attribute tag: '+' means a read belongs to a transcript on '+' strand of genome. '-' means a read belongs to a transcript on '-' strand of genome.. possible values: , F, R
  type:
  - string
  - 'null'
- id: hisat2_score_min
  doc: |-
    Function governing the minimum alignment score needed for an alignment to be considered 'valid' (i.e. good enough to report). This is a function of read length. possible values: C, G, L, S
  type:
  - string
  - 'null'
- id: hisat2_seed
  doc: Use this number as the seed for pseudo-random number generator. Default=0
  type:
  - int
  - 'null'
- id: hisat2_skip
  doc: 'Skip the first N reads or pairs in the input. default: 0'
  type:
  - int
  - 'null'
- id: hisat2_sp
  doc: |-
    Maximum soft-clipping penalty. Sets the maximum (MX) penalty for soft-clipping per base. A number less than or equal to MX and greater than or equal to MN is subtracted from the alignment score for each position. The number subtracted is MN + floor( (MX-MN)(MIN(Q, 40.0)/40.0) ) where Q is the Phred quality value
  type:
  - int
  - 'null'
- id: hisat2_trim3
  doc: |-
    Trim 3' end. Trim N bases from 3' (right) end of each read before alignment, default: 0
  type:
  - int
  - 'null'
- id: hisat2_trim5
  doc: |-
    Trim 5' end. Trim N bases from 5' (left) end of each read before alignment, default: 0
  type:
  - int
  - 'null'
- id: hisat2_un
  doc: unaligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_un_bz2
  doc: unaligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_un_conc
  doc: unaligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_un_conc_bz2
  doc: unaligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_un_conc_gz
  doc: unaligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_un_gz
  doc: unaligned reads (L)
  type:
  - File
  - 'null'
- id: hisat2_input_f
  doc: None
  type: string
  default: F
- id: hisat2_seq
  doc: None
  type: string
  default: seq
- id: hisat2_flag_f
  doc: None
  type: boolean
  default: true
- id: hisat2_option_p
  doc: None
  type: int
  default: 1
- id: hisat2_option_u2
  doc: None
  type:
  - string
  - 'null'
- id: hisat2_option_x2
  doc: None
  type: string
  default: genome
- id: featurecounts_byreadgroup
  doc: None
  type: boolean
  default: false
- id: featurecounts_flag_b
  doc: None
  type: boolean
  default: false
- id: featurecounts_flag_f
  doc: |-
    On feature level. If specified, read summarization will be performed at the feature level. By default (-f is not specified), the read summarization is performed at the meta-feature level.. possible values:  -f
  type: boolean
  default: false
- id: featurecounts_flag_j
  doc: |-
    Exon-exon junctions. If specified, reads supporting each exon-exon junction will be counted. possible values: -J
  type: boolean
  default: false
- id: featurecounts_flag_l
  doc: None
  type: boolean
  default: false
- id: featurecounts_flag_o
  doc: None
  type: boolean
  default: false
- id: featurecounts_flag_p
  doc: |-
    Check paired-end distance. If specified, paired-end distance will be checked when assigning fragments to meta-features or features. This option is only applicable when -p (Count fragments instead of reads) is specified. The distance thresholds should be specified using -d and -D (minimum and maximum fragment/template length) options.. possible values:  -P
  type: boolean
  default: false
- id: featurecounts_flag_r
  doc: None
  type: boolean
  default: false
- id: featurecounts_fraction
  doc: None
  type: boolean
  default: false
- id: featurecounts_ignoredup
  doc: None
  type: boolean
  default: false
- id: featurecounts_largestoverlap
  doc: None
  type: boolean
  default: false
- id: featurecounts_primary
  doc: None
  type: boolean
  default: false
- id: featurecounts_read2pos
  doc: None
  type: boolean
  default: false
- id: featurecounts_option_a
  doc: |-
    Gene annotation file. The program assumes that the provided annotation file is in GTF format. Make sure that the gene annotation file corresponds to the same reference genome as used for the alignment
  type: File
- id: featurecounts_option_c
  doc: |-
    Alignment file. The input alignment file(s) where the gene expression has to be counted. The file can have a SAM or BAM format; but ALL files must be in the same format. Unless you are using a Gene annotation file from the History, these files must have the database/genome attribute already specified e.g. hg38, not the default: ?
  type: File
- id: featurecounts_option_d1
  doc: Minimum fragment/template length.
  type: int
- id: featurecounts_option_d2
  doc: Maximum fragment/template length.
  type: int
- id: featurecounts_option_f
  doc: None
  type: string
  default: SAF
- id: featurecounts_option_g2
  doc: |-
    Reference sequence file. The FASTA-format file that contains the reference sequences used in read mapping can be used to improve read counting for junctions
  type:
  - File
  - 'null'
- id: featurecounts_option_m
  doc: |-
    Count multi-mapping reads/fragments. If specified, multi-mapping reads/fragments will be counted (ie. a multi-mapping read will be counted up to N times if it has N reported mapping locations). The program uses the `NH' tag to find multi-mapping reads.. possible values: ,  -M
  type:
  - string
  - 'null'
- id: featurecounts_option_p
  doc: |-
    Count fragments instead of reads. If specified, fragments (or templates) will be counted instead of reads.. possible values: ,  -p
  type:
  - string
  - 'null'
- id: featurecounts_readextension3
  doc: Read 3' extension. Reads are extended upstream by ... bases from their 3' end
  type: int
- id: featurecounts_readextension5
  doc: Read 5' extension. Reads are extended upstream by ... bases from their 5' end
  type: int
- id: featurecounts_fracoverlap
  doc: |-
    Minimum fraction (of read) overlapping a feature. Specify the minimum required fraction of overlapping bases between a read (or a fragment) and a feature. Value should be within range [0,1]. 0 by default. Number of overlapping bases is counted from both reads if paired end. Both this option and '--minOverlap' need to be satisfied for read assignment.
  type: int
  default: 0
- id: featurecounts_fracoverlapfeature
  doc: |-
    Minimum fraction (of feature) overlapping a read. Specify the minimum required fraction of bases included in a feature overlapping bases between a read (or a read-pair). Value should be within range [0,1]. 0 by default.
  type: int
  default: 0
- id: featurecounts_minoverlap
  doc: |-
    Minimum bases of overlap. Specify the minimum required number of overlapping bases between a read (or a fragment) and a feature. 1 by default. If a negative value is provided, the read will be extended from both ends.
  type: int
  default: 1
- id: featurecounts_option_g1
  doc: |-
    GFF gene identifier. Specify the attribute type used to group features (eg. exons) into meta-features (eg. genes), when GTF annotation is provided. `gene_id' by default. This attribute type is usually the gene identifier. This argument is useful for the meta-feature level summarization.
  type: string
  default: gene_id
- id: featurecounts_option_o
  doc: None
  type: string
  default: output
- id: featurecounts_option_q
  doc: |-
    Minimum mapping quality per read. The minimum mapping quality score a read must satisfy in order to be counted. For paired-end reads, at least one end should satisfy this criteria. 12 by default.
  type: int
  default: 12
- id: featurecounts_option_s
  doc: |-
    Specify strand information. Indicate if the data is stranded and if strand-specific read counting should be performed. Strand setting must be the same as the strand settings used to produce the mapped BAM input(s). possible values: 0, 1, 2
  type: string
  default: '0'
- id: featurecounts_option_t1
  doc: |-
    GFF feature type filter. Specify the feature type. Only rows which have the matched matched feature type in the provided GTF annotation file will be included for read counting. `exon' by default.
  type: string
  default: exon
- id: featurecounts_option_t2
  doc: None
  type: int
  default: 2
- id: picard_markduplicates_assume_sorted
  doc: None
  type: string
- id: picard_markduplicates_barcode_tag
  doc: |-
    Barcode Tag. Barcode SAM tag. This tag can be utilized when you have data from an assay that includes Unique Molecular Indices.
  type:
  - string
  - 'null'
- id: picard_markduplicates_duplicate_scoring_strategy
  doc: None
  type: string
- id: picard_markduplicates_input_bam
  doc: |-
    Select SAM/BAM dataset or dataset collection. If empty, upload or import a SAM/BAM dataset
  type: File
- id: picard_markduplicates_metrics_file
  doc: MarkDuplicate metrics
  type: File
- id: picard_markduplicates_optical_duplicate_pixel_distance
  doc: |-
    The maximum offset between two duplicte clusters in order to consider them optical duplicates. OPTICAL_DUPLICATE_PIXEL_DISTANCE; default=100
  type: int
- id: picard_markduplicates_output_bam
  doc: MarkDuplicates BAM output
  type: File
- id: picard_markduplicates_quiet
  doc: None
  type: string
- id: picard_markduplicates_remove_duplicates
  doc: None
  type: string
- id: picard_markduplicates_validation_stringency
  doc: None
  type: string
- id: picard_markduplicates_verbosity
  doc: None
  type: string
- id: picard_markduplicates_arguments
  doc: None
  type: string
  default: arguments
- id: picard_markduplicates_optional
  doc: None
  type: string
  default: Optional
- id: picard_markduplicates_positional1
  doc: None
  type: string
- id: picard_markduplicates_positional2
  doc: None
  type: string
- id: rseqc_genebody_coverage_minimum_length
  doc: |-
    Minimum mRNA length (default: 100). Minimum mRNA length in bp, mRNA that are shorter than this value will be skipped (--minimum_length).
  type: int
  default: 100
- id: rseqc_genebody_coverage_option_i
  doc: None
  type: string
- id: rseqc_genebody_coverage_option_o
  doc: None
  type: string
  default: output
- id: rseqc_infer_experiment_mapq
  doc: |-
    Minimum mapping quality. Minimum mapping quality for an alignment to be considered as 'uniquely mapped' (--mapq)
  type: int
  default: 30
- id: rseqc_infer_experiment_sample_size
  doc: Number of reads sampled from SAM/BAM file (default = 200000). (--sample-size)
  type: int
  default: 200000
- id: collection_column_join_collection_column_join_script
  type: string
- id: multiqc_comment
  doc: Custom comment. It will be printed at the top of the report
  type:
  - string
  - 'null'
- id: multiqc_title
  doc: Report title. It is printed as page header
  type: string
  default: Tutorial
- id: multiqc_config
  doc: None
  type: string
- id: multiqc_filename
  doc: None
  type: string
  default: report

outputs:
- id: fastqc1_out_html_file
  type: File
  outputSource: fastqc1/out_html_file
- id: fastqc1_out_text_file
  type: File
  outputSource: fastqc1/out_text_file
- id: cutadapt_out1
  type: File
  outputSource: cutadapt/out1
- id: cutadapt_out2
  type: File
  outputSource: cutadapt/out2
- id: cutadapt_out_report
  type: File
  outputSource: cutadapt/out_report
- id: cutadapt_out_info_file
  type: File
  outputSource: cutadapt/out_info_file
- id: cutadapt_out_rest_output
  type: File
  outputSource: cutadapt/out_rest_output
- id: cutadapt_out_wild_output
  type: File
  outputSource: cutadapt/out_wild_output
- id: cutadapt_out_untrimmed_output
  type: File
  outputSource: cutadapt/out_untrimmed_output
- id: cutadapt_out_untrimmed_paired_output
  type: File
  outputSource: cutadapt/out_untrimmed_paired_output
- id: cutadapt_out_too_short_output
  type: File
  outputSource: cutadapt/out_too_short_output
- id: cutadapt_out_too_short_paired_output
  type: File
  outputSource: cutadapt/out_too_short_paired_output
- id: cutadapt_out_too_long_output
  type: File
  outputSource: cutadapt/out_too_long_output
- id: cutadapt_out_too_long_paired_output
  type: File
  outputSource: cutadapt/out_too_long_paired_output
- id: fastqc2_out_html_file
  type: File
  outputSource: fastqc2/out_html_file
- id: fastqc2_out_text_file
  type: File
  outputSource: fastqc2/out_text_file
- id: hisat2_output_alignments
  type: File
  outputSource: hisat2/output_alignments
- id: hisat2_output_unaligned_reads_l1
  type: File
  outputSource: hisat2/output_unaligned_reads_l1
- id: hisat2_output_aligned_reads_l1
  type: File
  outputSource: hisat2/output_aligned_reads_l1
- id: hisat2_output_unaligned_reads_r
  type: File
  outputSource: hisat2/output_unaligned_reads_r
- id: hisat2_output_aligned_reads_r
  type: File
  outputSource: hisat2/output_aligned_reads_r
- id: hisat2_out_summary_file
  type: File
  outputSource: hisat2/out_summary_file
- id: featurecounts_output_medium
  type: File
  outputSource: featurecounts/output_medium
- id: featurecounts_output_bam
  type: File
  outputSource: featurecounts/output_bam
- id: featurecounts_output_short
  type: File
  outputSource: featurecounts/output_short
- id: featurecounts_output_full
  type: File
  outputSource: featurecounts/output_full
- id: featurecounts_output_summary
  type: File
  outputSource: featurecounts/output_summary
- id: featurecounts_output_feature_lengths
  type: File
  outputSource: featurecounts/output_feature_lengths
- id: featurecounts_output_jcounts
  type: File
  outputSource: featurecounts/output_jcounts
- id: picard_markduplicates_out_metrics_file
  type: File
  outputSource: picard_markduplicates/out_metrics_file
- id: picard_markduplicates_outfile
  type: File
  outputSource: picard_markduplicates/outfile
- id: samtools_idxstats_output_tabular
  type: File
  outputSource: samtools_idxstats/output_tabular
- id: rseqc_genebody_coverage_outputcurvespdf
  type: File
  outputSource: rseqc_genebody_coverage/outputcurvespdf
- id: rseqc_genebody_coverage_outputheatmappdf
  type: File
  outputSource: rseqc_genebody_coverage/outputheatmappdf
- id: rseqc_genebody_coverage_outputr
  type: File
  outputSource: rseqc_genebody_coverage/outputr
- id: rseqc_genebody_coverage_outputtxt
  type: File
  outputSource: rseqc_genebody_coverage/outputtxt
- id: rseqc_infer_experiment_output_textfile
  type: File
  outputSource: rseqc_infer_experiment/output_textfile
- id: rseqc_read_distribution_output_textfile
  type: File
  outputSource: rseqc_read_distribution/output_textfile
- id: collection_column_join_out_tabular_output
  type: File
  outputSource: collection_column_join/out_tabular_output
- id: collection_column_join_out_script_output
  type: File
  outputSource: collection_column_join/out_script_output
- id: multiqc_out_stats
  type: string
  outputSource: multiqc/out_stats
- id: multiqc_out_html_report
  type: File
  outputSource: multiqc/out_html_report
- id: multiqc_out_log
  type: File
  outputSource: multiqc/out_log

steps:
- id: fastqc1
  in:
  - id: input_file
    source: in_input_fastqs_collection
  - id: extract
    source: fastqc1_extract
  - id: quiet
    source: fastqc1_quiet
  - id: contaminants
    source: fastqc1_contaminants
  - id: limits
    source: fastqc1_limits
  - id: option_f
    source: fastqc1_option_f
  - id: outdir
    source: fastqc1_outdir
  run: tools/fastqc_0_72.cwl
  out:
  - id: out_html_file
  - id: out_text_file
- id: cutadapt
  in:
  - id: info_file
    source: cutadapt_info_file
  - id: rest_file
    source: cutadapt_rest_file
  - id: too_long_output
    source: cutadapt_too_long_output
  - id: too_short_output
    source: cutadapt_too_short_output
  - id: untrimmed_output
    source: cutadapt_untrimmed_output
  - id: wildcard_file
    source: cutadapt_wildcard_file
  - id: error_rate
    source: cutadapt_error_rate
  - id: length
    source: cutadapt_length
  - id: length_tag
    source: cutadapt_length_tag
  - id: max_n
    source: cutadapt_max_n
  - id: maximum_length
    source: cutadapt_maximum_length
  - id: minimum_length
    source: cutadapt_minimum_length
  - id: nextseq_trim
    source: cutadapt_nextseq_trim
  - id: option_u1
    source: cutadapt_option_u1
  - id: option_u2
    source: cutadapt_option_u2
  - id: overlap
    source: cutadapt_overlap
  - id: pair_filter
    source: cutadapt_pair_filter
  - id: prefix
    source: cutadapt_prefix
  - id: quality_cutoff
    source: cutadapt_quality_cutoff
  - id: suffix
    source: cutadapt_suffix
  - id: times
    source: cutadapt_times
  run: tools/cutadapt_1_16_3.cwl
  out:
  - id: out_report
  - id: out1
  - id: out2
  - id: out_info_file
  - id: out_rest_output
  - id: out_wild_output
  - id: out_untrimmed_output
  - id: out_untrimmed_paired_output
  - id: out_too_short_output
  - id: out_too_short_paired_output
  - id: out_too_long_output
  - id: out_too_long_paired_output
- id: fastqc2
  in:
  - id: input_file
    source: cutadapt/out1
  - id: extract
    source: fastqc2_extract
  - id: quiet
    source: fastqc2_quiet
  - id: contaminants
    source: fastqc2_contaminants
  - id: limits
    source: fastqc2_limits
  - id: option_f
    source: fastqc2_option_f
  - id: outdir
    source: fastqc2_outdir
  run: tools/fastqc_0_72.cwl
  out:
  - id: out_html_file
  - id: out_text_file
- id: hisat2
  in:
  - id: input_f
    source: hisat2_input_f
  - id: seq
    source: hisat2_seq
  - id: dta
    source: hisat2_dta
  - id: dta_cufflinks
    source: hisat2_dta_cufflinks
  - id: ff
    source: hisat2_ff
  - id: flag_f
    source: hisat2_flag_f
  - id: fr
    source: hisat2_fr
  - id: ignore_quals
    source: hisat2_ignore_quals
  - id: int_quals
    source: hisat2_int_quals
  - id: new_summary
    source: hisat2_new_summary
  - id: no_discordant
    source: hisat2_no_discordant
  - id: no_mixed
    source: hisat2_no_mixed
  - id: no_softclip
    source: hisat2_no_softclip
  - id: no_spliced_alignment
    source: hisat2_no_spliced_alignment
  - id: no_templatelen_adjustment
    source: hisat2_no_templatelen_adjustment
  - id: nofw
    source: hisat2_nofw
  - id: non_deterministic
    source: hisat2_non_deterministic
  - id: norc
    source: hisat2_norc
  - id: phred33
    source: hisat2_phred33
  - id: phred64
    source: hisat2_phred64
  - id: rf
    source: hisat2_rf
  - id: solexa_quals
    source: hisat2_solexa_quals
  - id: summary_file
    source: hisat2_summary_file
  - id: tmo
    source: hisat2_tmo
  - id: al
    source: hisat2_al
  - id: al_bz2
    source: hisat2_al_bz2
  - id: al_conc
    source: hisat2_al_conc
  - id: al_conc_bz2
    source: hisat2_al_conc_bz2
  - id: al_conc_gz
    source: hisat2_al_conc_gz
  - id: al_gz
    source: hisat2_al_gz
  - id: known_splicesite_infile
    source: hisat2_known_splicesite_infile
  - id: max_intronlen
    source: hisat2_max_intronlen
  - id: min_intronlen
    source: hisat2_min_intronlen
  - id: mp
    source: hisat2_mp
  - id: n_ceil
    source: hisat2_n_ceil
  - id: np
    source: hisat2_np
  - id: option_1
    source: hisat2_option_1
  - id: option_2
    source: hisat2_option_2
  - id: option_i
    source: hisat2_option_i
  - id: option_k
    source: hisat2_option_k
  - id: option_p
    source: hisat2_option_p
  - id: option_s
    source: hisat2_option_s
  - id: option_u1
    source: hisat2_option_u1
  - id: option_u2
    source: hisat2_option_u2
  - id: option_x1
    source: hisat2_option_x1
  - id: option_x2
    source: hisat2_option_x2
  - id: pen_canintronlen
    source: hisat2_pen_canintronlen
  - id: pen_cansplice
    source: hisat2_pen_cansplice
  - id: pen_noncanintronlen
    source: hisat2_pen_noncanintronlen
  - id: pen_noncansplice
    source: hisat2_pen_noncansplice
  - id: qupto
    source: hisat2_qupto
  - id: rdg
    source: hisat2_rdg
  - id: rfg
    source: hisat2_rfg
  - id: rna_strandness
    source: hisat2_rna_strandness
  - id: score_min
    source: hisat2_score_min
  - id: seed
    source: hisat2_seed
  - id: skip
    source: hisat2_skip
  - id: sp
    source: hisat2_sp
  - id: trim3
    source: hisat2_trim3
  - id: trim5
    source: hisat2_trim5
  - id: un
    source: hisat2_un
  - id: un_bz2
    source: hisat2_un_bz2
  - id: un_conc
    source: hisat2_un_conc
  - id: un_conc_bz2
    source: hisat2_un_conc_bz2
  - id: un_conc_gz
    source: hisat2_un_conc_gz
  - id: un_gz
    source: hisat2_un_gz
  run: tools/hisat2_2_1_0.cwl
  out:
  - id: output_unaligned_reads_l1
  - id: output_unaligned_reads_l2
  - id: output_unaligned_reads_l3
  - id: output_aligned_reads_l1
  - id: output_aligned_reads_l2
  - id: output_aligned_reads_l3
  - id: output_unaligned_reads_l4
  - id: output_unaligned_reads_l5
  - id: output_unaligned_reads_l6
  - id: output_aligned_reads_l4
  - id: output_aligned_reads_l5
  - id: output_aligned_reads_l6
  - id: output_alignments
  - id: output_unaligned_reads_r
  - id: output_aligned_reads_r
  - id: out_summary_file
- id: featurecounts
  in:
  - id: byreadgroup
    source: featurecounts_byreadgroup
  - id: flag_b
    source: featurecounts_flag_b
  - id: flag_f
    source: featurecounts_flag_f
  - id: flag_j
    source: featurecounts_flag_j
  - id: flag_l
    source: featurecounts_flag_l
  - id: flag_o
    source: featurecounts_flag_o
  - id: flag_p
    source: featurecounts_flag_p
  - id: flag_r
    source: featurecounts_flag_r
  - id: fraction
    source: featurecounts_fraction
  - id: ignoredup
    source: featurecounts_ignoredup
  - id: largestoverlap
    source: featurecounts_largestoverlap
  - id: primary
    source: featurecounts_primary
  - id: read2pos
    source: featurecounts_read2pos
  - id: fracoverlap
    source: featurecounts_fracoverlap
  - id: fracoverlapfeature
    source: featurecounts_fracoverlapfeature
  - id: minoverlap
    source: featurecounts_minoverlap
  - id: option_a
    source: featurecounts_option_a
  - id: option_c
    source: featurecounts_option_c
  - id: option_d1
    source: featurecounts_option_d1
  - id: option_d2
    source: featurecounts_option_d2
  - id: option_f
    source: featurecounts_option_f
  - id: option_g1
    source: featurecounts_option_g1
  - id: option_g2
    source: featurecounts_option_g2
  - id: option_m
    source: featurecounts_option_m
  - id: option_o
    source: featurecounts_option_o
  - id: option_p
    source: featurecounts_option_p
  - id: option_q
    source: featurecounts_option_q
  - id: option_s
    source: featurecounts_option_s
  - id: option_t1
    source: featurecounts_option_t1
  - id: option_t2
    source: featurecounts_option_t2
  - id: readextension3
    source: featurecounts_readextension3
  - id: readextension5
    source: featurecounts_readextension5
  run: tools/featurecounts_1_6_3.cwl
  out:
  - id: output_medium
  - id: output_bam
  - id: output_short
  - id: output_full
  - id: output_summary
  - id: output_feature_lengths
  - id: output_jcounts
- id: picard_markduplicates
  in:
  - id: positional1
    source: picard_markduplicates_positional1
  - id: positional2
    source: picard_markduplicates_positional2
  - id: optional
    source: picard_markduplicates_optional
  - id: arguments
    source: picard_markduplicates_arguments
  - id: assume_sorted
    source: picard_markduplicates_assume_sorted
  - id: barcode_tag
    source: picard_markduplicates_barcode_tag
  - id: duplicate_scoring_strategy
    source: picard_markduplicates_duplicate_scoring_strategy
  - id: input_bam
    source: picard_markduplicates_input_bam
  - id: metrics_file
    source: picard_markduplicates_metrics_file
  - id: optical_duplicate_pixel_distance
    source: picard_markduplicates_optical_duplicate_pixel_distance
  - id: output_bam
    source: picard_markduplicates_output_bam
  - id: quiet
    source: picard_markduplicates_quiet
  - id: remove_duplicates
    source: picard_markduplicates_remove_duplicates
  - id: validation_stringency
    source: picard_markduplicates_validation_stringency
  - id: verbosity
    source: picard_markduplicates_verbosity
  run: tools/picard_MarkDuplicates_2_18_2_1.cwl
  out:
  - id: outfile
  - id: out_metrics_file
- id: samtools_idxstats
  in:
  - id: input_bam
    source: hisat2/output_alignments
  run: tools/samtools_idxstats_2_0_2.cwl
  out:
  - id: output_tabular
- id: rseqc_genebody_coverage
  in:
  - id: minimum_length
    source: rseqc_genebody_coverage_minimum_length
  - id: option_i
    source: rseqc_genebody_coverage_option_i
  - id: option_o
    source: rseqc_genebody_coverage_option_o
  - id: option_r
    source: in_input_reference_gene_bed
  run: tools/rseqc_geneBody_coverage_2_6_4_3.cwl
  out:
  - id: outputcurvespdf
  - id: outputheatmappdf
  - id: outputr
  - id: outputtxt
- id: rseqc_infer_experiment
  in:
  - id: mapq
    source: rseqc_infer_experiment_mapq
  - id: option_i
    source: hisat2/output_alignments
  - id: option_r
    source: in_input_reference_gene_bed
  - id: sample_size
    source: rseqc_infer_experiment_sample_size
  run: tools/rseqc_infer_experiment_2_6_4_1.cwl
  out:
  - id: output_textfile
- id: rseqc_read_distribution
  in:
  - id: option_i
    source: hisat2/output_alignments
  - id: option_r
    source: in_input_reference_gene_bed
  run: tools/rseqc_read_distribution_2_6_4_1.cwl
  out:
  - id: output_textfile
- id: collection_column_join
  in:
  - id: collection_column_join_script
    source: collection_column_join_collection_column_join_script
  run: tools/collection_column_join_0_0_3.cwl
  out:
  - id: out_tabular_output
  - id: out_script_output
- id: multiqc
  in:
  - id: comment
    source: multiqc_comment
  - id: config
    source: multiqc_config
  - id: filename
    source: multiqc_filename
  - id: title
    source: multiqc_title
  run: tools/multiqc_1_6.cwl
  out:
  - id: out_stats
  - id: out_html_report
  - id: out_log
id: rna_seq_reads_to_counts
