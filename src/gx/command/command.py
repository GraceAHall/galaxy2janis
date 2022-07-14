


from .factory import CommandFactory
from .Command import Command
from gx.gxtool.XMLToolDefinition import XMLToolDefinition



def gen_command(xmltool: XMLToolDefinition) -> Command:
    factory = CommandFactory(xmltool)
    return factory.create()



