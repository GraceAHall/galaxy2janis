

from typing import Optional
from tool.parsing.GalaxyOutput import GalaxyOutput



class WildcardFetcher:
    def get(self, gxout: GalaxyOutput) -> Optional[str]:
        """gets the file collection wildcard from the output if relevant"""
        if gxout.output_type == 'data' and gxout.from_work_dir:
            return str(gxout.from_work_dir)
        if gxout.dataset_collector_descriptions:
            return self.get_discover(gxout)

    def get_discover(self, gxout: GalaxyOutput) -> str:
        coll = gxout.dataset_collector_descriptions[0]
        return f'{coll.directory}/{coll.pattern}'

        
        
        
        

                
