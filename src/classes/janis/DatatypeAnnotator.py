




import json
from typing import Union, Optional
from classes.outputs.Outputs import Output

from classes.params.ParamRegister import ParamRegister
from classes.outputs.OutputRegister import OutputRegister
from classes.command.Command import Positional, Flag, Option, Command, TokenType, Token
from classes.Logger import Logger


class DatatypeAnnotator:
    def __init__(self, command: Command, param_register: ParamRegister, out_register: OutputRegister, logger: Logger):
        self.command = command
        self.param_register = param_register
        self.out_register = out_register
        self.logger = logger
        self.init_datastructures()


    def init_datastructures(self) -> None:
        self.gx_parsed = self.load_gx_parsed_types()
        self.gx_capitalisation_map = self.create_capitalisation_map()
        self.ext_to_gx = self.invert_dict(self.gx_parsed)
        self.gx_janis_mapping = self.load_gx_janis_mapping()
        self.janis_categories = self.load_janis_category_map()


    def load_gx_parsed_types(self) -> set[str]:
        # annoying capitalisations
        with open('src/data/galaxy_types_register.json', 'r') as fp:
            return json.load(fp)


    def create_capitalisation_map(self) -> dict[str, str]:
        """
        annoying but has to be done
        the capitalisation changes between tool xml and galaxy type definitions
        need to know the reverse mapping to annotate with correct type
        """
        out = {}
        for gtype in self.gx_parsed.keys():
            out[gtype.lower()] = gtype
        return out


    def invert_dict(self, the_dict: dict[str, list[str]]) -> dict[str, str]:
        out = {}
        for gtype, exts in the_dict.items():
            for ext in exts:
                out[ext] = gtype
        return out


    def load_gx_janis_mapping(self) -> dict[str, str]:
        mapping = {}

        with open('src/data/galaxy_janis_datatypes_mapping.tsv', 'r') as fp:
            lines = fp.readlines()
            lines = [ln.strip('\n').strip(' ') for ln in lines]
            lines = [ln.split() for ln in lines]
            for source, dest in lines:
                mapping[source] = dest

        return mapping
    
    
    def load_janis_category_map(self) -> dict[str, str]:
        mapping = {}

        with open('src/data/datatype_categories.tsv', 'r') as fp:
            lines = fp.readlines()
            lines = [ln.strip('\n').strip(' ') for ln in lines]
            lines = [ln.split() for ln in lines]
            for source, dest in lines:
                mapping[source] = dest

        return mapping


    def annotate(self) -> None:
        for item in self.command.positionals.values():
            self.annotate_positional(item)

        for item in self.command.flags.values():
            self.annotate_flag(item)

        for item in self.command.options.values():
            self.annotate_option(item)
        
        for item in self.out_register.get_outputs():
            self.annotate_output(item)


    def annotate_positional(self, the_positional) -> None:
        # can be string, int, float, file type (fasta, html etc)   
        the_positional.datatypes = self.get_token_datatypes(the_positional.token)


    def get_token_datatypes(self, the_token: Token) -> list[str]:
        """
        TODO note here pls 
        DONT TELL ME WHAT TO DO?
        """
        # galaxy variables
        if the_token.type in [TokenType.GX_PARAM, TokenType.GX_OUT]:
            return self.infer_types_from_gx(the_token)

        # strings
        elif the_token.type in [TokenType.RAW_STRING, TokenType.QUOTED_STRING]:
            # return string or file type inferred from .extension
            ext_types = self.infer_types_from_ext(the_token.text)
            if len(ext_types) > 0:
                return ext_types
            return ['String']
        
        # numeric
        elif the_token.type == [TokenType.RAW_NUM, TokenType.QUOTED_NUM]:
            # return int or float
            return self.infer_types_from_numeric(the_token)
        
        # linux
        elif the_token.type == TokenType.LINUX_OP:
            return ['LinuxOp']
        
        # linux
        elif the_token.type == TokenType.GX_KEYWORD:
            return ['GalaxyKW']


    def infer_types_from_gx(self, the_token: Token) -> list[str]:
        """
        for gx params or gx outputs
        gx params and outputs already have type annotation
        extracted from the xml
        """

        if the_token.type == TokenType.GX_PARAM:
            param = self.param_register.get(the_token.gx_ref)
            gx_types = param.galaxy_type.split(',')

        elif the_token.type == TokenType.GX_OUT:
            output = self.out_register.get(the_token.gx_ref)
            gx_types = output.galaxy_type.split(',')

        janis_types = self.cast_to_janis(gx_types)
        #final_type = self.get_simplest_type(janis_types)
        return janis_types


    def cast_to_janis(self, types: list[str]) -> list[str]:
        # try gx_janis_mapping first
        # then gx_parsed

        out = []
        for t in types:
            if t in self.gx_janis_mapping:
                out.append(self.gx_janis_mapping[t])
            
            elif t in self.gx_capitalisation_map:
                out.append(self.gx_capitalisation_map[t])
        
        return out


    def get_simplest_type(self, types: list[str]) -> str:
        """
        
        """
        if len(types) == 0:
            return 'File'
            
        elif len(types) == 1:
            return types[0]

        # if more than 1 type
        types.sort(key = lambda x: len(x))
        return types[0]


    def infer_types_from_ext(self, the_string: str) -> list[str]:
        hits = []

        components = the_string.split('.')
        if len(components) > 1:
            for i in range(1, len(components)):
                ext = '.'.join(components[i:])
                if ext in self.ext_to_gx:
                    hits.append(self.ext_to_gx[ext])

        return hits


    def infer_types_from_numeric(self, the_token: Token) -> list[str]:
        # check string against 
        the_string = the_token.text
        if '.' in the_string:
            return ['Float']
        return ['Integer']


    def annotate_flag(self, the_flag) -> None:
        # priority list
        # gx param / gx out

        source_datatypes = []

        for token in the_flag.sources:
            datatypes = self.get_token_datatypes(token)
            source_datatypes.append([token.type, datatypes])

        the_flag.datatypes = self.select_datatypes_source(source_datatypes)
        
        print()


    def select_datatypes_source(self, source_datatypes) -> list[str]:  # type: ignore
        """
        flags or option can have multiple references in the command string
        and therefore be set from multiple tokens
        some tokens (ie GX_PARAM or GX_OUT) are more informative of the real type(s)
        this func selects the best source to annotate types from
        """

        from_galaxy = []
        for token_type, datatypes in source_datatypes:
            if token_type in [TokenType.GX_PARAM, TokenType.GX_OUT] and len(datatypes) > 0:
                from_galaxy.append(datatypes)
        
        from_numeric = [dt for tt, dt in source_datatypes if tt in [TokenType.RAW_NUM, TokenType.QUOTED_NUM]]    
        from_string = [dt for tt, dt in source_datatypes if tt in [TokenType.RAW_STRING, TokenType.QUOTED_STRING]]    

        # galaxy is best 
        if len(from_galaxy) > 0:
            return from_galaxy[0] # hopefully just 1 galaxy obj ref

        # then numeric
        elif len(from_numeric) > 0:
            return from_numeric[0]
        
        # then string
        if len(from_string) > 0:
            return from_string[0]
        
        # don't care about the rest. equal importance. 
        return source_datatypes[0][1]

  
    def annotate_option(self, the_option) -> None:
        """
        copy of annotate_flag()
        """
        source_datatypes = []

        for token in the_option.sources:
            datatypes = self.get_token_datatypes(token)
            source_datatypes.append([token.type, datatypes])

        the_option.datatypes = self.select_datatypes_source(source_datatypes)


    def annotate_output(self, the_output: Output) -> None:
        """
        a little different to the others. runs on a galaxy output obj not tokens
        """
        the_output.datatypes = self.get_output_datatype(the_output)


    def get_output_datatype(self, the_output: Output) -> list[str]:
        # try from galaxy_type first
        if the_output.galaxy_type != '':
            gx_types = the_output.galaxy_type.split(',')
            return self.cast_to_janis(gx_types)

        # then from the extension on the selector contents
        ext_types = self.infer_types_from_ext(the_output.selector_contents)
        if len(ext_types) > 0:
            # ext_types returns parsed galaxy types
            return ext_types

        # fallback        
        return ['File']
