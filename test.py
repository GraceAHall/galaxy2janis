

from Cheetah.Template import Template


partial_template = """
    ## Preparing files
    #if str( $paired_unpaired.fastq_input_selector ) == "paired"
        paired
        
        
        
        
        
        
        
        
        
        
        
    #elif str( $paired_unpaired.fastq_input_selector ) == "paired_collection"
        paired_collection
        
        
        
        
        
        
        
        
        
        
        
    #elif str( $paired_unpaired.fastq_input_selector ) == "single"
        single
        
        
        
        
        
    #end if
    #if $long
        long
        
        
        
        
        
        
        
    #end if
    ## Get location for pilon installation
    pilon=`pilon --jar_dir` &&
    ## Running Unicycler
    unicycler -t "\${GALAXY_SLOTS:-4}"
    -o ./
    --verbosity 3
    --pilon_path \$pilon
    #if str( $paired_unpaired.fastq_input_selector ) == "paired"
        paired
        
    #elif str( $paired_unpaired.fastq_input_selector ) == "paired_collection"
        paired_collection
        
    #elif str( $paired_unpaired.fastq_input_selector ) == "single"
        single
    #end if
    #if $long
        long
    #end if
    ## General Unicycler Options section
    ## ----------------------------------------------------------
    --mode '$mode'
    --min_fasta_length '$min_fasta_length'
    --linear_seqs '$linear_seqs'
    #if str($min_anchor_seg_len) != ''
    --min_anchor_seg_len '$min_anchor_seg_len'
    #end if
    ## Spades Options section
    ## ----------------------------------------------------------
    $spades.no_correct
    --min_kmer_frac '$spades.min_kmer_frac'
    --max_kmer_frac '$spades.max_kmer_frac'
    #if str($spades.kmers) != ''
    --kmers '$spades.kmers'
    #end if
    --kmer_count '$spades.kmer_count'
    --depth_filter '$spades.depth_filter'
    #if $spades.largest_component
        --largest_component
    #end if
    ## Rotation Options section
    ## ----------------------------------------------------------
    $rotation.no_rotate
    #if $rotation.start_genes
        --start_genes '$rotation.start_genes'
    #end if
    --start_gene_id '$rotation.start_gene_id'
    --start_gene_cov '$rotation.start_gene_cov'
    ## Pilon Options section
    ## ----------------------------------------------------------
    $pilon.no_pilon
    #if str($pilon.min_polish_size) != ''
        --min_polish_size '$pilon.min_polish_size'
    #end if
    ## Graph cleaning Options sdection
    ## ----------------------------------------------------------
    --min_component_size '$graph_clean.min_component_size'
    --min_dead_end_size '$graph_clean.min_dead_end_size'
    ## Long Read Alignment Options
    ## ----------------------------------------------------------
    #if $lr_align.contamination
        --contamination '$lr_align.contamination'
    #end if
    --scores '${lr_align.scores}'
    #if str($lr_align.low_score) != ''
        --low_score '$lr_align.low_score'
    #end if
"""

input_dict = {
    "graph_clean": {
        "min_component_size": "1000", 
        "min_dead_end_size": "1000"
    }, 
    "linear_seqs": "0", 
    "long": {"__class__": "RuntimeValue"}, 
    "lr_align": {
        "contamination": {"__class__": "RuntimeValue"}, 
        "scores": "", 
        "low_score": None
    }, 
    "min_anchor_seg_len": None, 
    "min_fasta_length": "100", 
    "mode": "normal", 
    "paired_unpaired": {
        "__current_case__": 0, 
        "fastq_input_selector": "paired", 
        "fastq_input1": {"__class__": "RuntimeValue"}, 
        "fastq_input2": {"__class__": "RuntimeValue"}
    }, 
    "pilon": {
        "no_pilon": False, 
        "min_polish_size": "1000"
    }, 
    "rotation": {
        "start_genes": {"__class__": "RuntimeValue"}, 
        "no_rotate": False, 
        "start_gene_id": "90.0", 
        "start_gene_cov": "95.0"
    }, 
    "spades": {
        "no_correct": False, 
        "min_kmer_frac": "0.2", 
        "max_kmer_frac": "0.95", 
        "kmers": "", 
        "kmer_count": "10", 
        "depth_filter": "0.25", 
        "largest_component": False
    }, 
    "__page__": None, 
    "__rerun_remap_job_id__": None
}

t = Template(partial_template, searchList=[input_dict]) # type: ignore
print(t)
