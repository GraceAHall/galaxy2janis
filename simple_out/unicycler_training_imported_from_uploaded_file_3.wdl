version development

import "tools/fastqc_0_72.wdl" as F
import "tools/unicycler_0_4_8_0.wdl" as U
import "tools/multiqc_1_7.wdl" as M
import "tools/quast_5_0_2.wdl" as Q
import "tools/prokka_1_14_5.wdl" as P

workflow unicycler_training_imported_from_uploaded_file {
  input {
    File in_forward_reads
    File in_reverse_reads
    File in_long_reads
    File fastqc1_adapters
    File fastqc1_contaminants
    File fastqc1_html_file
    File fastqc1_limits
    Boolean? fastqc1_nogroup = false
    File fastqc2_adapters
    File fastqc2_contaminants
    File fastqc2_html_file
    File fastqc2_limits
    Boolean? fastqc2_nogroup = false
    File unicycler_contamination
    File unicycler_input_l_file
    File unicycler_pilon_path
    File unicycler_start_genes
    Boolean? unicycler_no_rotate = false
    Boolean? unicycler_no_correct = false
    Boolean? unicycler_no_pilon = false
    Boolean? unicycler_largest_component = false
    Float? unicycler_start_gene_id = 90.0
    Float? unicycler_start_gene_cov = 95.0
    File multiqc_config
    File quast_labels
    File quast_references_list2
    Boolean? quast_use_all_alignments = false
    Boolean? quast_fragmented = false
    Boolean? quast_large = false
    Boolean? quast_skip_unaligned_mis_contigs = true
    Boolean? quast_upper_bound_assembly = false
    Boolean? quast_split_scaffolds = false
    Boolean? quast_circos = false
    Boolean? quast_conserved_genes_finding = false
    Boolean? quast_strict_na = false
    Boolean? quast_rna_finding = false
    File prokka_proteins
    String? prokka_species = "Coli"
    String? prokka_genus = "Escherichia"
    String? prokka_strain = "C-1"
    String? prokka_locustag = "PROKKA"
    Int? prokka_increment = 10
  }
  call F.fastqc as fastqc1 {
    input:
      html_file=fastqc1_html_file,
      nogroup=select_first([fastqc1_nogroup, false]),
      adapters=fastqc1_adapters,
      contaminants=fastqc1_contaminants,
      limits=fastqc1_limits
  }
  call F.fastqc as fastqc2 {
    input:
      html_file=fastqc2_html_file,
      nogroup=select_first([fastqc2_nogroup, false]),
      adapters=fastqc2_adapters,
      contaminants=fastqc2_contaminants,
      limits=fastqc2_limits
  }
  call U.unicycler as unicycler {
    input:
      largest_component=select_first([unicycler_largest_component, false]),
      no_correct=select_first([unicycler_no_correct, false]),
      no_pilon=select_first([unicycler_no_pilon, false]),
      no_rotate=select_first([unicycler_no_rotate, false]),
      contamination=unicycler_contamination,
      fastq_input1=in_forward_reads,
      fastq_input2=in_reverse_reads,
      input_l_file=unicycler_input_l_file,
      input_s_fastqsanger=in_forward_reads,
      long=in_long_reads,
      pilon_path=unicycler_pilon_path,
      start_gene_cov=select_first([unicycler_start_gene_cov, 95.0]),
      start_gene_id=select_first([unicycler_start_gene_id, 90.0]),
      start_genes=unicycler_start_genes
  }
  call M.multiqc as multiqc {
    input:
      config=multiqc_config
  }
  call Q.quast as quast {
    input:
      circos=select_first([quast_circos, false]),
      conserved_genes_finding=select_first([quast_conserved_genes_finding, false]),
      fragmented=select_first([quast_fragmented, false]),
      large=select_first([quast_large, false]),
      rna_finding=select_first([quast_rna_finding, false]),
      skip_unaligned_mis_contigs=select_first([quast_skip_unaligned_mis_contigs, true]),
      split_scaffolds=select_first([quast_split_scaffolds, false]),
      strict_na=select_first([quast_strict_na, false]),
      upper_bound_assembly=select_first([quast_upper_bound_assembly, false]),
      use_all_alignments=select_first([quast_use_all_alignments, false]),
      labels=quast_labels,
      references_list2=quast_references_list2
  }
  call P.prokka as prokka {
    input:
      genus=select_first([prokka_genus, "Escherichia"]),
      increment=select_first([prokka_increment, 10]),
      locustag=select_first([prokka_locustag, "PROKKA"]),
      notrna=unicycler.out_assembly,
      proteins=prokka_proteins,
      species=select_first([prokka_species, "Coli"]),
      strain=select_first([prokka_strain, "C-1"])
  }
  output {
    File fastqc1_out_html_file = fastqc1.out_html_file
    File fastqc1_out_text_file = fastqc1.out_text_file
    File fastqc2_out_html_file = fastqc2.out_html_file
    File fastqc2_out_text_file = fastqc2.out_text_file
    File unicycler_out_assembly = unicycler.out_assembly
    File multiqc_out_stats = multiqc.out_stats
    File multiqc_out_html_report = multiqc.out_html_report
    File quast_out_report_html = quast.out_report_html
    File prokka_out_gff = prokka.out_gff
    File prokka_out_gbk = prokka.out_gbk
    File prokka_out_fna = prokka.out_fna
    File prokka_out_faa = prokka.out_faa
    File prokka_out_ffn = prokka.out_ffn
    File prokka_out_sqn = prokka.out_sqn
    File prokka_out_fsa = prokka.out_fsa
    File prokka_out_tbl = prokka.out_tbl
    File prokka_out_err = prokka.out_err
    File prokka_out_txt = prokka.out_txt
    File prokka_out_log = prokka.out_log
  }
}