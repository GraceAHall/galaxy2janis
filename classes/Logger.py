

class Logger:
    def __init__(self) -> None:
        self.map_level = {
            0: "INFO",
            1: "WARN",
            2: "ERROR",
        }


    def log(self, level: int, message: str) -> None:
        log_type = self.map_level(level)
        print(f'gxtool2janis: [{log_type}]: {message}')