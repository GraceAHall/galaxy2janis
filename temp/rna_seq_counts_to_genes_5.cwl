#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.2

requirements:
- class: InlineJavascriptRequirement
- class: StepInputExpressionRequirement

inputs:
- id: in_seqdata
  type: string
- id: in_sampleinfo
  type: string
- id: tp_cut_tool1_flag_error
  doc: None
  type: boolean
  default: false
- id: tp_cut_tool1_option_b
  doc: List of Fields. (-f)
  type:
  - int
  - 'null'
- id: tp_cut_tool1_option_c
  doc: List of Fields. (-f)
  type:
  - int
  - 'null'
- id: tp_cut_tool1_option_f
  doc: List of Fields. (-f)
  type:
  - int
  - 'null'
- id: tp_cut_tool1_input__
  doc: None
  type: string
  default: .
- id: tp_cut_tool1_complement
  doc: None
  type: boolean
  default: true
- id: mergecols1_col1
  doc: Merge column
  type: int
  default: 3
- id: mergecols1_col2
  doc: with column. Need to add more columns? Use controls below.
  type: int
  default: 4
- id: mergecols1_out_file11
  doc: None
  type: File
- id: tp_replace_in_line_sandbox
  doc: |-
    Find pattern. Use simple text, or a valid regular expression (without backslashes // ) 
  type: string
- id: tp_replace_in_line_flag_r
  doc: None
  type: boolean
  default: true
- id: tp_cut_tool2_complement
  doc: None
  type: boolean
  default: false
- id: tp_cut_tool2_flag_error
  doc: None
  type: boolean
  default: false
- id: tp_cut_tool2_option_b
  doc: List of Fields. (-f)
  type:
  - int
  - 'null'
- id: tp_cut_tool2_option_c
  doc: List of Fields. (-f)
  type:
  - int
  - 'null'
- id: tp_cut_tool2_option_f
  doc: List of Fields. (-f)
  type:
  - int
  - 'null'
- id: tp_cut_tool2_input__
  doc: None
  type: string
  default: .
- id: annotatemyids_annotatemyids_script
  type: string
- id: limma_voom_flag_i
  doc: None
  type: boolean
  default: false
- id: limma_voom_option_c
  doc: |-
    Minimum CPM. Treat genes with CPM below this value as unexpressed and filter out. See the Filter Low Counts section below for more information.
  type: float
  default: 0.5
- id: limma_voom_option_j
  doc: None
  type: string
- id: limma_voom_option_l
  doc: |-
    Minimum Log2 Fold Change. Genes above this threshold and below the p-value threshold are considered significant and highlighted in the MD plot. Default: 0.
  type: float
  default: 0.58
- id: limma_voom_option_p
  doc: |-
    P-Value Adjusted Threshold. Genes below this threshold are considered significant and highlighted in the MD plot. If either BH(1995) or BY(2001) are selected then this value is a false-discovery-rate control. If Holm(1979) is selected then this is an adjusted p-value for family-wise error rate. Default: 0.05.
  type: float
  default: 0.01
- id: limma_voom_option_s
  doc: |-
    Minimum Samples. Filter out all genes that do not meet the Minimum CPM in at least this many samples. See the Filter Low Counts section below for more information.
  type: int
  default: 2
- id: limma_voom_option_t
  doc: |-
    Prior count. Average count to be added to each observation to avoid taking log of zero. Default: 3.
  type: float
- id: limma_voom_input_d
  doc: None
  type: string
  default: d
- id: limma_voom_flag_b
  doc: None
  type: boolean
  default: true
- id: limma_voom_flag_c
  doc: None
  type: boolean
  default: true
- id: limma_voom_flag_f
  doc: None
  type: boolean
  default: true
- id: limma_voom_flag_l
  doc: None
  type: boolean
  default: true
- id: limma_voom_flag_r
  doc: None
  type: boolean
  default: true
- id: limma_voom_flag_t
  doc: None
  type: boolean
  default: true
- id: limma_voom_flag_w
  doc: None
  type: boolean
  default: true
- id: limma_voom_flag_x
  doc: None
  type: boolean
  default: true
- id: limma_voom_flag_y
  doc: None
  type: boolean
  default: true
- id: limma_voom_option_d
  doc: None
  type: string
  default: BH
- id: limma_voom_option_g
  doc: |-
    Number of genes to highlight in Volcano plot, Heatmap and Stripcharts. The top DE genes will be highlighted in the Volcano plot for each contrast and can be output in heatmap and stripchart PDFs (max 100). Default: 10.
  type: int
  default: 10
- id: limma_voom_option_n
  doc: None
  type: string
  default: TMM
- id: limma_voom_option_o
  doc: None
  type: string
- id: limma_voom_option_r
  doc: Report
  type: File
- id: limma_voom_option_z
  doc: |-
    Minimum Count. Filter out all genes that do not meet this minimum count. You can choose below to apply this filter to the total count for all samples or specify the number of samples under Minimum Samples. See the Filter Low Counts section below for more information.
  type: int
  default: 0

outputs:
- id: tp_cut_tool1_output_tabular
  type: File
  outputSource: tp_cut_tool1/output_tabular
- id: mergecols1_out_file12
  type: File
  outputSource: mergecols1/out_file12
- id: tp_replace_in_line_outfile
  type: string
  outputSource: tp_replace_in_line/outfile
- id: tp_cut_tool2_output_tabular
  type: File
  outputSource: tp_cut_tool2/output_tabular
- id: annotatemyids_out_tab
  type: File
  outputSource: annotatemyids/out_tab
- id: annotatemyids_out_rscript
  type: File
  outputSource: annotatemyids/out_rscript
- id: limma_voom_outtables
  type: string
  outputSource: limma_voom/outtables
- id: limma_voom_outreport
  type: File
  outputSource: limma_voom/outreport
- id: limma_voom_outfilt
  type: File
  outputSource: limma_voom/outfilt
- id: limma_voom_outnorm
  type: File
  outputSource: limma_voom/outnorm
- id: limma_voom_out_rscript
  type: File
  outputSource: limma_voom/out_rscript
- id: limma_voom_out_libinfo
  type: File
  outputSource: limma_voom/out_libinfo

steps:
- id: tp_cut_tool1
  in:
  - id: input__
    source: tp_cut_tool1_input__
  - id: input_textfile1
    source: in_seqdata
  - id: input_textfile2
    source: in_seqdata
  - id: complement
    source: tp_cut_tool1_complement
  - id: flag_error
    source: tp_cut_tool1_flag_error
  - id: option_b
    source: tp_cut_tool1_option_b
  - id: option_c
    source: tp_cut_tool1_option_c
  - id: option_f
    source: tp_cut_tool1_option_f
  run: tools/tp_cut_tool_1_1_0.cwl
  out:
  - id: output_tabular
- id: mergecols1
  in:
  - id: input1
    source: in_sampleinfo
  - id: out_file11
    source: mergecols1_out_file11
  - id: col1
    source: mergecols1_col1
  - id: col2
    source: mergecols1_col2
  run: tools/mergeCols1_1_0_1.cwl
  out:
  - id: out_file12
- id: tp_replace_in_line
  in:
  - id: infile
    source: tp_cut_tool1/output_tabular
  - id: flag_r
    source: tp_replace_in_line_flag_r
  - id: sandbox
    source: tp_replace_in_line_sandbox
  run: tools/tp_replace_in_line_1_1_1.cwl
  out:
  - id: outfile
- id: tp_cut_tool2
  in:
  - id: input__
    source: tp_cut_tool2_input__
  - id: input_textfile1
    source: mergecols1/out_file12
  - id: input_textfile2
    source: mergecols1/out_file12
  - id: complement
    source: tp_cut_tool2_complement
  - id: flag_error
    source: tp_cut_tool2_flag_error
  - id: option_b
    source: tp_cut_tool2_option_b
  - id: option_c
    source: tp_cut_tool2_option_c
  - id: option_f
    source: tp_cut_tool2_option_f
  run: tools/tp_cut_tool_1_1_0.cwl
  out:
  - id: output_tabular
- id: annotatemyids
  in:
  - id: annotatemyids_script
    source: annotatemyids_annotatemyids_script
  run: tools/annotatemyids_3_5_0_1.cwl
  out:
  - id: out_tab
  - id: out_rscript
- id: limma_voom
  in:
  - id: input_d
    source: limma_voom_input_d
  - id: flag_b
    source: limma_voom_flag_b
  - id: flag_c
    source: limma_voom_flag_c
  - id: flag_f
    source: limma_voom_flag_f
  - id: flag_i
    source: limma_voom_flag_i
  - id: flag_l
    source: limma_voom_flag_l
  - id: flag_r
    source: limma_voom_flag_r
  - id: flag_t
    source: limma_voom_flag_t
  - id: flag_w
    source: limma_voom_flag_w
  - id: flag_x
    source: limma_voom_flag_x
  - id: flag_y
    source: limma_voom_flag_y
  - id: option_a
    source: annotatemyids/out_tab
  - id: option_c
    source: limma_voom_option_c
  - id: option_d
    source: limma_voom_option_d
  - id: option_f
    source: tp_cut_tool2/output_tabular
  - id: option_g
    source: limma_voom_option_g
  - id: option_j
    source: limma_voom_option_j
  - id: option_l
    source: limma_voom_option_l
  - id: option_m
    source: tp_replace_in_line/outfile
  - id: option_n
    source: limma_voom_option_n
  - id: option_o
    source: limma_voom_option_o
  - id: option_p
    source: limma_voom_option_p
  - id: option_r
    source: limma_voom_option_r
  - id: option_s
    source: limma_voom_option_s
  - id: option_t
    source: limma_voom_option_t
  - id: option_z
    source: limma_voom_option_z
  run: tools/limma_voom_3_34_9_9.cwl
  out:
  - id: outreport
  - id: outtables
  - id: outfilt
  - id: outnorm
  - id: out_rscript
  - id: out_libinfo
id: rna_seq_counts_to_genes
