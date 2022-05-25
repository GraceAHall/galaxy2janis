

from collections import defaultdict
from dataclasses import dataclass
import os
import sys
from typing import Optional



@dataclass
class LogLine:
    """structure = '[%(levelname)s] [%(name)s] %(message)s'"""
    level: str
    logger: str
    message: str


@dataclass
class LogFile:
    type: str  # either 'tool' or 'workflow'
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
class ToolParsingReport:
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



@dataclass
class WorkflowReport:
    name: str
    tools_report: ToolParsingReport
    logfile: LogFile
    workflow_path: Optional[str]

    # TODO make actual messages go to logfile. 
    # TODO read info from the logfile. 

    @property
    def tool_failure(self) -> bool:
        # did one of the tool translations fail?
        raise NotImplementedError()
    
    @property
    def workflow_failure(self) -> bool:
        # did something else about the workflow translation cause failure?
        raise NotImplementedError()
    
    @property
    def translatable(self) -> bool:
        # does janis translate cwl work?
        raise NotImplementedError()



@dataclass
class WorkflowParsingReport:
    reports: list[WorkflowReport]

    def hello(self) -> None:
        print()
    

def main(argv: list[str]):
    mode = argv[0]
    parsed_folder = argv[1]
    if mode == 'tool':
        tool_mode(parsed_folder)
    elif mode == 'workflow':
        workflow_mode(parsed_folder)
    else:
        raise RuntimeError()


def tool_mode(parsed_folder: str) -> None:
    report = create_tool_parsing_report(parsed_folder)
    print_tool_parsing_report(report)

def workflow_mode(parsed_folder: str) -> None:
    report = create_workflow_parsing_report(parsed_folder)
    print_workflow_parsing_report(report)

def create_tool_parsing_report(parsed_tools_folder: str) -> ToolParsingReport:
    log_paths = get_tool_logfile_paths(parsed_tools_folder)
    log_files = [load_log(path, logtype='tool') for path in log_paths]
    return ToolParsingReport(log_files)

def create_workflow_parsing_report(parsed_workflows_folder: str) -> WorkflowParsingReport:
    reports: list[WorkflowReport] = []
    workflow_dirs = get_workflow_directories(parsed_workflows_folder)
    for directory in workflow_dirs:
        folder = f'{parsed_workflows_folder}/{directory}'
        reports.append(WorkflowReport(
            name=directory, 
            tools_report=load_workflow_tools_report(folder), 
            logfile=load_workflow_logfile(folder), 
            workflow_path=load_workflow_path(folder))
        )
    return WorkflowParsingReport(reports)

def get_workflow_directories(folder: str) -> list[str]:
    files = os.listdir(folder)
    return [f for f in files if os.path.isdir(f'{folder}/{f}')]

def load_workflow_tools_report(folder: str) -> ToolParsingReport:
    tools_dir = f'{folder}/tools'
    return create_tool_parsing_report(tools_dir)

def load_workflow_logfile(folder: str) -> LogFile:
    logfile_path = f'{folder}/workflow.log'
    return load_log(logfile_path)

def load_workflow_path(folder: str) -> Optional[str]:
    if os.path.exists(f'{folder}/workflow.py'):
        return f'{folder}/workflow.py'
    return None


# helper methods
def get_tool_logfile_paths(folder: str) -> list[str]:
    out: list[str] = []
    for root, dirs, files in os.walk(folder):
        out += [f'{root}/{f}' for f in files if f != 'workflow.log' and f.endswith('.log')]
    return out

def load_log(path: str, logtype: str='tool') -> LogFile:
    log_lines: list[LogLine] = []
    with open(path, 'r') as fp:
        line = fp.readline().strip('\n').split(' ', 2) # how to delim each LogLine
        while line[0] != '':
            level = line[0].strip('][')
            logger = line[1].strip('][')
            message = line[2]
            log_lines.append(LogLine(level, logger, message))
            line = fp.readline().strip('\n').split(' ', 2)
    return LogFile(logtype, path, log_lines)
    
def print_tool_parsing_report(report: ToolParsingReport) -> None:
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

def print_workflow_parsing_report(report: WorkflowParsingReport) -> None:
    report.hello()
    print()



if __name__ == '__main__':
    main(sys.argv[1:])


# # helper methods
# def get_logfile_paths(folder: str) -> list[str]:
#     out: list[str] = []
#     for log_dir in get_logfile_directories(folder):
#         files = os.listdir(log_dir)
#         log_files = [f for f in files if f.endswith('.log')]
#         out += [f'{log_dir}/{f}' for f in log_files]
#     return out



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



