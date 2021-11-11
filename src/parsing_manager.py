


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
        TH_COUNT = 10
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
        self.missed_datatypes = set()
        self.tool_count = 0
        self.error_counter = defaultdict(int)
        self.tool_statuses = defaultdict(int)
         

    def report(self) -> None:
        for parsed_dir in self.directories:
            files = os.listdir(f'{self.workdir}/{parsed_dir}')
            logfiles = [f for f in files if f.endswith('.log')]

            for logfile in logfiles:
                print(logfile)
                self.tool_count += 1
                filepath = f'{self.workdir}/{parsed_dir}/{logfile}'
                self.update_errors(filepath)

        self.print_report()


    def update_errors(self, filepath: str) -> None:
        with open(filepath, 'r') as fp:
            log_lines = fp.readlines()
            log_lines = [ln.rstrip('\n') for ln in log_lines]
            
        self.handle_levels(log_lines)
        self.handle_messages(log_lines)
            

    def handle_levels(self, log_lines: list[str]) -> None:
        level_state_map = {
            'INFO': 0,
            'WARN': 1,
            'ERROR': 2
        }

        if len(log_lines) == 0:
            self.tool_statuses['PASS'] += 1
            return

        max_level = 0

        for line in log_lines:
            state, message = line.split(',')
            level = level_state_map[state]
            if level > max_level:
                max_level = level
        
        if max_level == 0:
            self.tool_statuses['PASS'] += 1
        elif max_level == 1:
            self.tool_statuses['WARN'] += 1
        elif max_level == 2:
            self.tool_statuses['ERROR'] += 1

                  
    def handle_messages(self, log_lines: list[str]) -> None:
        for line in log_lines:
            status, message = line.split(',')

            if 'tool contains configfiles' in message:
                self.error_counter['configfiles'] += 1

            elif 'variable not found in command string' in message:
                self.error_counter['var_not_found'] += 1

            elif 'user input required' in message:
                self.error_counter['user_input'] += 1

            elif 'datatype conversion failed' in message:
                self.error_counter['datatype_conversion'] += 1
                datatype = message.rsplit(' ', 1)[-1]
                if datatype != '':
                    self.missed_datatypes.add(datatype)

            elif 'container requirement encountered' in message:
                self.error_counter['contatiner'] += 1
            
            elif 'chosen base command is set_environment' in message:
                self.error_counter['set_environment'] += 1
            
            elif 'complex regex' in message:
                self.error_counter['complex_regex'] += 1
            
            elif 'unsupported param type' in message:
                self.error_counter['unsupported_param'] += 1
            
            elif 'container could not be resolved' in message:
                self.error_counter['unresolved_container'] += 1
        

    def print_report(self) -> None:
        print()
        print(f'tools parsed: {self.tool_count}\n')
        for error_type, count in self.error_counter.items():
            print(f'{error_type}: {count}')

        mds = list(self.missed_datatypes)
        mds.sort()
        print('\n\ndatatypes missed ------------')
        for i in range(0, len(self.missed_datatypes) - 2, 4):
            print(f'{mds[i]:30s}{mds[i+1]:30s}{mds[i+2]:30s}{mds[i+3]:30s}')



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