




import yaml
from typing import Optional
#from classes.outputs.Outputs import Output
from galaxy.tool_util.parser.output_objects import ToolOutput

from classes.params.ParamRegister import ParamRegister
from classes.outputs.OutputRegister import OutputRegister
from classes.command.Command import Positional, Flag, Option, Command, TokenType, Token
from classes.logging.Logger import Logger
from classes.tool.Tool import Tool

class DatatypeAnnotator:
    def __init__(self, tool: Tool, logger: Logger):
        self.tool = tool
        self.logger = logger
        self.init_datastructures()


    def init_datastructures(self) -> None:
        self.format_datatype_map = self.load_yaml('src/data/gxformat_combined_types.yaml')
        self.ext_to_format_map = self.index_by_ext(self.format_datatype_map)
    

    def load_yaml(self, filepath: str) -> dict[str, dict[str, str]]:
        """
        func loads the combined datatype yaml then converts it to dict with format as keys
        provides structue where we can search all the galaxy and janis types given what we see
        in galaxy 'format' attributes.
        """
        with open(filepath, 'r') as fp:
            datatypes = yaml.safe_load(fp)
        
        format_datatype_map = {}

        for dtype in datatypes['types']:
            # add new elem if not exists
            if dtype['format'] not in format_datatype_map:
                format_datatype_map[dtype['format']] = []
            
            # add this type
            format_datatype_map[dtype['format']].append(dtype)

        return format_datatype_map


    def index_by_ext(self, format_datatype_map: dict[str, dict[str, str]]) -> dict[str, str]:
        """
        maps ext -> list of datatypes (janis / galaxy) 
        this way can look up a file extension, and get the gxformats that use that type
        can then use self.format_datatype_map to get the actual janis and galaxy type info 
        """
        ext_format_map = {}
        for gxformat, dtype_list in format_datatype_map.items():
            # get all exts from galaxy + janis types of that gxformat
            exts = set()
            for dtype in dtype_list:
                if dtype['extensions'] is not None:
                    dtype_exts = dtype['extensions'].split(',')
                    exts.update(dtype_exts)
            
            # for each ext, add as key to ext_format_map or append datatype to that key
            for ext in list(exts):
                # make entry if not exists
                if ext not in ext_format_map:
                    ext_format_map[ext] = []
                # append gxformat
                ext_format_map[ext].append(gxformat)

        return ext_format_map


    # now the datastructures are initialised, here are some methods
    # to access types given gxformat or extension
    def get_datatype_by_format(self, gxformat: str) -> Optional[dict[str, str]]:
        if gxformat in self.format_datatype_map:
            datatypes = self.format_datatype_map[gxformat]

            if len(datatypes) == 0:
                return None
            
            if len(datatypes) > 1:            
                for dtype in datatypes:
                    if dtype['source'] == 'janis':
                        return dtype

            return datatypes[0]
        
        return None
    

    # def get_datatype_by_ext(self, ext: str) -> Optional[dict[str, str]]:
    #     if ext in self.ext_to_format_map:
    #         gxformat_list = self.ext_to_format_map[ext]

    #         if len(gxformat_list) == 0:
    #             return None

    #         best_gxformat = self.get_best_gxformat(ext, gxformat_list)
    #         return self.get_datatype_by_format(best_gxformat)

    #     return None


    def get_best_gxformat(self, ext: str, gxformat_list: list[str]) -> str:
        """
        gxformat_list will always be passed with 1+ items
        """
        gxformat_distances = []

        for gxformat in gxformat_list:
            dist = self.levenshtein(ext, gxformat)
            gxformat_distances.append((gxformat, dist))
        
        gxformat_distances.sort(key=lambda x: x[1])
        return gxformat_distances[0]


    # this is adapted from:
    # https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    @staticmethod
    def levenshtein(s1, s2):
        if len(s1) < len(s2):
            s1, s2 = s2, s1

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
                deletions = current_row[j] + 1       # than s2
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]


    def annotate(self) -> None:
        for item in self.tool.command.positionals.values():
            self.annotate_positional(item)
            self.assert_has_datatype(item)

        for item in self.tool.command.options.values():
            self.annotate_option(item)
            self.assert_has_datatype(item)
        
        for item in self.tool.out_register.get_outputs():
            self.annotate_output(item)
            self.assert_has_datatype(item)


    def annotate_positional(self, the_positional) -> None:
        # can be string, int, float, file type (fasta, html etc)   
        the_positional.datatypes = self.get_token_datatypes(the_positional.token)
        

    def assert_has_datatype(self, obj):
        datatypes = [d for d in obj.datatypes if d is not None]
        
        if len(datatypes) == 0:
            if type(obj) == Positional:
                self.logger.log(2, f'missing datatype for Positional {obj.token.text}')
            elif type(obj) == Flag or type(obj) == Option:
                self.logger.log(2, f'missing datatype for {type(obj)} {obj.sources[0].text}')
            else:
                self.logger.log(2, f'missing datatype for Output {obj.gx_var}')


    def get_token_datatypes(self, the_token: Token) -> list[dict[str, str]]:
        """
        accepts a token, works out the best datatype
        different logic depending on the token type
        """
        # galaxy variables
        if the_token.type in [TokenType.GX_PARAM, TokenType.GX_OUT]:
            return self.infer_types_from_gx(the_token)
    
        # strings
        elif the_token.type in [TokenType.RAW_STRING, TokenType.QUOTED_STRING]:
            # return string or file type inferred from .extension
            return self.infer_types_from_ext(the_token.text)
           
        # numeric
        elif the_token.type in [TokenType.RAW_NUM, TokenType.QUOTED_NUM]:
            # return int or float
            return self.infer_types_from_numeric(the_token)
        
        # linux
        elif the_token.type == TokenType.LINUX_OP:
            return [{
                'format': 'string',
                'source': 'janis',
                'classname': 'String',
                'extensions': None,
                'import_path': 'janis_core.types.common_data_types'
            }]
        

    def infer_types_from_gx(self, the_token: Token) -> list[dict[str, str]]:
        """
        for gx params or gx outputs
        gx params and outputs already have type annotation
        extracted from the xml
        always returns list, but list may have zero items
        """
        fallback_datatypes = [{
                'format': 'file',
                'source': 'janis',
                'classname': 'File',
                'extensions': None,
                'import_path': 'janis_core.types.common_data_types'
            }]

        if the_token.type == TokenType.GX_PARAM:
            param = self.tool.param_register.get(the_token.gx_ref)
            gxformat_list = param.galaxy_type.split(',')

        elif the_token.type == TokenType.GX_OUT:
            output = self.tool.out_register.get(the_token.gx_ref)
            gxformat_list = output.galaxy_type.split(',')

        if len(gxformat_list) == 0:
            return fallback_datatypes
        
        datatypes = []
        for gxformat in gxformat_list:
            dtype = self.get_datatype_by_format(gxformat)
            if dtype is not None:
                datatypes.append(dtype)
        
        if len(datatypes) == 0:
            return fallback_datatypes

        return datatypes


    def infer_types_from_ext(self, the_string: str) -> list[dict[str, str]]:
        """
        2 steps: ext -> gxformat, gxformat -> dtype
        returns the datatypes which use the identified extension
        the best extension is identified then translated to gxformat
        the longest extension is used
        ie for input.fq.gz, .fq.gz is set as best extension rather than .gz
        """
        fallback_datatypes = [{
                'format': 'string',
                'source': 'janis',
                'classname': 'String',
                'extensions': None,
                'import_path': 'janis_core.types.common_data_types'
            }]
            
        gxformat = ''
        components = the_string.split('.')
        components = [c for c in components if c != '']

        if len(components) > 1:
            for i in range(1, len(components)):
                ext = '.'.join(components[i:])
                if ext in self.ext_to_format_map:
                    gxformat = self.ext_to_format_map[ext]
                    break

        if gxformat != '':
            dtype = self.get_datatype_by_format(gxformat)
            if dtype is not None:
                return [dtype]

        return fallback_datatypes


    def infer_types_from_numeric(self, the_token: Token) -> list[dict[str, str]]:
        # check string against 
        the_string = the_token.text
        if '.' in the_string:
            return [{
                'format': 'float',
                'source': 'janis',
                'classname': 'Float',
                'extensions': None,
                'import_path': 'janis_core.types.common_data_types'
            }]

        return [{
            'format': 'integer',
            'source': 'janis',
            'classname': 'Int',
            'extensions': None,
            'import_path': 'janis_core.types.common_data_types'
        }]


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


    def annotate_output(self, the_output: ToolOutput) -> None:
        """
        a little different to the others. runs on a galaxy output obj not tokens
        """
        the_output.datatypes = self.get_output_datatype(the_output)


    def get_output_datatype(self, the_output: ToolOutput) -> list[str]:
        fallback_datatypes = [{
            'format': 'file',
            'source': 'janis',
            'classname': 'File',
            'extensions': None,
            'import_path': 'janis_core.types.common_data_types'
        }]

        datatypes = []

        # try from galaxy_type first
        if the_output.galaxy_type != '':    
            gxformat_list = the_output.galaxy_type.split(',')
            for gxformat in gxformat_list:
                dtype = self.get_datatype_by_format(gxformat)
                if dtype is not None:
                    datatypes.append(dtype)

        # then from the extension on the selector contents
        if len(datatypes) == 0:
            datatypes = self.infer_types_from_ext(the_output.selector_contents)
            datatypes = [d for d in datatypes if d['classname'] != 'String']
        
        if len(datatypes) >= 1:
            return datatypes

        # fallback   
        return fallback_datatypes     



  