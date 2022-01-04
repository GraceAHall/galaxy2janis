

import sys 

from classes.tool.ToolParser import ToolParser
from classes.execution import startup

# main entry point
def main():
    esettings = startup(sys.argv[1:])
    tp = ToolParser(esettings)
    tp.parse()


if __name__ == '__main__':
    main()






    

