


from runtime.settings import ExecutionSettings
from galaxy_interaction.GalaxyManager import GalaxyManager


def load_manager(esettings: ExecutionSettings) -> GalaxyManager:
    return GalaxyManager(esettings)