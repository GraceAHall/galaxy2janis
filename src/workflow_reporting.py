

from collections import defaultdict
from dataclasses import dataclass
import os
import sys


"""
metrics:
- was a workflow produced? - file presence
- are there UNKNOWN inputs? - log
- does it translate to cwl? - translate using janis

think that the wrapper build issue may cause a lot of failed workflow parsing runs
"""




@dataclass
class LogLine:
    """structure = '[%(levelname)s] [%(name)s] %(message)s'"""
    level: str
    logger: str
    message: str


@dataclass
class LogFile:
    path: str
    lines: list[LogLine]

    @property
    def unique_messages(self) -> list[str]:
        messages = [line.message for line in self.lines]
        return list(set(messages))

    @property
    def status(self) -> str:
        level_map: dict[str, int] = {
            'OK': 10,
            'WARNING': 30,
            'ERROR': 40,
            'CRITICAL': 50,
        }
        level_map_reverse: dict[int, str] = {val: key for key, val in level_map.items()}
        levels = [level_map[line.level] for line in self.lines]
        if levels:
            max_level = max(levels)
        else:
            max_level = 10
        status = level_map_reverse[max_level]
        return status


@dataclass
class Report:
    logfiles: list[LogFile]

    @property
    def tool_count(self) -> int:
        return len(self.logfiles)

    @property
    def statuses(self) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for logfile in self.logfiles:
            counts[logfile.status] += 1
        # touch the following (set to zero)
        counts['OK']
        counts['WARNING']
        counts['ERROR']
        counts['CRITICAL']
        return counts
    
    @property
    def messages(self) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for logfile in self.logfiles:
            for msg in logfile.unique_messages:
                counts[msg] += 1
        return counts
    
    def get_tools_with_level(self, level: str) -> list[str]:
        out: set[str] = set()
        for logfile in self.logfiles:
            for logline in logfile.lines:
                if logline.level == level:
                    out.add(logfile.path.rstrip('.log'))
        return list(out)

    def get_tools_with_msg(self, message: str) -> list[str]:
        out: set[str] = set()
        for logfile in self.logfiles:
            for logline in logfile.lines:
                if logline.message == message:
                    out.add(logfile.path.rstrip('.log'))
        return list(out)



class Reporter:
    def __init__(self, directory: str):
        self.directory = directory

    def report(self) -> None:
        report = self.load_report()
        self.print_report(report)

    def load_report(self) -> Report:
        log_paths = self.get_logfile_paths()
        log_files = [self.load_log(path) for path in log_paths]
        return Report(log_files)

    def get_logfile_paths(self) -> list[str]:
        out: list[str] = []
        for log_dir in self.get_logfile_directories():
            files = os.listdir(log_dir)
            log_files = [f for f in files if f.endswith('.log')]
            out += [f'{log_dir}/{f}' for f in log_files]
        return out

    def get_logfile_directories(self) -> list[str]:
        return [self.directory]

    def load_log(self, path: str) -> LogFile:
        log_lines: list[LogLine] = []
        with open(path, 'r') as fp:
            line = fp.readline().strip('\n').split(' ', 2) # how to delim each LogLine
            while line[0] != '':
                level = line[0].strip('][')
                logger = line[1].strip('][')
                message = line[2]
                log_lines.append(LogLine(level, logger, message))
                line = fp.readline().strip('\n').split(' ', 2)
        return LogFile(path, log_lines)
    
    def print_report(self, report: Report) -> None:
        print(f'\nTOOLS PARSED: {report.tool_count}')
        
        print('\nSTATUSES:')
        statuses = list(report.statuses.items())
        statuses.sort(key=lambda x: x[1], reverse=True)
        print(f"{'status':<10}{'tool count':>13}{'percent':>10}")
        for status, count in statuses:
            percent = count / report.tool_count * 100
            print(f'{status:<10}{count:>13}{percent:>10.1f}')

        print('\nMESSAGES:')
        messages = list(report.messages.items())
        messages.sort(key=lambda x: x[1], reverse=True)
        print(f"{'message':<30}{'tool count':>13}{'percent':>10}")
        for message, count in messages:
            percent = count / report.tool_count * 100
            print(f'{message:<30}{count:>13}{percent:>10.1f}')

        print('\nERROR TOOLS:')
        for tool in report.get_tools_with_level('ERROR'):
            print(tool)
        
        print('\nCRITICAL TOOLS:')
        for tool in report.get_tools_with_msg('exception'):
            print(tool)


def main(argv: list[str]):
    parsed_folder = argv[0]
    reporter = Reporter(parsed_folder)
    reporter.report()


if __name__ == '__main__':
    main(sys.argv[1:])





    # def report(self) -> None:
    #     for parsed_dir in self.directories:
    #         files = os.listdir(f'{self.workdir}/{parsed_dir}')
    #         logfiles = [f for f in files if f.endswith('.log')]
            
    #         for logfile in logfiles:
    #             pyfile = logfile.rsplit('.')[0] + '.py'
    #             if os.path.exists(f'{self.workdir}/{parsed_dir}/{pyfile}'):
    #                 self.tool_count += 1
    #                 self.update_errors_from_logfile(parsed_dir, logfile)
    #                 self.update_errors_from_filepair(parsed_dir, logfile, pyfile)
        
    #     self.print_report()

        
    # def update_errors_from_logfile(self, parsed_dir: str, logfile: str) -> None:
    #     filepath = f'{self.workdir}/{parsed_dir}/{logfile}'
    #     with open(filepath, 'r', encoding="utf-8") as fp:
    #         log_lines = fp.readlines()
    #         log_lines = [ln.rstrip('\n') for ln in log_lines]
            
    #     self.handle_levels(log_lines, logfile)
    #     self.handle_messages(log_lines)
            

    # def handle_levels(self, log_lines: list[str], logfile: str) -> None:
    #     level_state_map = {
    #         'INFO': 0,
    #         'WARN': 1,
    #         'ERROR': 2
    #     }

    #     if len(log_lines) == 0:
    #         self.tool_statuses[logfile.rsplit('.')[0]] = 'PASS'
    #         return

    #     max_level = 0

    #     for line in log_lines:
    #         state, message = line.split(',')
    #         level = level_state_map[state]
    #         if level > max_level:
    #             max_level = level
        
    #     if max_level == 0:
    #         self.tool_statuses[logfile.rsplit('.')[0]] = 'PASS'
    #     elif max_level == 1:
    #         self.tool_statuses[logfile.rsplit('.')[0]] = 'WARN'
    #     elif max_level == 2:
    #         self.tool_statuses[logfile.rsplit('.')[0]] = 'ERROR'

                  
    # def handle_messages(self, log_lines: list[str]) -> None:
    #     for line in log_lines:
    #         status, message = line.split(',')

    #         if 'tool contains configfiles' in message:
    #             self.error_counter['configfiles_ERROR'] += 1

    #         elif 'missing datatype for' in message:
    #             self.error_counter['missing_datatype_WARN'] += 1

    #         elif 'could not find tool version in api request' in message or 'no container found' in message:
    #             self.error_counter['container_not_found_ERROR'] += 1
            
    #         elif 'chosen base command is set_environment' in message:
    #             self.error_counter['set_environment_ERROR'] += 1
            
    #         elif 'pipe encountered as end of 1st command' in message:
    #             self.error_counter['pipe_command_ERROR'] += 1
            
    #         elif 'multiple commands encountered' in message:
    #             self.error_counter['multiple_commands_WARN'] += 1
            
    #         elif 'for loop encountered' in message or 'while loop' in message:
    #             self.error_counter['for_loop_WARN'] += 1
    

    # def update_errors_from_filepair(self, parsed_dir: str, logfile: str, pyfile: str) -> None:
    #     logfile_path = f'{self.workdir}/{parsed_dir}/{logfile}'
    #     pyfile_path = f'{self.workdir}/{parsed_dir}/{pyfile}'

    #     with open(logfile_path, 'r', encoding="utf-8") as fp:
    #         logfile_contents = fp.read()
    #     with open(pyfile_path, 'r', encoding="utf-8") as fp:
    #         pyfile_contents = fp.read()

    #     if logfile_contents == '' and pyfile_contents == '':
    #         self.error_counter['uncaught_error'] += 1
    #         self.tool_statuses[logfile.rsplit('.')[0]] = 'ERROR'



