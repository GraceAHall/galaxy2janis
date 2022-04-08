version development

import "tools/fastqc_0_72.wdl" as F
import "tools/unicycler_0_4_8_0.wdl" as U
import "tools/multiqc_1_7.wdl" as M
import "tools/quast_5_0_2.wdl" as Q
import "tools/prokka_1_14_5.wdl" as P

workflow unicycler_training {
  input {
    File forward_reads
    File reverse_reads
    File long_reads
    File fastqc1_adapters
    File fastqc1_contaminants
    File fastqc1_html_file
    File fastqc1_limits
    File fastqc1_outdir
    File fastqc2_adapters
    File fastqc2_contaminants
    File fastqc2_html_file
    File fastqc2_limits
    File fastqc2_outdir
    File unicycler_contamination
    File unicycler_fq11
    File unicycler_fq12
    File unicycler_l_file
    File unicycler_pilon_path
    File unicycler_start_genes
    Float? unicycler_start_gene_cov = 95.0
    Float? unicycler_start_gene_id = 90.0
    File multiqc_multiqc_config
    File quast_labels
    File quast_references_list2
    Boolean? quast_skip_unaligned_mis_contigs = true
    File prokka_proteins
    String? prokka_genus = "Escherichia"
    Int? prokka_gcode = 11
    String? prokka_strain = "C-1"
    Int? prokka_increment = 10
    String? prokka_locustag = "PROKKA"
    String? prokka_species = "Coli"
  }
  call F.fastqc as fastqc1 {
    input:
      html_file=fastqc1_html_file,
      adapters=fastqc1_adapters,
      outdir=fastqc1_outdir,
      contaminants=fastqc1_contaminants,
      limits=fastqc1_limits
  }
  call F.fastqc as fastqc2 {
    input:
      html_file=fastqc2_html_file,
      adapters=fastqc2_adapters,
      outdir=fastqc2_outdir,
      contaminants=fastqc2_contaminants,
      limits=fastqc2_limits
  }
  call U.unicycler as unicycler {
    input:
      fq11=unicycler_fq11,
      fq12=unicycler_fq12,
      s_FastqSanger=forward_reads,
      FastqSanger_2=reverse_reads,
      long=long_reads,
      start_genes=unicycler_start_genes,
      start_gene_id=select_first([unicycler_start_gene_id, 90.0]),
      start_gene_cov=select_first([unicycler_start_gene_cov, 95.0]),
      contamination=unicycler_contamination,
      pilon_path=unicycler_pilon_path,
      l_File=unicycler_l_file
  }
  call M.multiqc as multiqc {
    input:
      multiqc_config=multiqc_multiqc_config
  }
  call Q.quast as quast {
    input:
      skip_unaligned_mis_contigs=select_first([quast_skip_unaligned_mis_contigs, true]),
      references_list2=quast_references_list2,
      labels=quast_labels
  }
  call P.prokka as prokka {
    input:
      locustag=select_first([prokka_locustag, "PROKKA"]),
      increment=select_first([prokka_increment, 10]),
      genus=select_first([prokka_genus, "Escherichia"]),
      species=select_first([prokka_species, "Coli"]),
      strain=select_first([prokka_strain, "C-1"]),
      gcode=select_first([prokka_gcode, 11]),
      proteins=prokka_proteins,
      notrna=unicycler.assembly
  }
  output {
    File fastqc1_html_file_out = fastqc1.html_file
    File fastqc1_text_file_out = fastqc1.text_file
    File fastqc2_html_file_out = fastqc2.html_file
    File fastqc2_text_file_out = fastqc2.text_file
    File unicycler_assembly_out = unicycler.assembly
    File multiqc_stats_out = multiqc.stats
    File multiqc_html_report_out = multiqc.html_report
    File quast_report_html_out = quast.report_html
    File prokka_out_gff_out = prokka.out_gff
    File prokka_out_gbk_out = prokka.out_gbk
    File prokka_out_fna_out = prokka.out_fna
    File prokka_out_faa_out = prokka.out_faa
    File prokka_out_ffn_out = prokka.out_ffn
    File prokka_out_sqn_out = prokka.out_sqn
    File prokka_out_fsa_out = prokka.out_fsa
    File prokka_out_tbl_out = prokka.out_tbl
    File prokka_out_err_out = prokka.out_err
    File prokka_out_txt_out = prokka.out_txt
    File prokka_out_log_out = prokka.out_log
  }
}