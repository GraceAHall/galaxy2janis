

class Logger:
    def __init__(self) -> None:
        self.map_level = {
            0: "INFO",
            1: "WARN",
            2: "ERROR",
        }

        self.message_log = []


    def log(self, level: int, message: str) -> None:
        log_type = self.map_level[level]
        message = f'gxtool2janis: [{log_type}]: {message}'
        
        if message not in self.message_log:
            self.message_log.append(message)
            print(message)


    def log_unknown_type(self, level: int, datatype: str) -> None:
        log_type = self.map_level[level]
        message = f'gxtool2janis: [{log_type}]: cannot parse datatype: "{datatype}". Falling back to "String"'

        if message not in self.message_log:
            self.message_log.append(message)
            print(message)
