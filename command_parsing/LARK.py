


from lark import Lark

with open('command_parsing/rules.lark', 'r') as fp:
    ruleset = fp.read()

json_parser = Lark(ruleset, start='value')

text = '{"key1": ["item0", "item1", 3.14], "key2": "value2", "key3": 5}'

print(json_parser.parse(text).pretty())
print()
