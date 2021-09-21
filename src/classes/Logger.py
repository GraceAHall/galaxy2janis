

import sys

class Logger:
    def __init__(self, outdir: str) -> None:
        self.outdir = outdir
        self.map_level = {
            0: "INFO",
            1: "WARN",
            2: "ERROR",
        }

        self.message_log = []


    """
    - complex regex - WARN [done]
    - cannot find command line reference - WARN (due to current restrictions) [done]
    - uses configfile - ERROR [done]
    - needs user input (datatype / command line references) - ERROR [done]

    BOOKMARK TODO HERE
    - DETOUR: conversion to janis
    - types - WARN []
    """


    def log(self, level: int, message: str) -> None:
        log_type = self.map_level[level]
        message = f'[{log_type}] {message}\n'
        
        if message not in self.message_log:
            self.message_log.append(message)
            self.update_logs(message)
        
        if level == 2:
            sys.exit()


    # TODO delete all files in the outdir at program start
    def update_logs(self, message: str) -> None:
        with open(f'{self.outdir}/log.txt', 'a') as fp:
            fp.write(message)


