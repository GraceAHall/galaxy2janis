


from dataclasses import dataclass
import os
import sys
import subprocess
import threading


def get_folder_ga1s(directory: str) -> list[str]:
    files = os.listdir(directory)
    ga1s = [f for f in files if f.endswith('.ga')]
    return ga1s


@dataclass
class WorkflowJobDetails:
    workflow_dir: str
    workflow_file: str
    outdir: str


class WorkflowModeRunner:
    def __init__(self, indir: str, outdir: str):
        self.indir = indir
        self.outdir = outdir
        #self.xmldirs: list[str] = self.get_xml_directories()

    def worker(self, job: WorkflowJobDetails) -> None:
        """
        thread worker target function
        """
        print(job.workflow_file)
        command = f'python src/gxtool2janis.py workflow {job.workflow_dir}/{job.workflow_file} --dev-no-test-cmdstrs'
        subprocess.run(command, shell=True)
        #subprocess.run(command, shell=True, check=True)

    def run(self) -> None:
        wflowdirs = self.get_workflow_directories()
        details = self.get_job_details(wflowdirs)
        self.run_jobs(details=details, threads=8)
    
    def get_workflow_directories(self) -> list[str]:
        #banned_dirs = set(['mine'])
        banned_dirs = set([])
        out: list[str] = []
        for root, dirs, files in os.walk(self.indir):
            if any([f.endswith('.ga') for f in files]):
                if not root in banned_dirs:
                    out.append(root)
        return out

    def get_job_details(self, workflow_dirs: list[str]) -> list[WorkflowJobDetails]:
        """set up jobs to run"""
        details: list[WorkflowJobDetails] = []
        for workflow_dir in workflow_dirs:
            workflow_files = get_folder_ga1s(workflow_dir)
            for workflow_file in workflow_files:
                wflow_basename = workflow_file.lower().replace('-', '_').rsplit('.', 1)[0]
                outdir = f'{self.outdir}/{wflow_basename}' # unnecessary
                details.append(WorkflowJobDetails(workflow_dir, workflow_file, outdir))
        return details

    def run_jobs(self, details: list[WorkflowJobDetails], threads: int) -> None:
        # execute jobs using threads
        for i in range(0, len(details), threads):
            pool: list[threading.Thread] = []
            for j in range(threads):
                if i + j < len(details):
                    job = details[i + j]
                    t = threading.Thread(target=self.worker, args=(job,))
                    t.daemon = True
                    pool.append(t)
            for j in range(len(pool)):
                pool[j].start()
            for j in range(len(pool)):
                pool[j].join()
                

def main(argv: list[str]):
    workflows_folder = argv[0]
    out_dir = argv[1]
    runner = WorkflowModeRunner(workflows_folder, out_dir)
    runner.run()



if __name__ == '__main__':
    main(sys.argv[1:])