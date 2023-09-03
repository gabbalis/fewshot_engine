import subprocess
from few_shot_engine.context_managers.PythonPathHas import PythonPathHas
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Command-line arguments for script.")
    parser.add_argument("--save_dir", type=str, required=True, help="""The root directory from which to build the save structure:
{root}
├─{topic}
├───{name}.json
├───{name}_dir
├─────<assorted unzipped data replicated from {name}.json>
""")
    parser.add_argument("--name", type=str, required=True, help="Name of the alchemy being performed.")
    parser.add_argument("--base_prompt", type=str, required=True, help="Base prompt for FewShotEngine.")
    parser.add_argument("--prompt_input", type=str, required=True, help="Prompt input for processing.")
    parser.add_argument("--topic", type=str, required=True, help="Topic folder to save files.")
    args = parser.parse_args()
    
    save_dir = args.save_dir
    name = args.name
    base_prompt = args.base_prompt
    prompt_input = args.prompt_input
    topic = args.topic

    with PythonPathHas('.'):
        from context_managers.OpenWithHandling import OpenWithHandling as open
        from few_shot_engine.few_shot_engine import FewShotEngine

        command = f"python zip_utils.py --unzipped_dir {save_dir}\\{topic}\\{name}_dir\\ --zipped_file {save_dir}\\{topic}\\{name}.json --zip"
        subprocess.run(command, shell=True)

        f=FewShotEngine(f"{name}", os.path.abspath(f'{save_dir}\\{topic}'), save_examples=True, base_prompt=base_prompt)
        f.process(prompt_input)

        command = f"python zip_utils.py --unzipped_dir {save_dir}\\{topic}\\{name}_dir\\ --zipped_file {save_dir}\\{topic}\\{name}.json --unzip"
        subprocess.run(command, shell=True)

if __name__ == '__main__':

    main()