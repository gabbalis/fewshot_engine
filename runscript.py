import subprocess
from context_managers.PythonPathHas import PythonPathHas
import os
import argparse

def main(args):
    with PythonPathHas('.'):
        from context_managers.OpenWithHandling import OpenWithHandling as open
        from src.few_shot_engine import FewShotEngine

        command = f"python .\\few_shot_engine\\src\\zip_utils.py --unzipped_dir .\\{topic}\\{name}_dir\\ --zipped_file .\\{topic}\\{name}.json --zip"
        subprocess.run(command, shell=True)

        save_dir = args.save_dir
        name = args.name
        base_prompt = args.base_prompt
        prompt_input = args.prompt_input
        topic = args.topic


        f=FewShotEngine(f"{name}", os.path.abspath('.\\{topic}'), save_examples=True, base_prompt=base_prompt)
        f.process(prompt_input)

        command = f"python .\\few_shot_engine\\src\\zip_utils.py --unzipped_dir {save_dir}\\{topic}\\{name}_dir\\ --zipped_file {save_dir}\\{topic}\\{name}.json --unzip"
        subprocess.run(command, shell=True)

if __name__ == '__main__':
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
    main(args)