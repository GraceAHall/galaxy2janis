


from collections import defaultdict
import os
import sys
import subprocess
import threading
from typing import Counter

class Runner:
    def __init__(self, workdir: str, directories: list[str]):
        self.workdir = workdir
        self.directories = directories


    def worker(self, job: list[str]) -> None:
        """
        thread worker target function
        """
        print(job[2])
        command = f'C:\\Users\\graci\\AppData\\Local\\Programs\\Python\\Python39\\python.exe src/gxtool2janis.py {job[2]} {job[0]}/{job[1]}'
        subprocess.run(command, shell=True)


    def run(self) -> None:
        TH_COUNT = 1
        jobs = []

        # set up all jobs to complete
        for tool_dir in self.directories:
            xmls = self.get_xmls(self.workdir, tool_dir)
            for xml in xmls:
                jobs.append([self.workdir, tool_dir, xml])

        # execute jobs using threads
        for i in range(0, len(jobs), TH_COUNT):
            threads = []

            for j in range(TH_COUNT):
                if i + j < len(jobs):
                    job = jobs[i + j]
                    t = threading.Thread(target=self.worker, args=(job,))
                    t.daemon = True
                    threads.append(t)

            for j in range(len(threads)):
                threads[j].start()

            for j in range(len(threads)):
                threads[j].join()
                


    def get_xmls(self, workdir, tool_dir) -> list[str]:
        files = os.listdir(f'{workdir}/{tool_dir}')
        xmls = [f for f in files if f.endswith('xml')]
        xmls = [x for x in xmls if 'macros' not in x]
        return xmls



class Reporter:
    def __init__(self, workdir: str, directories: list[str]):
        self.workdir = workdir
        self.directories = directories
        self.tool_count = 0
        self.error_counter = defaultdict(int)
        self.tool_statuses = defaultdict(str)
         

    def report(self) -> None:
        for parsed_dir in self.directories:
            files = os.listdir(f'{self.workdir}/{parsed_dir}')
            logfiles = [f for f in files if f.endswith('.log')]
            
            for logfile in logfiles:
                pyfile = logfile.rsplit('.')[0] + '.py'
                if os.path.exists(f'{self.workdir}/{parsed_dir}/{pyfile}'):
                    self.tool_count += 1
                    self.update_errors_from_logfile(parsed_dir, logfile)
                    self.update_errors_from_filepair(parsed_dir, logfile, pyfile)
        
        self.print_report()

        
    def update_errors_from_logfile(self, parsed_dir: str, logfile: str) -> None:
        filepath = f'{self.workdir}/{parsed_dir}/{logfile}'
        with open(filepath, 'r') as fp:
            log_lines = fp.readlines()
            log_lines = [ln.rstrip('\n') for ln in log_lines]
            
        self.handle_levels(log_lines, logfile)
        self.handle_messages(log_lines)
            

    def handle_levels(self, log_lines: list[str], logfile: str) -> None:
        level_state_map = {
            'INFO': 0,
            'WARN': 1,
            'ERROR': 2
        }

        if len(log_lines) == 0:
            self.tool_statuses[logfile.rsplit('.')[0]] = 'PASS'
            return

        max_level = 0

        for line in log_lines:
            state, message = line.split(',')
            level = level_state_map[state]
            if level > max_level:
                max_level = level
        
        if max_level == 0:
            self.tool_statuses[logfile.rsplit('.')[0]] = 'PASS'
        elif max_level == 1:
            self.tool_statuses[logfile.rsplit('.')[0]] = 'WARN'
        elif max_level == 2:
            self.tool_statuses[logfile.rsplit('.')[0]] = 'ERROR'

                  
    def handle_messages(self, log_lines: list[str]) -> None:
        for line in log_lines:
            status, message = line.split(',')

            if 'tool contains configfiles' in message:
                self.error_counter['configfiles'] += 1

            elif 'missing datatype for' in message:
                self.error_counter['missing_datatype'] += 1

            elif 'could not find tool version in api request' or 'no container found' in message:
                self.error_counter['container_not_found'] += 1
            
            elif 'chosen base command is set_environment' in message:
                self.error_counter['set_environment'] += 1
            
            elif 'pipe encountered as end of 1st command' in message:
                self.error_counter['pipe_command'] += 1
            
            elif 'multiple commands encountered' in message:
                self.error_counter['multiple_commands_INFO'] += 1
            
            elif 'for loop encountered' or 'while loop' in message:
                self.error_counter['for_loop_INFO'] += 1
    

    def update_errors_from_filepair(self, parsed_dir: str, logfile: str, pyfile: str) -> None:
        logfile_path = f'{self.workdir}/{parsed_dir}/{logfile}'
        pyfile_path = f'{self.workdir}/{parsed_dir}/{pyfile}'

        with open(logfile_path, 'r') as fp:
            logfile_contents = fp.read()
        with open(pyfile_path, 'r') as fp:
            pyfile_contents = fp.read()

        if logfile_contents == '' and pyfile_contents == '':
            self.error_counter['uncaught_error'] += 1
            self.tool_statuses[logfile.rsplit('.')[0]] = 'ERROR'


    def print_report(self) -> None:
        print()
        print(f'TOOLS PARSED: {self.tool_count}\n')

        print('\nERRORS')
        for error_type, count in self.error_counter.items():
            print(f'{error_type}: {count}')

        print('\nSTATUSES')
        tool_statuses = list(self.tool_statuses.items())
        passes = [tool for tool, status in tool_statuses if status == 'PASS']
        warns = [tool for tool, status in tool_statuses if status == 'WARN']
        errors = [tool for tool, status in tool_statuses if status == 'ERROR']
        print(f'PASS:\t{len(passes)}')
        print(f'WARN:\t{len(warns)}')
        print(f'ERROR:\t{len(errors)}')





def main(argv):
    tools_folder = argv[0]
    parsed_folder = argv[1]
    
    tool_directories = get_directories(tools_folder)
    parsed_directories = get_directories(parsed_folder)

    runner = Runner(tools_folder, tool_directories)
    runner.run()

    reporter = Reporter(parsed_folder, parsed_directories)
    reporter.report()


def get_directories(folder_path):
    files = os.listdir(folder_path)
    directories = [f for f in files if os.path.isdir(f'{folder_path}/{f}')]
    return directories





if __name__ == '__main__':
    main(sys.argv[1:])