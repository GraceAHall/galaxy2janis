


from collections import Counter


gx_janis_datatype_mapping = {
    "bai": "BAI",
    "bam": "BAM",
    "bed": "bed",
    "bed.gz": "BedGz",
    "tabix": "BedTABIX",
    "bool": "Boolean",
    "boolean": "Boolean",
    "tar.gz": "CompressedTarFile",
    "brai": "CRAI",
    "cram": "CRAM",
    "CramPair": "CramPair",
    "csv": "csv",
    "directory": "Directory",
    "double": "Double",
    "fa": "Fasta",
    "fna": "Fasta",
    "fasta": "Fasta",
    "FastaBwa": "FastaBwa",  # TODO
    "fai": "FastaFai",  
    "fasta.gz": "FastaGz",
    "FastaGzBwa": "FastaGzBwa",  # TODO
    "FastaGzFai": "FastaGzFai",  # TODO
    "FastaGzWithIndexes": "FastaGzWithIndexes",
    "FastaWithIndexes": "FastaWithIndexes",
    "FastDict": "FastDict",
    "FastGzDict": "FastGzDict",
    "fq": "Fastq",
    "fastq": "Fastq",
    "fastqsanger": "Fastq",
    "fastqillumina": "Fastq",
    "fastq.gz": "FastqGz",
    "fastqsanger.gz": "FastqGz",
    "fastqillumina.gz": "FastqGz",
    "file": "File",
    "filename": "Filename",
    "float": "Float",
    "gz": "Gzip",
    "html": "HtmlFile",
    "IndexedBam": "IndexedBam",  # TODO
    "integer": "Integer",
    "json": "jsonFile",
    "kallisto.idx": "KallistoIdx",
    "sam": "SAM",
    "stdout": "Stdout",
    "color": "String",
    "string": "String",
    "text": "String",
    "tar": "TarFile",
    "txt": "TextFile",
    "tsv": "tsv",
    "vcf": "VCF",
    "vcf_bgzip": "CompressedVCF",
    "IndexedVCF": "IndexedVCF",  # TODO
    "CompressedIndexedVCF": "CompressedIndexedVCF", # TODO?
    "WhisperIdx": "WhisperIdx", # TODO
    "zip": "Zip"
}


def get_common_extension(the_list: list[str]) -> str: 
    """
    identifies whether a list of items has a common extension. 
    all items must share the same extension. 
    will return the extension if true, else will return ""
    """
    
    try:
        ext_list = [item.rsplit('.', 1)[1] for item in the_list]
    except IndexError:
        return ''  # at least one item has no extension

    ext_list = convert_extensions(ext_list)
    ext_counter = Counter(ext_list)
        
    if len(ext_counter) == 1:  
        ext, count = ext_counter.popitem() 
        if count == len(the_list):  # does every item have the extension?
            return ext 

    return ""
    

def convert_extensions(the_list: list[str]) -> list[str]:
    """
    converts galaxy extensions to janis. 
    also standardises exts: fastqsanger -> Fastq, fastq -> Fastq. 
    """
    out_list = []
    for item in the_list:
        if item in gx_janis_datatype_mapping:
            ext = gx_janis_datatype_mapping[item]
        else:
            ext = 'String'  # fallback pretty bad but yeah. 
        out_list.append(ext)

    return out_list