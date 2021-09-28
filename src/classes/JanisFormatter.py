


from classes.Logger import Logger
from classes.datastructures.Output import Output
from classes.datastructures.Params import Param
from classes.parsers.ToolParser import ToolParser

from typing import Union

class JanisFormatter:
    def __init__(self, tool: ToolParser, out_def: str) -> None:
        self.tool = tool
        self.out_def = out_def
        self.logger = tool.logger # bad awful yuck
        self.inputs: list[str] = []
        self.outputs: list[str] = []
        self.command: list[str] = []
        self.metadata: list[str] = []
        
        self.janis_import_dict: dict[str, set[str]] = {
            'janis_core': {
                'CommandToolBuilder', 
                'ToolInput', 
                'ToolOutput'
            },
            'bioinformatics_types': set(),
            'common_types': set(),
            'unix_types': set(),
        }

        self.datatype_categories = {
            "BAI": 'bioinformatics_types',
            "BAM": 'bioinformatics_types',
            "bed": 'bioinformatics_types',
            "BedGz": 'bioinformatics_types',
            "BedTABIX": 'bioinformatics_types',
            "Boolean": 'common_types',
            "CompressedTarFile": 'unix_types',
            "CRAI": 'bioinformatics_types',
            "CRAM": 'bioinformatics_types',
            "CramPair": 'bioinformatics_types',
            "csv": 'unix_types',
            "Directory": 'common_types',
            "Double": 'common_types',
            "Fasta": 'bioinformatics_types',
            "FastaBwa": 'bioinformatics_types',
            "FastaFai": 'bioinformatics_types',
            "FastaGz": 'bioinformatics_types',
            "FastaGzBwa": 'bioinformatics_types',
            "FastaGzFai": 'bioinformatics_types',
            "FastaGzWithIndexes": 'bioinformatics_types',
            "FastaWithIndexes": 'bioinformatics_types',
            "FastDict": 'bioinformatics_types',
            "FastGzDict": 'bioinformatics_types',
            "Fastq": 'bioinformatics_types',
            "FastqGz": 'bioinformatics_types',
            "File": 'common_types',
            "Filename": 'common_types',
            "Float": 'common_types',
            "Gzip": 'unix_types',
            "HtmlFile": 'unix_types',
            "IndexedBam": 'bioinformatics_types',
            "Integer": 'common_types',
            "jsonFile": 'unix_types',
            "KallistoIdx": 'bioinformatics_types',
            "SAM": 'bioinformatics_types',
            "Stdout": 'common_types',
            "String": 'common_types',
            "TarFile": 'unix_types',
            "TextFile": 'unix_types',
            "tsv": 'unix_types',
            "VCF": 'bioinformatics_types',
            "CompressedVCF": 'bioinformatics_types',
            "IndexedVCF": 'bioinformatics_types',
            "CompressedIndexedVCF": 'bioinformatics_types',
            "WhisperIdx": 'bioinformatics_types',
            "Zip": 'unix_types'
        }

        self.gx_janis_datatype_mapping = {
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


    def format(self) -> None:
        self.inputs = self.gen_inputs()
        self.outputs = self.gen_outputs()
        self.imports = self.gen_imports()
        self.command = self.gen_command()
        self.commandtool = self.gen_commandtool()
        self.main_call = self.gen_main_call()
        

    def gen_inputs(self) -> list[str]:
        """
        each str elem in out list is a tool input        
        """
        inputs = []

        for param in self.tool.params:
            if param.validated:  # TODO this will rule out complex param syntax at this stage
                param_string = self.format_param_to_string(param) 
                inputs.append(param_string)

        return inputs
        

    def update_datatype_imports(self, entity: Union[Param, Output]) -> None:
        """
        bad naming here. entity because it could be a Param or Output. 
        either way have to update the import list for the datatypes it needs.
        """
        dtype_list = entity.janis_type.split(',')
        for dtype in dtype_list:
            category = self.datatype_categories[dtype]
            self.janis_import_dict[category].add(dtype)


    def format_param_to_string(self, param: Param) -> str:
        """
        ToolInput(
            'fastq1',
            Fastq,
            prefix='--in1',
            doc="First fastq input. If paired end, input2 is used for the other PE fastq"
        )
        """
        # TODO: move this to ParamPostProcessing?
        param.janis_type = self.convert_types_to_janis(param)

        out_str = '\tToolInput(\n'
        out_str += f'\t\t"{param.name}",\n'
        out_str += f'\t\t{param.janis_type},\n'
        out_str += f'\t\tprefix="{param.prefix or ""}",\n'
        out_str += f'\t\tdefault="{param.default_value}",\n'
        out_str += f'\t\tdoc="{param.help_text}"\n'
        out_str += '\t),\n'

        return out_str
        

    def convert_types_to_janis(self, param: Param) -> str:
        """
        converts galaxy extensions to janis. 
        also standardises exts: fastqsanger -> Fastq, fastq -> Fastq. 
        """
        # TODO handle the Union types - for now
        # fallback to most common type?

        # TODO this has to check optional status!
        # TODO has to check whether is an array! 

        self.convert_type_list(param)
        self.update_datatype_imports(param)
        out_str = self.format_janis_typestr(param)

        return out_str


    def convert_type_list(self, param: Param) -> None:
        out_list = [] 
        galaxy_types = param.galaxy_type.split(',') 
        for gtype in galaxy_types:
            if gtype in self.gx_janis_datatype_mapping:
                ext = self.gx_janis_datatype_mapping[gtype]
            else:
                self.logger.log(1, f'datatype conversion failed: {gtype}')
                ext = 'File'
            out_list.append(ext)

        param.janis_type = ','.join(out_list)


    # depricated?
    def check_conversion(self, param: Param) -> None:
        # check if conversion was fully successful
        for jtype in param.janis_type:
            if jtype == 'none':
                status = 1
                break


    # TODO ADD OPTIONALITY, ARRAYS
    def format_janis_typestr(self, param: Param) -> str:
        # init
        out_str = ''
        
        # add janis type list
        type_list = param.janis_type.split(',')
        for jtype in type_list:
            out_str += (f'{jtype}, ')
        
        # strip trailing comma
        out_str = out_str.rstrip(', ')

        # union wrapping needed? 
        if len(type_list) > 1:
            out_str = f'Union[{out_str}]'

        return out_str



    def gen_outputs(self) -> list[str]:
        """
        each str elem in out list is tool output
        identifier: str,
        datatype: Optional[ParseableType] = None,
        source: Union[Selector, ConnectionSource]=None # or List[Selector, ConnectionSource]
        output_folder: Union[str, Selector, List[Union[str, Selector]]] = None,
        output_name: Union[bool, str, Selector, ConnectionSource] = True, # let janis decide output name
        extension: Optional[str] = None, # file extension if janis names file
        doc: Union[str, OutputDocumentation] = None,
        """
        outputs = []

        for output in self.tool.outputs:
            output_string = self.format_output_to_string(output) 
            self.update_component_imports(output)
            outputs.append(output_string)

        return outputs
        

    def format_output_to_string(self, output: Output) -> str:
        """
        formats outputs into janis tooldef string
        """
        output.janis_type = self.convert_types_to_janis(output)

        out_str = '\tToolOutput(\n'
        out_str += f'\t\t"{output.name}",\n'
        out_str += f'\t\t{output.janis_type},\n'

        # TODO this isnt strictly correct
        out_str += f'\t\tselector={output.selector}("{output.selector_contents}"),\n'
        out_str += f'\t\tdoc="{output.help_text}"\n'
        out_str += '\t),\n'

        return out_str


    def update_component_imports(self, output: Output) -> None:
        """
        need to add the selector type to imports too!
        """
        self.janis_import_dict['janis_core'].add(output.selector)


    def gen_imports(self) -> list[str]:
        out_str = ''
        jid = self.janis_import_dict
        
        # janis core
        if len(jid['janis_core']) > 0:
            modules = ', '.join(jid['janis_core'])
            out_str += f'\nfrom janis_core import {modules}\n'

        # bioinformatics types
        if len(jid['bioinformatics_types']) > 0:
            modules = ', '.join(jid['bioinformatics_types'])
            out_str += f'\nfrom janis_bioinformatics.data_types import {modules}\n'

        # common types
        if len(jid['common_types']) > 0:
            modules = ', '.join(jid['common_types'])
            out_str += f'\nfrom janis_core.types.common_data_types import {modules}\n'

        # unix types
        if len(jid['unix_types']) > 0:
            out_str += '\n'
            for module in jid['unix_types']:
                if module == 'TextFile':  # who even wrote janis
                    out_str += f'from janis_unix.data_types.text import TextFile\n'
                else:
                    out_str += f'from janis_unix.data_types.{module.lower()} import {module}\n'

        return out_str


    def gen_command(self) -> list[str]:
        """
        each str elem in out list is tool output
        """
        return self.tool.base_command
        

    def gen_commandtool(self) -> list[str]:
        """
        each str elem in out list is tool output
        """
        toolname = self.tool.tool_id.replace('-', '_')
        container = self.tool.container
        version = self.tool.tool_version

        out_str = f'\n{toolname} = CommandToolBuilder(\n'
        out_str += f'\ttool="{toolname}",\n'
        out_str += f'\tbase_command=["{self.command}"],\n'
        out_str += f'\tinputs=inputs,\n'
        out_str += f'\toutputs=outputs,\n'
        out_str += f'\tcontainer="{container}",\n'
        out_str += f'\tversion="{version}",\n'
        # TODO here add requirements (biocontainer for conda pkg or container + version)
        out_str += ')\n'

        return out_str

    
    def gen_main_call(self) -> str:
        """
        generates the __main__ call to translate to wdl on program exec
        """
        toolname = self.tool.tool_id.replace('-', '_')

        out_str = '\n'
        out_str += 'if __name__ == "__main__":\n'
        out_str += f'\t{toolname}().translate(\n'
        out_str += '\t\t"wdl", to_console=True\n'
        out_str += '\t)'
        return out_str
        

    def write(self) -> None:
        """
        writes the text to tool def fil

        """

        with open(self.out_def, 'w') as fp:
            fp.write(self.imports + '\n\n')

            fp.write('inputs = [\n')
            for inp in self.inputs:
                fp.write(inp)
            fp.write(']\n\n')

            fp.write('outputs = [\n')
            for out in self.outputs:
                fp.write(out)
            fp.write(']\n\n')

            fp.write(self.commandtool + '\n')
            fp.write(self.main_call + '\n')



