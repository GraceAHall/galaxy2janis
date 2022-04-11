version development

import "tools/fastqc_0_72.wdl" as F

workflow unicycler_training_imported_from_uploaded_file {
  input {
    File in_forward_reads
    File in_reverse_reads
    File in_long_reads
    File fastqc_adapters
    File fastqc_contaminants
    File fastqc_html_file
    File fastqc_limits
    File fastqc_outdir
    Boolean? fastqc_nogroup = false
  }
  call F.fastqc as fastqc {
    input:
      html_file=fastqc_html_file,
      nogroup=select_first([fastqc_nogroup, false]),
      adapters=fastqc_adapters,
      outdir=fastqc_outdir,
      contaminants=fastqc_contaminants,
      limits=fastqc_limits
  }
  output {
    File fastqc_out_html_file = fastqc.out_html_file
    File fastqc_out_text_file = fastqc.out_text_file
  }
}