

import sys

class Logger:
    def __init__(self, logfile: str) -> None:
        self.logfile = logfile
        self.map_level = {
            0: "INFO",
            1: "WARN",
            2: "ERROR",
        }

        self.message_log = []


    """

    BOOKMARK TODO HERE
    - DETOUR: conversion to janis
    - types - WARN []

    """


    def log(self, level: int, message: str) -> None:
        log_type = self.map_level[level]
        message = f'{log_type},{message}\n'
        
        if message not in self.message_log:
            self.message_log.append(message)
            self.update_logs(message)
        
        if level == 2:
            sys.exit()


    # TODO delete all files in the outdir at program start
    def update_logs(self, message: str) -> None:
        with open(f'{self.logfile}', 'a') as fp:
            fp.write(message)


