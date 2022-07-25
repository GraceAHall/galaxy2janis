


from dataclasses import dataclass
import os
import sys
import subprocess
import threading


def get_folder_xmls(directory: str) -> list[str]:
    # rudimentary
    files = os.listdir(directory)
    xmlfiles = [f for f in files if f.endswith('xml')]
    xmlfiles = [x for x in xmlfiles if 'macro' not in x]
    return xmlfiles


@dataclass
class ToolJobDetails:
    xmlpath: str
    outdir: str

class ToolModeRunner:
    def __init__(self, tooldir: str, outdir: str):
        self.tooldir = tooldir
        self.outdir = outdir

    def run(self, threads: int=10) -> None:
        xmldirs = self._get_xml_directories()
        details = self._get_job_details(xmldirs)
        self._run_jobs(details=details, threads=threads)
    
    def _worker(self, job: ToolJobDetails) -> None:
        """
        thread worker target function
        """
        xmlfile = job.xmlpath.rsplit('/', 1)[-1]
        print(xmlfile)
        command = f'python src/gxtool2janis.py tool --local {job.xmlpath}'
        subprocess.run(command, shell=True)
        #subprocess.run(command, shell=True, check=True)
    
    def _get_xml_directories(self):
        files = os.listdir(self.tooldir)
        directories = [f for f in files if os.path.isdir(f'{self.tooldir}/{f}')]
        directories = [f for f in files if not f.startswith('__')]
        xmldirs = [f'{self.tooldir}/{xmldir}' for xmldir in directories]
        return xmldirs

    def _get_job_details(self, xmldirs: list[str]) -> list[ToolJobDetails]:
        """set up jobs to run"""
        details: list[ToolJobDetails] = []
        for xmldir in xmldirs:
            xmlfiles = get_folder_xmls(xmldir)
            for xmlfile in xmlfiles:
                xmlpath = f'{xmldir}/{xmlfile}'
                details.append(ToolJobDetails(xmlpath, self.outdir))
        return details

    def _run_jobs(self, details: list[ToolJobDetails], threads: int) -> None:
        # execute jobs using threads
        for i in range(0, len(details), threads):
            pool: list[threading.Thread] = []
            for j in range(threads):
                if i + j < len(details):
                    job = details[i + j]
                    t = threading.Thread(target=self._worker, args=(job,))
                    t.daemon = True
                    pool.append(t)
            for j in range(len(pool)):
                pool[j].start()
            for j in range(len(pool)):
                pool[j].join()
                

def main(argv: list[str]):
    tools_folder = argv[0]
    out_dir = argv[1]
    runner = ToolModeRunner(tools_folder, out_dir)
    runner.run(threads=10)


if __name__ == '__main__':
    main(sys.argv[1:])