

from classes.MacroExpander import MacroExpander
import xml.etree.ElementTree as et


# not working. 
def test_macro_expansion_file() -> None:
    me = MacroExpander('tools/busco', 'busco.xml')
    me.collect()
    me.expand()

    me_tree = me.tree
    target_tree = et.parse('tests/test_data/macro_test.xml')

    assert(me_tree == target_tree)
    

def test_token_resolution_file() -> None:
    pass