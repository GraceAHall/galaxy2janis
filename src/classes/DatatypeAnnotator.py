




import json
from typing import Union, Optional


from classes.datastructures.Command import Positional, Flag, Option, Command, TokenTypes, Token


class DatatypeAnnotator:
    def __init__(self, command: Command):
        self.command = command
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


    def annotate_positional(self, the_positional) -> None:
        # can be string, int, float, file type (fasta, html etc)   
        the_positional.datatypes = self.get_token_datatypes(the_positional.token)


    def get_token_datatypes(self, the_token: Token) -> list[str]:
        """
        TODO note here pls
        """
        # galaxy variables
        if the_token.type in [TokenTypes.GX_PARAM, TokenTypes.GX_OUT]:
            return self.infer_types_from_gx(the_token)

        # strings
        elif the_token.type in [TokenTypes.RAW_STRING, TokenTypes.QUOTED_STRING]:
            # return string or file type inferred from .extension
            ext_types = self.infer_types_from_ext(the_token)
            if len(ext_types) > 0:
                return ext_types
            return ['String']
        
        # numeric
        elif the_token.type == [TokenTypes.RAW_NUM, TokenTypes.QUOTED_NUM]:
            # return int or float
            return self.infer_types_from_numeric(the_token)
        
        # linux
        elif the_token.type == TokenTypes.LINUX_OP:
            return ['LinuxOp']
        
        # linux
        elif the_token.type == TokenTypes.GX_KEYWORD:
            return ['GalaxyKW']


    def infer_types_from_gx(self, the_token: Token) -> list[str]:
        # for gx params or gx outputs
        # gx params and outputs already have type annotation
        # extracted from the xml

        if the_token.type == TokenTypes.GX_PARAM:
            gx_var = the_token.value  
            gx_types = gx_var.galaxy_type.split(',')

        elif the_token.type == TokenTypes.GX_OUT:
            gx_out = the_token.value
            gx_types = the_token.value.galaxy_type.split(',')

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
        NOTE this is where some safety features are implemented
        if the list of janis types is empty, just set as 'File'
        """
        if len(types) == 0:
            return 'File'
            
        elif len(types) == 1:
            return types[0]

        # if more than 1 type
        types.sort(key = lambda x: len(x))
        return types[0]


    def infer_types_from_ext(self, the_token: Token) -> list[str]:
        the_string = the_token.value
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
        the_string = the_token.value
        if '.' in the_string:
            return ['Float']
        return ['Integer']


    def annotate_flag(self, the_flag) -> None:
        # priority list
        # gx param / gx out
        # 

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
            if token_type in [TokenTypes.GX_PARAM, TokenTypes.GX_OUT] and len(datatypes) > 0:
                from_galaxy.append(datatypes)
        
        from_numeric = [dt for tt, dt in source_datatypes if tt in [TokenTypes.RAW_NUM, TokenTypes.QUOTED_NUM]]    
        from_string = [dt for tt, dt in source_datatypes if tt in [TokenTypes.RAW_STRING, TokenTypes.QUOTED_STRING]]    

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

        print()

    
    """
    def convert_type_list(self, type_list) -> None:
        out_list = set()

        galaxy_types = param.galaxy_type.split(',') 
        for gtype in galaxy_types:
            if gtype in self.gx_janis_datatype_mapping:
                ext = self.gx_janis_datatype_mapping[gtype]
            else:
                self.logger.log(1, f'datatype conversion failed: {gtype}')
                ext = 'File'
            out_list.add(ext)

        param.janis_type = ','.join(out_list)


    def get_janis_type(self) -> str:
        out_str = ''

        # get janis types (already converted from galaxy)
        type_list = list(set(param.janis_type.split(',')))

        # reduce to single type 
        if len(type_list) > 1:
            type_list = self.reduce_datatype(type_list)
        
        return type_list[0]


    def reduce_datatype(self, type_list: list[str]) -> list[str]:
        " ""
        selects a single datatype from list of types. 
        should be either 
            - the most accessible form of the datatype (raw rather than gz)
            - the common format (bam rather than sam)
            - anything except 'File' fallback
        " ""
        # remove 'File' type
        type_list = [t for t in type_list if t != 'File']
        
        # only the 'File' type was present
        if len(type_list) == 0:
            return ['File']

        # if had 2 types where 1 was 'File'
        elif len(type_list) == 1:
            return type_list

        else:
            # remove basic types (String, Integer etc) like above 'File'?
            pass

        # TODO change this laziness. just sorting alphabetically and on length. is this even stable sort? 
        type_list.sort()
        type_list.sort(key=lambda x: len(x))

        return [type_list[0]]


    """

