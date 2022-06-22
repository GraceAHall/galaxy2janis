


from shellparser.CommandFactory import CommandFactory
from shellparser.Command import Command
from gx.xmltool.XMLToolDefinition import XMLToolDefinition



def gen_command(xmltool: XMLToolDefinition) -> Command:
    factory = CommandFactory(xmltool)
    return factory.create()

