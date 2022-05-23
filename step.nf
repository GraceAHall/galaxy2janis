process SAMTOOLS_VIEW {
    tag 'samtools view'
    container 'quay.io/biocontainers/samtools:1.5--2'

    input:
      path input
    
    output:
      path '*.filtered.bam', emit: output
    
    script:
    def min_mapping_qualityArgument = params.min_mapping_quality ? "-q $params.min_mapping_quality" : ''
    def bits_setArgument = params.bits_set ? "-F $params.bits_set" : ''
    def threadsArgument = params.threads_samtools ? "--threads $params.threads_samtools" : ''
    """
    samtools view $threadsArgument $min_mapping_qualityArgument $bits_setArgument $input -o ${input.simpleName}.filtered.bam
    """
}



process PICARD_MARKDUPLICATES {
  tag "picard markduplicates"
  container 'quay.io/biocontainers/picard:2.10.6--py35_0'

  input:
    path input

  output:
    path "*.sorted.dedup.bam", emit: alignments
    path "*.sorted.dedup.metrics.txt", emit: metrics

  script:
    """
    picard MarkDuplicates \\
      INPUT=$input \\
      OUTPUT=${input.simpleName}.dedup.bam \\
      METRICS_FILE=${input.simpleName}.dedup.metrics.txt \\
      ASSUME_SORTED=TRUE
    """
}