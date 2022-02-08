


from logger.errors import ParamNotSupportedError
from tool.parsing.GalaxyOutput import GalaxyOutput


class DatatypeFetcher:
    def get(self, gxout: GalaxyOutput) -> list[str]:
        match gxout.output_type:
            case 'data':
                if gxout.format and gxout.format != 'data':
                    return str(gxout.format).split(',')
            case 'collection':
                if gxout.default_format and gxout.default_format != 'data':
                    return str(gxout.default_format).split(',')
            case _:
                raise ParamNotSupportedError()
        
        if gxout.dataset_collector_descriptions:
            return self.get_discover(gxout)
        return ['data']
        

    def get_discover(self, gxout: GalaxyOutput) -> list[str]:
        coll = gxout.dataset_collector_descriptions[0]
        if coll.default_ext:
            return str(coll.default_ext).split(',')
        return ['data']
        
        