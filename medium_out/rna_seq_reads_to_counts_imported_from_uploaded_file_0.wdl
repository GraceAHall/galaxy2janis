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
    String in_input_fastqs_collection
    String in_input_reference_gene_bed
    File fastqc1_contaminants2
    File fastqc1_limits
    String fastqc1_contaminants1
    Boolean? fastqc1_extract = true
    String? fastqc1_option_f = "fastq"
    String? fastqc1_outdir = "/tmp/tmpm6wv3dfv/working/dataset_4_files"
    Boolean? fastqc1_quiet = true
    Boolean? cutadapt_info_file = false
    Int? cutadapt_minimum_length = 20
    String? cutadapt_quality_cutoff = "20"
    Boolean? cutadapt_rest_file = false
    Boolean? cutadapt_too_long_output = false
    Boolean? cutadapt_too_short_output = false
    Boolean? cutadapt_untrimmed_output = false
    Boolean? cutadapt_wildcard_file = false
    Float? cutadapt_error_rate = 0.1
    Int? cutadapt_length = 0
    String? cutadapt_length_tag
    Float? cutadapt_max_n
    Int? cutadapt_maximum_length = 0
    Int? cutadapt_nextseq_trim = 0
    Int? cutadapt_option_u1 = 0
    Int? cutadapt_option_u2 = 0
    Int? cutadapt_overlap = 3
    String? cutadapt_pair_filter = "any"
    String? cutadapt_prefix
    String? cutadapt_suffix
    Int? cutadapt_times = 1
    File fastqc2_contaminants2
    File fastqc2_limits
    String fastqc2_contaminants1
    Boolean? fastqc2_extract = true
    String? fastqc2_option_f = "fastq"
    String? fastqc2_outdir = "/tmp/tmpsnwwj5h8/working/dataset_4_files"
    Boolean? fastqc2_quiet = true
    Boolean? hisat2_new_summary = true
    Boolean? hisat2_summary_file = true
    Boolean? hisat2_add_chrname = false
    File? hisat2_al
    File? hisat2_al_bz2
    File? hisat2_al_conc
    File? hisat2_al_conc_bz2
    File? hisat2_al_conc_gz
    File? hisat2_al_gz
    Boolean? hisat2_dta = false
    Boolean? hisat2_dta_cufflinks = false
    Boolean? hisat2_ff = false
    Boolean? hisat2_flag_f = true
    Boolean? hisat2_fr = false
    Boolean? hisat2_ignore_quals = false
    Boolean? hisat2_int_quals = false
    String? hisat2_known_splicesite_infile = "splice_sites.txt"
    Int? hisat2_max_intronlen = 500000
    Int? hisat2_min_intronlen = 20
    Int? hisat2_mp = 6
    String? hisat2_n_ceil = "L"
    Boolean? hisat2_no_discordant = false
    Boolean? hisat2_no_mixed = false
    Boolean? hisat2_no_softclip = true
    Boolean? hisat2_no_spliced_alignment = false
    Boolean? hisat2_no_templatelen_adjustment = false
    Boolean? hisat2_no_unal = false
    Boolean? hisat2_nofw = false
    Boolean? hisat2_non_deterministic = false
    Boolean? hisat2_norc = false
    String? hisat2_novel_splicesite_outfile = "novel_splicesite_output"
    Int? hisat2_np = 1
    Boolean? hisat2_omit_sec_seq = false
    String? hisat2_option_1 = "input_f.fastq"
    String? hisat2_option_2 = "input_r.fastq"
    Int? hisat2_option_i = 0
    Int? hisat2_option_k
    Int? hisat2_option_p = 1
    Int? hisat2_option_s = 0
    Int? hisat2_option_u1 = 0
    String? hisat2_option_u2 = "input_f.fastq"
    Int? hisat2_option_x1 = 500
    String? hisat2_option_x2 = "genome"
    String? hisat2_pen_canintronlen = "G"
    Int? hisat2_pen_cansplice = 0
    String? hisat2_pen_noncanintronlen = "G"
    Int? hisat2_pen_noncansplice = 12
    Boolean? hisat2_phred33 = false
    Boolean? hisat2_phred64 = false
    Int? hisat2_qupto = 0
    Int? hisat2_rdg = 5
    Boolean? hisat2_remove_chrname = false
    Boolean? hisat2_rf = false
    Int? hisat2_rfg = 5
    String? hisat2_rg_id = "read_group"
    String? hisat2_rna_strandness = ""
    String? hisat2_score_min = "L"
    Int? hisat2_seed = 0
    Int? hisat2_skip = 0
    Boolean? hisat2_solexa_quals = false
    Int? hisat2_sp = 2
    Boolean? hisat2_tmo = false
    Int? hisat2_trim3 = 0
    Int? hisat2_trim5 = 0
    File? hisat2_un
    File? hisat2_un_bz2
    File? hisat2_un_conc
    File? hisat2_un_conc_bz2
    File? hisat2_un_conc_gz
    File? hisat2_un_gz
    Boolean? featurecounts_byreadgroup = false
    Boolean? featurecounts_flag_b = false
    Boolean? featurecounts_flag_c = true
    Boolean? featurecounts_flag_f = false
    Boolean? featurecounts_flag_j = false
    Boolean? featurecounts_flag_l = false
    Boolean? featurecounts_flag_r = false
    Boolean? featurecounts_largestoverlap = false
    Boolean? featurecounts_flag_m = false
    Boolean? featurecounts_flag_o = false
    Boolean? featurecounts_flag_p = false
    Int? featurecounts_fracoverlap = 0
    Int? featurecounts_fracoverlapfeature = 0
    Boolean? featurecounts_fraction = false
    Boolean? featurecounts_ignoredup = false
    Int? featurecounts_minoverlap = 1
    Boolean? featurecounts_nonsplitonly = false
    File? featurecounts_option_a
    Int? featurecounts_option_d1 = 50
    Int? featurecounts_option_d2 = 600
    String? featurecounts_option_f = "GTF"
    String? featurecounts_option_g1 = "gene_id"
    File? featurecounts_option_g2
    String? featurecounts_option_o = "output"
    String? featurecounts_option_p = ""
    Int? featurecounts_option_q = 0
    String? featurecounts_option_s = "0"
    String? featurecounts_option_t1 = "exon"
    Int? featurecounts_option_t2 = 2
    Boolean? featurecounts_primary = false
    Boolean? featurecounts_read2pos = false
    Int? featurecounts_readextension3 = 0
    Int? featurecounts_readextension5 = 0
    Boolean? featurecounts_splitonly = false
    Boolean? picard_markduplicates_assume_sorted = true
    Boolean? picard_markduplicates_remove_duplicates = false
    String? picard_markduplicates_arguments = "arguments"
    String? picard_markduplicates_barcode_tag
    String? picard_markduplicates_duplicate_scoring_strategy = "SUM_OF_BASE_QUALITIES"
    String? picard_markduplicates_input_string
    File? picard_markduplicates_metrics_file
    Int? picard_markduplicates_optical_duplicate_pixel_distance = 100
    String? picard_markduplicates_optional = "Optional"
    File? picard_markduplicates_output_bam
    String? picard_markduplicates_quiet = "true"
    String? picard_markduplicates_validation_stringency = "LENIENT"
    String? picard_markduplicates_verbosity = "ERROR"
    String? samtools_idxstats_at
    String? samtools_idxstats_infile = "infile"
    Int? rseqc_genebody_coverage_minimum_length = 100
    String? rseqc_genebody_coverage_option_i
    String? rseqc_genebody_coverage_option_o = "output"
    Int? rseqc_infer_experiment_mapq = 30
    Int? rseqc_infer_experiment_sample_size = 200000
    String collection_column_join_collection_column_join_script
    String? multiqc_title = "Tutorial RNA-seq reads to counts"
    String? multiqc_comment
    String? multiqc_config
    String? multiqc_filename = "report"
  }
  call F.fastqc as fastqc1 {
    input:
      contaminants1=fastqc1_contaminants1,
      extract=select_first([fastqc1_extract, true]),
      quiet=select_first([fastqc1_quiet, true]),
      contaminants2=fastqc1_contaminants2,
      limits=fastqc1_limits,
      option_f=select_first([fastqc1_option_f, "fastq"]),
      outdir=select_first([fastqc1_outdir, "/tmp/tmpm6wv3dfv/working/dataset_4_files"])
  }
  call C.cutadapt as cutadapt {
    input:
      info_file=select_first([cutadapt_info_file, false]),
      rest_file=select_first([cutadapt_rest_file, false]),
      too_long_output=select_first([cutadapt_too_long_output, false]),
      too_short_output=select_first([cutadapt_too_short_output, false]),
      untrimmed_output=select_first([cutadapt_untrimmed_output, false]),
      wildcard_file=select_first([cutadapt_wildcard_file, false]),
      error_rate=select_first([cutadapt_error_rate, 0.1]),
      length=select_first([cutadapt_length, 0]),
      length_tag=cutadapt_length_tag,
      max_n=cutadapt_max_n,
      maximum_length=select_first([cutadapt_maximum_length, 0]),
      minimum_length=select_first([cutadapt_minimum_length, 20]),
      nextseq_trim=select_first([cutadapt_nextseq_trim, 0]),
      option_u1=select_first([cutadapt_option_u1, 0]),
      option_u2=select_first([cutadapt_option_u2, 0]),
      overlap=select_first([cutadapt_overlap, 3]),
      pair_filter=select_first([cutadapt_pair_filter, "any"]),
      prefix=cutadapt_prefix,
      quality_cutoff=select_first([cutadapt_quality_cutoff, "20"]),
      suffix=cutadapt_suffix,
      times=select_first([cutadapt_times, 1])
  }
  call F.fastqc as fastqc2 {
    input:
      contaminants1=fastqc2_contaminants1,
      extract=select_first([fastqc2_extract, true]),
      quiet=select_first([fastqc2_quiet, true]),
      contaminants2=fastqc2_contaminants2,
      limits=fastqc2_limits,
      option_f=select_first([fastqc2_option_f, "fastq"]),
      outdir=select_first([fastqc2_outdir, "/tmp/tmpsnwwj5h8/working/dataset_4_files"])
  }
  call H.hisat2 as hisat2 {
    input:
      add_chrname=select_first([hisat2_add_chrname, false]),
      dta=select_first([hisat2_dta, false]),
      dta_cufflinks=select_first([hisat2_dta_cufflinks, false]),
      ff=select_first([hisat2_ff, false]),
      flag_f=select_first([hisat2_flag_f, true]),
      fr=select_first([hisat2_fr, false]),
      ignore_quals=select_first([hisat2_ignore_quals, false]),
      int_quals=select_first([hisat2_int_quals, false]),
      new_summary=select_first([hisat2_new_summary, true]),
      no_discordant=select_first([hisat2_no_discordant, false]),
      no_mixed=select_first([hisat2_no_mixed, false]),
      no_softclip=select_first([hisat2_no_softclip, true]),
      no_spliced_alignment=select_first([hisat2_no_spliced_alignment, false]),
      no_templatelen_adjustment=select_first([hisat2_no_templatelen_adjustment, false]),
      no_unal=select_first([hisat2_no_unal, false]),
      nofw=select_first([hisat2_nofw, false]),
      non_deterministic=select_first([hisat2_non_deterministic, false]),
      norc=select_first([hisat2_norc, false]),
      omit_sec_seq=select_first([hisat2_omit_sec_seq, false]),
      phred33=select_first([hisat2_phred33, false]),
      phred64=select_first([hisat2_phred64, false]),
      remove_chrname=select_first([hisat2_remove_chrname, false]),
      rf=select_first([hisat2_rf, false]),
      solexa_quals=select_first([hisat2_solexa_quals, false]),
      summary_file=select_first([hisat2_summary_file, true]),
      tmo=select_first([hisat2_tmo, false]),
      al=hisat2_al,
      al_bz2=hisat2_al_bz2,
      al_conc=hisat2_al_conc,
      al_conc_bz2=hisat2_al_conc_bz2,
      al_conc_gz=hisat2_al_conc_gz,
      al_gz=hisat2_al_gz,
      known_splicesite_infile=select_first([hisat2_known_splicesite_infile, "splice_sites.txt"]),
      max_intronlen=select_first([hisat2_max_intronlen, 500000]),
      min_intronlen=select_first([hisat2_min_intronlen, 20]),
      mp=select_first([hisat2_mp, 6]),
      n_ceil=select_first([hisat2_n_ceil, "L"]),
      novel_splicesite_outfile=select_first([hisat2_novel_splicesite_outfile, "novel_splicesite_output"]),
      np=select_first([hisat2_np, 1]),
      option_1=select_first([hisat2_option_1, "input_f.fastq"]),
      option_2=select_first([hisat2_option_2, "input_r.fastq"]),
      option_i=select_first([hisat2_option_i, 0]),
      option_k=hisat2_option_k,
      option_p=select_first([hisat2_option_p, 1]),
      option_s=select_first([hisat2_option_s, 0]),
      option_u1=select_first([hisat2_option_u1, 0]),
      option_u2=select_first([hisat2_option_u2, "input_f.fastq"]),
      option_x1=select_first([hisat2_option_x1, 500]),
      option_x2=select_first([hisat2_option_x2, "genome"]),
      pen_canintronlen=select_first([hisat2_pen_canintronlen, "G"]),
      pen_cansplice=select_first([hisat2_pen_cansplice, 0]),
      pen_noncanintronlen=select_first([hisat2_pen_noncanintronlen, "G"]),
      pen_noncansplice=select_first([hisat2_pen_noncansplice, 12]),
      qupto=select_first([hisat2_qupto, 0]),
      rdg=select_first([hisat2_rdg, 5]),
      rfg=select_first([hisat2_rfg, 5]),
      rg_id=select_first([hisat2_rg_id, "read_group"]),
      rna_strandness=select_first([hisat2_rna_strandness, ""]),
      score_min=select_first([hisat2_score_min, "L"]),
      seed=select_first([hisat2_seed, 0]),
      skip=select_first([hisat2_skip, 0]),
      sp=select_first([hisat2_sp, 2]),
      trim3=select_first([hisat2_trim3, 0]),
      trim5=select_first([hisat2_trim5, 0]),
      un=hisat2_un,
      un_bz2=hisat2_un_bz2,
      un_conc=hisat2_un_conc,
      un_conc_bz2=hisat2_un_conc_bz2,
      un_conc_gz=hisat2_un_conc_gz,
      un_gz=hisat2_un_gz
  }
  call F2.featurecounts as featurecounts {
    input:
      alignment=hisat2.output_alignments,
      byreadgroup=select_first([featurecounts_byreadgroup, false]),
      flag_b=select_first([featurecounts_flag_b, false]),
      flag_c=select_first([featurecounts_flag_c, true]),
      flag_f=select_first([featurecounts_flag_f, false]),
      flag_j=select_first([featurecounts_flag_j, false]),
      flag_l=select_first([featurecounts_flag_l, false]),
      flag_m=select_first([featurecounts_flag_m, false]),
      flag_o=select_first([featurecounts_flag_o, false]),
      flag_p=select_first([featurecounts_flag_p, false]),
      flag_r=select_first([featurecounts_flag_r, false]),
      fraction=select_first([featurecounts_fraction, false]),
      ignoredup=select_first([featurecounts_ignoredup, false]),
      largestoverlap=select_first([featurecounts_largestoverlap, false]),
      nonsplitonly=select_first([featurecounts_nonsplitonly, false]),
      primary=select_first([featurecounts_primary, false]),
      read2pos=select_first([featurecounts_read2pos, false]),
      splitonly=select_first([featurecounts_splitonly, false]),
      fracoverlap=select_first([featurecounts_fracoverlap, 0]),
      fracoverlapfeature=select_first([featurecounts_fracoverlapfeature, 0]),
      minoverlap=select_first([featurecounts_minoverlap, 1]),
      option_a=featurecounts_option_a,
      option_d1=select_first([featurecounts_option_d1, 50]),
      option_d2=select_first([featurecounts_option_d2, 600]),
      option_f=select_first([featurecounts_option_f, "GTF"]),
      option_g1=select_first([featurecounts_option_g1, "gene_id"]),
      option_g2=featurecounts_option_g2,
      option_o=select_first([featurecounts_option_o, "output"]),
      option_p=select_first([featurecounts_option_p, ""]),
      option_q=select_first([featurecounts_option_q, 0]),
      option_s=select_first([featurecounts_option_s, "0"]),
      option_t1=select_first([featurecounts_option_t1, "exon"]),
      option_t2=select_first([featurecounts_option_t2, 2]),
      readextension3=select_first([featurecounts_readextension3, 0]),
      readextension5=select_first([featurecounts_readextension5, 0])
  }
  call P.picard_MarkDuplicates as picard_markduplicates {
    input:
      optional=select_first([picard_markduplicates_optional, "Optional"]),
      arguments=select_first([picard_markduplicates_arguments, "arguments"]),
      assume_sorted=select_first([picard_markduplicates_assume_sorted, true]),
      barcode_tag=picard_markduplicates_barcode_tag,
      duplicate_scoring_strategy=select_first([picard_markduplicates_duplicate_scoring_strategy, "SUM_OF_BASE_QUALITIES"]),
      input_string=picard_markduplicates_input_string,
      metrics_file=picard_markduplicates_metrics_file,
      optical_duplicate_pixel_distance=select_first([picard_markduplicates_optical_duplicate_pixel_distance, 100]),
      output_bam=picard_markduplicates_output_bam,
      quiet=select_first([picard_markduplicates_quiet, "true"]),
      remove_duplicates=select_first([picard_markduplicates_remove_duplicates, false]),
      validation_stringency=select_first([picard_markduplicates_validation_stringency, "LENIENT"]),
      verbosity=select_first([picard_markduplicates_verbosity, "ERROR"])
  }
  call S.samtools_idxstats as samtools_idxstats {
    input:
      infile=select_first([samtools_idxstats_infile, "infile"]),
      at=samtools_idxstats_at
  }
  call R.rseqc_geneBody_coverage as rseqc_genebody_coverage {
    input:
      minimum_length=select_first([rseqc_genebody_coverage_minimum_length, 100]),
      option_i=rseqc_genebody_coverage_option_i,
      option_o=select_first([rseqc_genebody_coverage_option_o, "output"]),
      option_r=in_input_reference_gene_bed
  }
  call R2.rseqc_infer_experiment as rseqc_infer_experiment {
    input:
      mapq=select_first([rseqc_infer_experiment_mapq, 30]),
      option_i=hisat2.output_alignments,
      option_r=in_input_reference_gene_bed,
      sample_size=select_first([rseqc_infer_experiment_sample_size, 200000])
  }
  call R3.rseqc_read_distribution as rseqc_read_distribution {
    input:
      option_i=hisat2.output_alignments,
      option_r=in_input_reference_gene_bed
  }
  call C2.collection_column_join as collection_column_join {
    input:
      collection_column_join_script=collection_column_join_collection_column_join_script
  }
  call M.multiqc as multiqc {
    input:
      comment=multiqc_comment,
      config=multiqc_config,
      filename=select_first([multiqc_filename, "report"]),
      title=select_first([multiqc_title, "Tutorial RNA-seq reads to counts"])
  }
}