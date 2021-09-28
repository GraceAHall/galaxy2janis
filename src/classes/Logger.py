

import sys

"""
Message logging for:
    - Uses configfile
    - User input required
    - Datatype cannot convert to janis
    - Input Param not found in command string (with this cause issue with output input params)
    - container requirement chose as command
    - set_environment requirement chosen as command
    - complex WildcardSelector regex
"""


class Logger:
    def __init__(self, logfile: str) -> None:
        self.logfile = logfile
        self.map_level = {
            0: "INFO",
            1: "WARN",
            2: "ERROR",
        }

        self.message_log = []


    def log(self, level: int, message: str) -> None:
        log_type = self.map_level[level]
        message = f'{log_type},{message}\n'
        
        if message not in self.message_log:
            self.message_log.append(message)
            self.update_logs(message)
        
        # if level == 2:
        #     sys.exit()


    def update_logs(self, message: str) -> None:
        with open(f'{self.logfile}', 'a') as fp:
            fp.write(message)


