


from lark import Lark
from lark.indenter import Indenter


with open('command_parsing/rules.lark', 'r') as fp:
    ruleset = fp.read()


text1 = '{"key1": ["the first item", "item1", 3.14], "key2": true, "key3": 5}'


text2 = """
--cpu \${GALAXY_SLOTS:-4}
--update-data
--evalue ${adv.evalue}
--limit ${adv.limit}
--in '${input}'
--mode='${busco_mode.mode}'
--out busco_galaxy
--out:busco_galaxy
"""


text3 = """
[ "hello", "there", 5]
"""

text4 = """
#if this:
    that
#end if
"""


# json_parser = Lark(ruleset, start='value')
# print(json_parser.parse(text1).pretty())
# print()


from lark import Transformer

with open('command_parsing/rules.lark', 'r') as fp:
    ruleset = fp.read()


class MyTransformer(Transformer):
    def dict(self, items):
        return dict(items)    
    
    def list(self, items):
        return list(items)

    def pair(self, kv_pair):
        k, v = kv_pair
        return k, v


class TreeToJson(Transformer):
    def string(self, str_token_list):
        print(str_token_list[0][1:-1])
        return str_token_list[0][1:-1]  # [1:-1] strips quotes

    def number(self, n):
        return float(n[0])

    list = list
    pair = tuple
    dict = dict

    
    #null = lambda self, _: None

    def null(self, x):
        return None
    
    #true = lambda self, _: True

    def true(self, *args, **kwargs):
        return True
    
    false = lambda self, _: False



json_parser = Lark(ruleset, start='value')
tree = json_parser.parse(text1)
print(tree)
myjson = TreeToJson().transform(tree)
print()



