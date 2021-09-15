



from classes.datastructures.Output import Output



class OutputParser:
    def __init__(self):
        pass


    def parse(self) -> list[Output]:
        # parse params
        tree_path = []
        for node in self.tree.getroot():
            self.explore_node(node, tree_path)

        return self.param_list