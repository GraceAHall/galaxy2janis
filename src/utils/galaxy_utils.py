


from collections import Counter
from xml.etree import ElementTree as et

# TODO write tests for all these

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



# ---- conversion to janis types ---- #

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
            ext = 'File'  # fallback pretty bad but yeah. 
        out_list.append(ext)

    return out_list



# ---- list operations ---- #

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


def is_string_list(the_list: list[str]) -> bool:
    """
    string list is list of values which do not look like prefixes ('-' at start)
    TODO awful. refactor.
    """
    for item in the_list:
        val = item['value']
        if val == '' or val[0] == '-':
            return False
    if len(the_list) == 2:
        if the_list[0]['value'] in ['true', 'false'] and the_list[1]['value'] in ['true', 'false']:
            return False
    return True


def is_flag_list(options: list[str]) -> bool:
    outcome = True

    # check all the options start with '-'
    for opt in options:
        if not opt['value'].startswith('-'):
            outcome = False
            break

    # ensure its just not because negative numbers
    try: 
        [float(opt['value']) for opt in options] 
        outcome = False  # if reaches this point, all opts are float castable
    except ValueError:
        pass

    return outcome


def cast_list(the_list: list[str]) -> str:
    """
    identifies whether all list items can be cast to a common datatype.
    currently just float and int
    """
    castable_types = []

    if can_cast_to_float(the_list):
        castable_types.append('Float')
    elif can_cast_to_int(the_list):
        castable_types.append('Integer')

    if 'Float' in castable_types:
        if 'Integer' in castable_types:
            return 'Integer'
        else:
            return 'Float'

    return ''


# write test
def can_cast_to_float(the_list: list[str]) -> bool:
    # each item is empty
    if all([elem == '' for elem in the_list]):
        return False

    # check if any can't be cast to float    
    for item in the_list:
        try:
            float(item)
        except ValueError:
            return False
    return True 


def can_cast_to_int(the_list: list[str]) -> bool:
    for item in the_list:
        if item[0] in ('-', '+'):
            item = item[1:]

        if not item.isdigit():
            return False

    return True 
    



