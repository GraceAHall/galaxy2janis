

from collections import defaultdict
from dataclasses import dataclass
import os
import sys
from typing import Optional

import subprocess

# LOGS
@dataclass
class LogLine:
    """
    represents a single log line within a .log file
    structure = '[%(levelname)s] [%(name)s] %(message)s'
    """
    level: str
    logger: str
    message: str


@dataclass
class LogFile:
    """represents a single .log file"""
    path: str
    lines: list[LogLine]

    @property
    def messages(self) -> list[str]:
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

    def has_message(self, message: str) -> bool:
        for line in self.lines:
            if line.message == message:
                return True
        return False
    
    def has_level(self, level: str) -> bool:
        for line in self.lines:
            if line.level == level:
                return True
        return False


# SINGLE TOOL
class ToolReport:
    """represents result of a single parsed tool"""
    def __init__(self, toolname: str, toolpath: Optional[str], logpath: str):
        self.toolname = toolname
        self.toolpath = toolpath  # path to .py file
        self.logfile: LogFile = load_log(logpath)  # loaded logfile

    @property
    def translatable(self) -> bool:
        # does janis translate cwl work?
        if not self.toolpath:
            return False
        try:
            command = f'python {self.toolpath}'
            subprocess.run(command, stdout=open(os.devnull, 'wb'), shell=True, check=True)
            return True
        except:
            return False

    @property
    def status(self) -> str:
        if not self.toolpath:  # no .py file generated, early exit
            return 'CRITICAL'
        return self.logfile.status
    

# MULTIPLE TOOLS
@dataclass
class ToolParsingReport:
    """represents result of a group of parsed tools"""
    reports: list[ToolReport]

    @property
    def tool_count(self) -> int:
        return len(self.reports)

    @property
    def statuses(self) -> dict[str, int]:
        counts: dict[str, int] = {
            'OK': 0,
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0,
        }
        for report in self.reports:
            counts[report.status] += 1
        return counts
    
    @property
    def message_counts(self) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for report in self.reports:
            for msg in report.logfile.messages:
                counts[msg] += 1
        return counts
    
    def get_tools_with_level(self, level: str) -> list[str]:
        return [report.toolname for report in self.reports if report.logfile.has_level(level)]

    def get_tools_with_msg(self, message: str) -> list[str]:
        return [report.toolname for report in self.reports if report.logfile.has_message(message)]


class WorkflowReport:
    """represents result of a single parsed workflow"""
    def __init__(self, name: str, logpath: str, toolspath: str, workflow_path: Optional[str]):
        self.name = name
        self.logfile: LogFile = load_log(logpath)
        self.tool_parsing_report: ToolParsingReport = create_tool_parsing_report(toolspath)
        self.workflow_path = workflow_path

    # TODO make actual messages go to logfile. 
    # TODO read info from the logfile. 

    @property
    def translatable(self) -> bool:
        # does janis translate cwl work?
        if not self.workflow_path:
            return False
        try:
            command = f'janis translate {self.workflow_path} cwl -o temp'
            subprocess.run(command, stdout=open(os.devnull, 'wb'), shell=True, check=True)
            return True
        except:
            return False

    @property
    def tool_failure(self) -> bool:
        # did one of the tool translations fail?
        if self.tool_parsing_report.statuses['CRITICAL'] > 0:
            return True
        return False
    
    @property
    def workflow_failure(self) -> bool:
        # did something else about the workflow translation cause failure?
        if self.logfile.status == 'CRITICAL':
            return True
        # no tool failure, but didnt produce workflow
        elif not self.tool_failure and not self.workflow_path:
            return True
        # no tool failure, but workflow is empty
        elif not self.tool_failure and self.workflow_empty:
            return True
        return False
    
    @property
    def workflow_empty(self) -> bool:
        if self.workflow_path:
            with open(self.workflow_path, 'r') as fp:
                contents = fp.read()
                if contents == '':
                    return True
        return False



@dataclass
class WorkflowParsingReport:
    """represents result of a group of parsed workflows"""
    reports: list[WorkflowReport]

    @property
    def workflow_count(self) -> int:
        return len(self.reports)

    @property
    def statuses(self) -> dict[str, int]:
        counts: dict[str, int] = {
            'TOOL_EXCEPTION': 0,
            'WORKFLOW_EXCEPTION': 0,
            'PARSED': 0,
            'TRANSLATABLE': 0
        }
        for report in self.reports:
            # these are abusing the fact that T/F bool == 1/0
            counts['TOOL_EXCEPTION'] += report.tool_failure
            counts['WORKFLOW_EXCEPTION'] += report.workflow_failure
            counts['TRANSLATABLE'] += report.translatable
            if not report.tool_failure and not report.workflow_failure:
                if report.workflow_path:
                    counts['PARSED'] += 1
        return counts
    
    @property
    def message_counts(self) -> dict[str, int]:
        raise NotImplementedError()
    
    


def main(argv: list[str]):
    mode = argv[0]
    parsed_folder = argv[1]
    if mode == 'tool':
        tool_mode(parsed_folder)
    elif mode == 'workflow':
        workflow_mode(parsed_folder)
    else:
        raise RuntimeError()


# MAIN EXECUTION LOGIC
def tool_mode(parsed_folder: str) -> None:
    report = create_tool_parsing_report(parsed_folder)
    print_tool_parsing_report(report)

def workflow_mode(parsed_folder: str) -> None:
    report = create_workflow_parsing_report(parsed_folder)
    print_workflow_parsing_report(report)

def create_tool_parsing_report(parsed_tools_folder: str) -> ToolParsingReport:
    folders = get_subfolders(parsed_tools_folder)
    reports = [make_tool_report(f) for f in folders]
    return ToolParsingReport(reports)

def make_tool_report(folder: str) -> ToolReport:
    logfiles = [x for x in os.listdir(folder) if x.endswith('.log')]
    pyfiles = [x for x in os.listdir(folder) if x.endswith('.py')]
    return ToolReport(
        toolname=folder.rsplit('/', 1)[-1],
        toolpath=f'{folder}/{pyfiles[0]}' if pyfiles else None,
        logpath=f'{folder}/{logfiles[0]}'
    )

def create_workflow_parsing_report(parsed_workflows_folder: str) -> WorkflowParsingReport:
    workflow_dirs = get_workflow_directories(parsed_workflows_folder)
    workflow_reports = [make_workflow_report(directory) for directory in workflow_dirs]
    return WorkflowParsingReport(workflow_reports)

def make_workflow_report(folder: str) -> WorkflowReport:
    return WorkflowReport(
        name=folder.rsplit('/', 1)[-1], 
        logpath=f'{folder}/workflow.log', 
        toolspath=f'{folder}/tools', 
        workflow_path=get_workflow_path(folder)
    )

# DIRECTORY METHODS
def get_subfolders(folder: str) -> list[str]:
    out: list[str] = []
    for entity in os.listdir(folder):
        path = f'{folder}/{entity}'
        if os.path.isdir(path):
            out.append(path)
    return out

def get_logfile_paths(folder: str) -> list[str]:
    out: list[str] = []
    for root, dirs, files in os.walk(folder):
        out += [f'{root}/{f}' for f in files if f != 'workflow.log' and f.endswith('.log')]
    return out

def get_workflow_directories(folder: str) -> list[str]:
    files = os.listdir(folder)
    paths = [f'{folder}/{f}' for f in files]
    return [p for p in paths if os.path.isdir(p)]

def get_workflow_path(folder: str) -> Optional[str]:
    if os.path.exists(f'{folder}/workflow.py'):
        return f'{folder}/workflow.py'
    return None


# FILE LOADING METHODS
def load_log(path: str) -> LogFile:
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
    

# TOOLS PRINTING
def print_tool_parsing_report(report: ToolParsingReport) -> None:
    print_tool_count(report)
    print_tool_statuses(report)
    print_tool_messages(report)
    print_critical_tools(report)

def print_tool_count(report: ToolParsingReport) -> None:
    print(f'\nTOOLS PARSED: {report.tool_count}')
    
def print_tool_statuses(report: ToolParsingReport) -> None:
    print('\nSTATUSES:')
    statuses = list(report.statuses.items())
    statuses.sort(key=lambda x: x[1], reverse=True)
    print(f"{'status':<10}{'tool count':>13}{'percent':>10}")
    for status, count in statuses:
        percent = count / report.tool_count * 100
        print(f'{status:<10}{count:>13}{percent:>10.1f}')

def print_tool_messages(report: ToolParsingReport) -> None:
    print('\nMESSAGES:')
    messages = list(report.message_counts.items())
    messages.sort(key=lambda x: x[1], reverse=True)
    print(f"{'message':<30}{'tool count':>13}{'percent':>10}")
    for message, count in messages:
        percent = count / report.tool_count * 100
        print(f'{message:<30}{count:>13}{percent:>10.1f}')

def print_critical_tools(report: ToolParsingReport) -> None:
    print('\nCRITICAL TOOLS:')
    for tool in report.get_tools_with_msg('exception'):
        print(tool)


# WORKFLOWS PRINTING
def print_workflow_parsing_report(report: WorkflowParsingReport) -> None:
    out_str: str = ''
    out_str += str_workflow_count(report)
    out_str += str_workflow_statuses(report)
    print(out_str)

def str_workflow_count(report: WorkflowParsingReport) -> str:
    return f'\n\nWORKFLOWS PARSED: {report.workflow_count}'
    
def str_workflow_statuses(report: WorkflowParsingReport) -> str:
    out: str = '\n\nSTATUSES:\n'
    statuses = list(report.statuses.items())
    statuses.sort(key=lambda x: x[1], reverse=True)
    out += f"{'status':<20}{'count':>13}{'percent':>10}\n"
    for status, count in statuses:
        percent = count / report.workflow_count * 100
        out += f'{status:<20}{count:>13}{percent:>10.1f}\n'
    return out

if __name__ == '__main__':
    main(sys.argv[1:])


