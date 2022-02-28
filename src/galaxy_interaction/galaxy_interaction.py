


from startup.ExeSettings import ToolExeSettings
from galaxy_interaction.GalaxyManager import GalaxyManager


def load_manager(esettings: ToolExeSettings) -> GalaxyManager:
    return GalaxyManager(esettings)