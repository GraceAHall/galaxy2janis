#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_long_reads
  type: File
- id: filtlong_assembly
  type: File
- id: filtlong_illumina_1
  type: File
- id: filtlong_illumina_2
  type: File
- id: filtlong_trim
  doc: None
  type: boolean
  default: false
- id: filtlong_keep_percent
  doc: Keep percentage. Keep only this percentage of the best reads (measured by bases)
  type:
  - float
  - 'null'
- id: filtlong_length_weight
  doc: 'Weight length score. Weight given to the length score (default: 1)'
  type: float
  default: 1.0
- id: filtlong_max_length
  doc: Max. length. Maximum length threshold
  type:
  - int
  - 'null'
- id: filtlong_mean_q_weight
  doc: 'Weight mean quality. Weight given to the mean quality score (default: 1)'
  type: float
  default: 1.0
- id: filtlong_min_length
  doc: Min. length. Minimum length threshold
  type: int
  default: 500
- id: filtlong_min_mean_q
  doc: Min. mean quality. Minimum mean quality threshold
  type: float
  default: 8.0
- id: filtlong_min_window_q
  doc: Min. window quality. Minimum window quality threshold
  type:
  - float
  - 'null'
- id: filtlong_split
  doc: |-
    Split at nr. of bases. split reads at this many (or more) consecutive non-k-mer-matching bases
  type:
  - int
  - 'null'
- id: filtlong_target_bases
  doc: Total bases. Keep only the best reads up to this many total bases
  type:
  - int
  - 'null'
- id: filtlong_window_q_weight
  doc: 'Weight window quality. Weight given to the window quality score (default:
    1)'
  type: float
  default: 1.0
- id: filtlong_window_size
  doc: |-
    Sliding window size. size of sliding window used when measuring window quality (default: 250)
  type: int
  default: 250
- id: nanoplot_alength
  doc: None
  type: boolean
  default: false
- id: nanoplot_barcoded
  doc: None
  type: boolean
  default: false
- id: nanoplot_drop_outliers
  doc: None
  type: boolean
  default: false
- id: nanoplot_loglength
  doc: None
  type: boolean
  default: false
- id: nanoplot_n50
  doc: None
  type: boolean
  default: false
- id: nanoplot_percentqual
  doc: None
  type: boolean
  default: false
- id: nanoplot_bam
  doc: None
  type:
  - string
  - 'null'
- id: nanoplot_color
  doc: |-
    Specify a color for the plots.. possible values: aliceblue, antiquewhite, aqua, aquamarine, azure
  type:
  - string
  - 'null'
- id: nanoplot_downsample
  doc: Reduce dataset to N reads by random sampling.
  type:
  - int
  - 'null'
- id: nanoplot_fasta
  doc: None
  type:
  - string
  - 'null'
- id: nanoplot_fastq_rich
  doc: None
  type:
  - string
  - 'null'
- id: nanoplot_maxlength
  doc: Drop reads longer than length specified.
  type:
  - int
  - 'null'
- id: nanoplot_minlength
  doc: Drop reads shorter than length specified.
  type:
  - int
  - 'null'
- id: nanoplot_minqual
  doc: Drop reads with an average quality lower than specified.
  type:
  - int
  - 'null'
- id: nanoplot_plots
  doc: |-
    Specify the bivariate format of the plots.. possible values: dot, hex, kde, pauvre
  type:
  - type: array
    items: string
  - 'null'
- id: nanoplot_readtype
  doc: |-
    Which read type to extract information about from summary.. possible values: 1D, 1D2, 2D
  type:
  - string
  - 'null'
- id: nanoplot_threads
  doc: None
  type: string
  default: '4'
- id: nanoplot_aliceblue
  doc: None
  type: string
  default: aliceblue
- id: nanoplot_input_1d
  doc: None
  type: string
  default: 1D
- id: nanoplot_png
  doc: None
  type: string
  default: png
- id: nanoplot_format
  doc: 'Specify the output format of the plots.. possible values: png, svg'
  type: string
  default: png
- id: nanoplot_option_o
  doc: None
  type: string
  default: .
- id: kraken2_quick
  doc: None
  type: boolean
  default: false
- id: kraken2_report_minimizer_data
  doc: None
  type: boolean
  default: false
- id: kraken2_report_zero_counts
  doc: None
  type: boolean
  default: false
- id: kraken2_use_mpa_style
  doc: None
  type: boolean
  default: false
- id: kraken2_use_names
  doc: None
  type: boolean
  default: false
- id: kraken2_classified_out
  doc: Classified reads
  type: File
- id: kraken2_paired
  doc: Reverse strand
  type: File
- id: kraken2_report
  doc: None
  type: File
- id: kraken2_unclassified_out
  doc: Unclassified reads
  type: File
- id: kraken2_confidence
  doc: Confidence. Confidence score threshold. Must be in [0, 1]
  type: float
  default: 0.0
- id: kraken2_db
  doc: None
  type: string
- id: kraken2_minimum_base_quality
  doc: |-
    Minimum Base Quality. Minimum base quality used in classification (only effective with FASTQ input)
  type: int
  default: 0
- id: kraken2_minimum_hit_groups
  doc: |-
    Minimum hit goups. Number of overlapping k-mers sharing the same minimizer needed to make a call
  type: int
  default: 2
- id: kraken2_threads
  doc: None
  type: int
  default: 1
- id: kraken2tax_ncbi_taxonomy_fields_path1
  type: string
- id: kraken2tax_ncbi_taxonomy_fields_path2
  type: string
- id: kraken2tax_positional_3
  doc: None
  type: int
  default: 1
- id: taxonomy_krona_chart_flag_c
  doc: None
  type: boolean
  default: false
- id: taxonomy_krona_chart_ktimporttext
  doc: None
  type: string
  default: ktImportText
- id: taxonomy_krona_chart_positional_1
  doc: None
  type: int
  default: 0
- id: taxonomy_krona_chart_option_n
  doc: Provide a name for the basal rank. -n; Otherwise it will simply be called 'Root'
  type: string
  default: Root
- id: taxonomy_krona_chart_option_o
  doc: HTML
  type: File

outputs:
- id: filtlong_outfile
  type: File
  outputSource: filtlong/outfile
- id: nanoplot_output_html
  type: File
  outputSource: nanoplot/output_html
- id: kraken2_output_tabular
  type: File
  outputSource: kraken2/output_tabular
- id: kraken2tax_out_file
  type: File
  outputSource: kraken2tax/out_file
- id: taxonomy_krona_chart_output_html
  type: File
  outputSource: taxonomy_krona_chart/output_html

steps:
- id: filtlong
  in:
  - id: input_file
    source: in_long_reads
  - id: trim
    source: filtlong_trim
  - id: assembly
    source: filtlong_assembly
  - id: illumina_1
    source: filtlong_illumina_1
  - id: illumina_2
    source: filtlong_illumina_2
  - id: keep_percent
    source: filtlong_keep_percent
  - id: length_weight
    source: filtlong_length_weight
  - id: max_length
    source: filtlong_max_length
  - id: mean_q_weight
    source: filtlong_mean_q_weight
  - id: min_length
    source: filtlong_min_length
  - id: min_mean_q
    source: filtlong_min_mean_q
  - id: min_window_q
    source: filtlong_min_window_q
  - id: split
    source: filtlong_split
  - id: target_bases
    source: filtlong_target_bases
  - id: window_q_weight
    source: filtlong_window_q_weight
  - id: window_size
    source: filtlong_window_size
  run: tools/filtlong_0_2_1.cwl
  out:
  - id: outfile
- id: nanoplot
  in:
  - id: input_1d
    source: nanoplot_input_1d
  - id: aliceblue
    source: nanoplot_aliceblue
  - id: png
    source: nanoplot_png
  - id: alength
    source: nanoplot_alength
  - id: barcoded
    source: nanoplot_barcoded
  - id: drop_outliers
    source: nanoplot_drop_outliers
  - id: loglength
    source: nanoplot_loglength
  - id: n50
    source: nanoplot_n50
  - id: percentqual
    source: nanoplot_percentqual
  - id: bam
    source: nanoplot_bam
  - id: color
    source: nanoplot_color
  - id: downsample
    source: nanoplot_downsample
  - id: fasta
    source: nanoplot_fasta
  - id: fastq_rich
    source: nanoplot_fastq_rich
  - id: format
    source: nanoplot_format
  - id: maxlength
    source: nanoplot_maxlength
  - id: minlength
    source: nanoplot_minlength
  - id: minqual
    source: nanoplot_minqual
  - id: option_o
    source: nanoplot_option_o
  - id: plots
    source: nanoplot_plots
  - id: readtype
    source: nanoplot_readtype
  - id: threads
    source: nanoplot_threads
  run: tools/nanoplot_1_28_2.cwl
  out:
  - id: output_html
  - id: out_nanostats
  - id: out_nanostats_post_filtering
  - id: out_read_length
  - id: out_log_read_length
- id: kraken2
  in:
  - id: single_paired_input_sequences
    source: filtlong/outfile
  - id: quick
    source: kraken2_quick
  - id: report_minimizer_data
    source: kraken2_report_minimizer_data
  - id: report_zero_counts
    source: kraken2_report_zero_counts
  - id: use_mpa_style
    source: kraken2_use_mpa_style
  - id: use_names
    source: kraken2_use_names
  - id: classified_out
    source: kraken2_classified_out
  - id: confidence
    source: kraken2_confidence
  - id: db
    source: kraken2_db
  - id: minimum_base_quality
    source: kraken2_minimum_base_quality
  - id: minimum_hit_groups
    source: kraken2_minimum_hit_groups
  - id: paired
    source: kraken2_paired
  - id: report
    source: kraken2_report
  - id: threads
    source: kraken2_threads
  - id: unclassified_out
    source: kraken2_unclassified_out
  run: tools/kraken2_2_1_1.cwl
  out:
  - id: output_tabular
  - id: out_classified_out_s
  - id: out_unclassified_out_s
  - id: out_report_output
  - id: out1
  - id: out2
  - id: out3
  - id: out4
  - id: out1_1
  - id: out2_1
  - id: out3_1
  - id: out4_1
- id: kraken2tax
  in:
  - id: ncbi_taxonomy_fields_path1
    source: kraken2tax_ncbi_taxonomy_fields_path1
  - id: ncbi_taxonomy_fields_path2
    source: kraken2tax_ncbi_taxonomy_fields_path2
  - id: positional_3
    source: kraken2tax_positional_3
  run: tools/Kraken2Tax_1_2.cwl
  out:
  - id: out_file
- id: taxonomy_krona_chart
  in:
  - id: positional_1
    source: taxonomy_krona_chart_positional_1
  - id: ktimporttext
    source: taxonomy_krona_chart_ktimporttext
  - id: flag_c
    source: taxonomy_krona_chart_flag_c
  - id: option_n
    source: taxonomy_krona_chart_option_n
  - id: option_o
    source: taxonomy_krona_chart_option_o
  run: tools/taxonomy_krona_chart_2_7_1.cwl
  out:
  - id: output_html
id: long_read_metagenomic_characterisation
