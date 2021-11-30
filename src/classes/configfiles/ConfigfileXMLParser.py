

from xml.etree import ElementTree as et

from classes.logging.Logger import Logger
from classes.configfiles.Configfile import Configfile


class ConfigfileXMLParser:
    def __init__(self, tree: et.ElementTree, tokens: dict[str, str], logger: Logger) -> None:
        self.tree = tree
        self.tokens = tokens
        self.logger = logger
        self.has_configfiles = False
        self.configfiles: list[Configfile] = []


    def parse(self) -> None:
        # currently just checks whether configfiles are present
        # if so, logs message and quits execution
        root = self.tree.getroot()
        configfiles_node = root.find('configfiles')
        if configfiles_node is not None:
            self.has_configfiles = True

        self.report_configfile_status()


    def report_configfile_status(self) -> None:
        if self.has_configfiles:
            self.logger.log(2, 'tool contains configfiles')

        