


from dataclasses import dataclass
import os
import sys
import subprocess
import threading


def get_folder_xmls(directory: str) -> list[str]:
    files = os.listdir(directory)
    xmlfiles = [f for f in files if f.endswith('xml')]
    xmlfiles = [x for x in xmlfiles if 'macros' not in x]
    return xmlfiles


@dataclass
class ToolJobDetails:
    xmldir: str
    xmlfile: str
    outdir: str


class ToolModeRunner:
    def __init__(self, tooldir: str, outdir: str):
        self.tooldir = tooldir
        self.outdir = outdir
        #self.xmldirs: list[str] = self.get_xml_directories()

    def worker(self, job: ToolJobDetails) -> None:
        """
        thread worker target function
        """
        print(job.xmlfile)
        command = f'python src/gxtool2janis.py tool --dir {job.xmldir} --xml {job.xmlfile} --outdir {job.outdir}'
        subprocess.run(command, shell=True)
        #subprocess.run(command, shell=True, check=True)

    def run(self) -> None:
        xmldirs = self.get_xml_directories()
        details = self.get_job_details(xmldirs)
        self.run_jobs(details=details, threads=10)
    
    def get_xml_directories(self):
        files = os.listdir(self.tooldir)
        directories = [f for f in files if os.path.isdir(f'{self.tooldir}/{f}')]
        directories = [f for f in files if not f.startswith('__')]
        xmldirs = [f'{self.tooldir}/{xmldir}' for xmldir in directories]
        return xmldirs

    def get_job_details(self, xmldirs: list[str]) -> list[ToolJobDetails]:
        """set up jobs to run"""
        details: list[ToolJobDetails] = []
        for xmldir in xmldirs:
            xmlfiles = get_folder_xmls(xmldir)
            for xmlfile in xmlfiles:
                details.append(ToolJobDetails(xmldir, xmlfile, self.outdir))
        return details

    def run_jobs(self, details: list[ToolJobDetails], threads: int) -> None:
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
    tools_folder = argv[0]
    out_dir = argv[1]
    runner = ToolModeRunner(tools_folder, out_dir)
    runner.run()



if __name__ == '__main__':
    main(sys.argv[1:])