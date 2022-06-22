version development

import "tools/fastqc_0_72.wdl" as F

workflow unicycler_training_imported_from_uploaded_file {
  input {
    File in_forward_reads
    File in_reverse_reads
    File in_long_reads
    File fastqc_adapters
    File fastqc_contaminants
    File fastqc_limits
    File fastqc_outdir
    File fastqc_option_f
    Boolean? fastqc_nogroup = false
    Int? fastqc_min_length
    Boolean? fastqc_extract = true
    Boolean? fastqc_quiet = true
    Int? fastqc_kmers = 7
  }
  call F.fastqc as fastqc {
    input:
      input_file=in_forward_reads,
      extract=select_first([fastqc_extract, true]),
      nogroup=select_first([fastqc_nogroup, false]),
      quiet=select_first([fastqc_quiet, true]),
      adapters=fastqc_adapters,
      contaminants=fastqc_contaminants,
      kmers=select_first([fastqc_kmers, 7]),
      limits=fastqc_limits,
      min_length=fastqc_min_length,
      option_f=fastqc_option_f,
      outdir=fastqc_outdir
  }
  output {
    File fastqc_out_html_file = fastqc.out_html_file
    File fastqc_out_text_file = fastqc.out_text_file
  }
}


