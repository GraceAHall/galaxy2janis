version development

import "tools/fastqc_0_72.wdl" as F
import "tools/cutadapt_1_16_3.wdl" as C
import "tools/hisat2_2_2_1.wdl" as H
import "tools/featurecounts_2_0_1.wdl" as F2
import "tools/picard_MarkDuplicates_2_18_2_1.wdl" as P
import "tools/samtools_idxstats_2_0_2.wdl" as S
import "tools/rseqc_geneBody_coverage_2_6_4_3.wdl" as R
import "tools/rseqc_infer_experiment_2_6_4_1.wdl" as R2
import "tools/rseqc_read_distribution_2_6_4_1.wdl" as R3
import "tools/collection_column_join_0_0_3.wdl" as C2
import "tools/multiqc_1_6.wdl" as M

workflow rna_seq_reads_to_counts_imported_from_uploaded_file {
  input {
    File in_input_fastqs_collection
    File in_input_reference_gene_bed
    File fastqc1_contaminants1
    File fastqc1_contaminants2
    File fastqc1_limits
    Boolean? cutadapt_match_read_wildcards = false
    Int? cutadapt_minimum_length = 20
    Boolean? cutadapt_discard_untrimmed = false
    Boolean? cutadapt_too_long_output = false
    Boolean? cutadapt_info_file = false
    Boolean? cutadapt_too_short_output = false
    Boolean? cutadapt_no_trim = false
    String? cutadapt_quality_cutoff = "20"
    Boolean? cutadapt_rest_file = false
    Boolean? cutadapt_trim_n = false
    Boolean? cutadapt_mask_adapter = false
    Boolean? cutadapt_untrimmed_output = false
    Boolean? cutadapt_discard_trimmed = false
    Boolean? cutadapt_wildcard_file = false
    Boolean? cutadapt_no_indels = false
    File fastqc2_contaminants1
    File fastqc2_contaminants2
    File fastqc2_limits
    File hisat2_hisat2_build
    File hisat2_input_1_file
    File hisat2_input_2_file
    File hisat2_input_u_file
    File hisat2_input_x_file
    Boolean? hisat2_summary_file = true
    Boolean? hisat2_new_summary = true
    Boolean? featurecounts_c_flag = true
    Boolean? featurecounts_j_flag = false
    Boolean? featurecounts_l_flag = false
    Boolean? featurecounts_largestoverlap = false
    Boolean? featurecounts_r_flag = false
    Boolean? featurecounts_b_flag = false
    Boolean? featurecounts_f_flag = false
    Boolean? featurecounts_byreadgroup = false
    File picard_markduplicates_input_file
    File picard_markduplicates_read_name_regex
    File picard_markduplicates_optional
    File picard_markduplicates_arguments
    Boolean? picard_markduplicates_assume_sorted = true
    Boolean? picard_markduplicates_remove_duplicates = false
    File samtools_idxstats_infile
    File samtools_idxstats_input_at_file
    File rseqc_genebody_coverage_input_i_file
    File collection_column_join_tmp_tmpn7l397qd_configs_tmpkux73fey
    File multiqc_config
    String? multiqc_title = "Tutorial RNA-seq reads to counts"
  }
  call F.fastqc as fastqc1 {
    input:
      contaminants1=fastqc1_contaminants1,
      contaminants2=fastqc1_contaminants2,
      limits=fastqc1_limits
  }
  call C.cutadapt as cutadapt {
    input:
      discard_trimmed=select_first([cutadapt_discard_trimmed, false]),
      discard_untrimmed=select_first([cutadapt_discard_untrimmed, false]),
      info_file=select_first([cutadapt_info_file, false]),
      mask_adapter=select_first([cutadapt_mask_adapter, false]),
      match_read_wildcards=select_first([cutadapt_match_read_wildcards, false]),
      no_indels=select_first([cutadapt_no_indels, false]),
      no_trim=select_first([cutadapt_no_trim, false]),
      rest_file=select_first([cutadapt_rest_file, false]),
      too_long_output=select_first([cutadapt_too_long_output, false]),
      too_short_output=select_first([cutadapt_too_short_output, false]),
      trim_n=select_first([cutadapt_trim_n, false]),
      untrimmed_output=select_first([cutadapt_untrimmed_output, false]),
      wildcard_file=select_first([cutadapt_wildcard_file, false]),
      minimum_length=select_first([cutadapt_minimum_length, 20]),
      quality_cutoff=select_first([cutadapt_quality_cutoff, "20"])
  }
  call F.fastqc as fastqc2 {
    input:
      contaminants1=fastqc2_contaminants1,
      contaminants2=fastqc2_contaminants2,
      limits=fastqc2_limits
  }
  call H.hisat2 as hisat2 {
    input:
      hisat2_build=hisat2_hisat2_build,
      new_summary=select_first([hisat2_new_summary, true]),
      summary_file=select_first([hisat2_summary_file, true]),
      input_1_file=hisat2_input_1_file,
      input_2_file=hisat2_input_2_file,
      input_u_file=hisat2_input_u_file,
      input_x_file=hisat2_input_x_file
  }
  call F2.featurecounts as featurecounts {
    input:
      b_flag=select_first([featurecounts_b_flag, false]),
      byreadgroup=select_first([featurecounts_byreadgroup, false]),
      c_flag=select_first([featurecounts_c_flag, true]),
      f_flag=select_first([featurecounts_f_flag, false]),
      j_flag=select_first([featurecounts_j_flag, false]),
      l_flag=select_first([featurecounts_l_flag, false]),
      largestoverlap=select_first([featurecounts_largestoverlap, false]),
      r_flag=select_first([featurecounts_r_flag, false])
  }
  call P.picard_MarkDuplicates as picard_markduplicates {
    input:
      read_name_regex=picard_markduplicates_read_name_regex,
      input_file=picard_markduplicates_input_file,
      optional=picard_markduplicates_optional,
      arguments=picard_markduplicates_arguments,
      assume_sorted=select_first([picard_markduplicates_assume_sorted, true]),
      remove_duplicates=select_first([picard_markduplicates_remove_duplicates, false])
  }
  call S.samtools_idxstats as samtools_idxstats {
    input:
      infile=samtools_idxstats_infile,
      input_at_file=samtools_idxstats_input_at_file
  }
  call R.rseqc_geneBody_coverage as rseqc_genebody_coverage {
    input:
      input_i_file=rseqc_genebody_coverage_input_i_file,
      input_r_bed12=in_input_reference_gene_bed
  }
  call R2.rseqc_infer_experiment as rseqc_infer_experiment {
    input:
      input_i_bam=hisat2.output_alignments,
      input_r_bed12=in_input_reference_gene_bed
  }
  call R3.rseqc_read_distribution as rseqc_read_distribution {
    input:
      input_i_bam=hisat2.output_alignments,
      input_r_bed12=in_input_reference_gene_bed
  }
  call C2.collection_column_join as collection_column_join {
    input:
      tmp_tmpn7l397qd_configs_tmpkux73fey=collection_column_join_tmp_tmpn7l397qd_configs_tmpkux73fey
  }
  call M.multiqc as multiqc {
    input:
      config=multiqc_config,
      title=select_first([multiqc_title, "Tutorial RNA-seq reads to counts"])
  }
}