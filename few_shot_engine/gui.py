import subprocess

class Gui:
    def __init__(self):
        self.processes = []

    def kill_old_processes(self):
        for process in self.processes:
            process.terminate()
        self.processes.clear()

    def display_fewshot(self, metadata_dir, input_dir, output_dir):
        # Kill old processes
        self.kill_old_processes()
        
        # Open files in Notepad and save process handles
        self.processes.append(subprocess.Popen(f"notepad {metadata_dir}", shell=True))
        self.processes.append(subprocess.Popen(f"notepad {input_dir}", shell=True))
        self.processes.append(subprocess.Popen(f"notepad {output_dir}", shell=True))
