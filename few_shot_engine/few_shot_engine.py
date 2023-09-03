import json
import os
from few_shot_engine.context_managers.OpenWithHandling import OpenWithHandling as open
from few_shot_engine.general_models.model_factory import ModelFactory
get_chat_completion = ModelFactory().get_chat_completion
import random
import argparse
import subprocess
import uuid

# BASE_SYSTEM_PROMPT = """
# You are a flawless completion engine.
# You output a completion to an input, in the exact format of your examples.
# """

class FewShotEngine:
    def __init__(self, name: str, save_directory, num_examples=3, save_examples=False, base_prompt=""):
        self.name = name
        self.save_directory = save_directory
        self.confirmed_examples = []
        self.unconfirmed_examples = []

        self.uuids = set([])
        self.last_gen_uuid = None
        
        self.prompt_history = []
        self.cli_inputs = []
        self.base_prompt = base_prompt if base_prompt is not None else ""
        self.prompt_history_index = -1
        self.save_examples = save_examples
        self.num_examples = num_examples
        if os.path.exists(save_directory):
            self.load_data()
        if len(self.prompt_history) == 0:
            self.prompt_history = [""]
            self.prompt_history_index = 0
        elif self.base_prompt in self.prompt_history:
            self.prompt_history_index = self.prompt_history.index(self.base_prompt)
        else:
            self.prompt_history.append(self.base_prompt)
            self.prompt_history_index = len(self.prompt_history)-1
        self.zip_script_path = os.path.join(os.path.dirname(__file__), 'zip_utils.py')

    def load_data(self):
        file_path = os.path.join(self.save_directory, f'{self.name}.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.confirmed_examples = data.get('confirmed_examples', [])
                self.unconfirmed_examples = data.get('unconfirmed_examples', [])
                self.prompt_history = data.get('prompt_history', [])
                self.cli_inputs =data.get('cli_inputs', [])

                for example_list in [self.confirmed_examples, self.unconfirmed_examples]:
                    for example in example_list:
                        if "uuid" not in example:
                            new_uuid = str(uuid.uuid4())
                            while new_uuid in self.uuids:  # Ensure uniqueness
                                new_uuid = str(uuid.uuid4())
                            example["uuid"] = str(new_uuid)
                            self.uuids.add(example["uuid"])

    def process(self, input_str, examples=None):
        if examples == None:
            examples = self.confirmed_examples

        selected_examples = random.sample(examples, min(len(examples), self.num_examples))
        examples_prompt = "\n".join([f"example{idx}:\ninput: {ex['input']}\noutput: {ex['output']}" for idx, ex in enumerate(selected_examples)])

        input = [
            {"role": "system", "content": f"{self.base_prompt}"},
            {"role": "user", "content": f"""
            Here is the list of examples:
            {examples_prompt}
            Your task is to produce output for the following input:
            {input_str}
            """}
        ]

        confirmed_index = next((index for index, e in enumerate(self.confirmed_examples) if e['input'] == input_str), -1)
        unconfirmed_index =  next((index for index, e in enumerate(self.unconfirmed_examples) if e['input'] == input_str), -1)

        if unconfirmed_index == -1 and confirmed_index == -1:
            output_str = get_chat_completion(input)
            if self.save_examples:
                self.add_unconfirmed_example(input_str, output_str)
        else:
            if confirmed_index >= 0:
                output_str =  self.confirmed_examples[confirmed_index]['output']
            else:
                output_str =  self.unconfirmed_examples[unconfirmed_index]['output']
        return output_str

    def add_unconfirmed_example(self, input_str, output_str):
        new_uuid = str(uuid.uuid4())
        while new_uuid in self.uuids:  # Ensure uniqueness
            new_uuid = str(uuid.uuid4())
        self.last_gen_uuid = new_uuid  # Set the last generated UUID

        new_example = {
            'uuid': new_uuid,
            'name': "",
            'input': input_str,
            'output': output_str,
            'prompt_history_index': self.prompt_history_index
        }
        self.unconfirmed_examples.append(new_example)
        self.uuids.add(new_uuid)

        self.save_data()


    def save_data(self):
        file_path = os.path.join(self.save_directory, f'{self.name}.json')
        data = {
            'confirmed_examples': self.confirmed_examples,
            'unconfirmed_examples': self.unconfirmed_examples,
            'prompt_history': self.prompt_history,
            'cli_inputs' : self.cli_inputs,
        }
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def zip(self):
        command = f"python {self.zip_script_path} --unzipped_dir {self.save_directory}\\{self.name}_dir\\ --zipped_file {self.save_directory}\\{self.name}.json --zip"
        subprocess.run(command, shell=True)
        self.load_data()

    def unzip(self):
        command = f"python {self.zip_script_path} --unzipped_dir {self.save_directory}\\{self.name}_dir\\ --zipped_file {self.save_directory}\\{self.name}.json --unzip"
        subprocess.run(command, shell=True)

    def get_last_gen_dirs(self):
        if self.last_gen_uuid is None:
            return None

        dirs = []

        # Flag to check if UUID is found in the directories
        uuid_found = False

        # Assuming the unzipped files are stored in folders within 'self.save_directory'
        for root, _, files in os.walk(f"{self.save_directory}\\{self.name}_dir"):
            for filename in files:
                if filename.endswith(".metadata.json"):
                    with open(os.path.join(root, filename), 'r') as f:
                        metadata = json.load(f)
                        if metadata.get("uuid") == self.last_gen_uuid:
                            uuid_found = True
                            dirs.append(os.path.abspath(os.path.join(root, filename)))  # Adding metadata.json
                            dirs.append(os.path.abspath(os.path.join(root, filename.replace(".metadata.json", ".input.txt"))))
                            dirs.append(os.path.abspath(os.path.join(root, filename.replace(".metadata.json", ".output.txt"))))

        # Raise an error if no directories are found with the given UUID
        if not uuid_found:
            raise ValueError(f"No directories found for the last generated UUID: {self.last_gen_uuid}")

        # Adding the path to the zipped directory
        zipped_dir = os.path.abspath(f"{self.save_directory}\\{self.name}.json")
        dirs.append(zipped_dir)

        return dirs



def main():
    parser = argparse.ArgumentParser(description="Run the FewShotEngine to generate code completions.")
    parser.add_argument('save_directory', type=str, help="Directory where the engine data is saved.")
    parser.add_argument('name', type=str, help="The name of the engine.")
    parser.add_argument('--num_examples', type=int, default=3, help="Number of examples to use (default is 3).")
    parser.add_argument('--save_examples', action='store_true', help="Flag to save examples (default is False).")
    parser.add_argument('--base_prompt_index', type=str, default=-1, help="Index of the Base prompt to prepend to the input (default is -1: the latest prompt).")

    
    args = parser.parse_args()

    # Load the FewShotEngine
    engine = FewShotEngine(name=args.name, save_directory=args.save_directory, num_examples=args.num_examples, save_examples=args.save_examples, base_prompt=args.base_prompt)
    # Adjust the prompt...
    engine.base_prompt_index = args.base_prompt_index
    engine.base_prompt = engine.prompt_history[args.base_prompt_index]

    for input in engine.cli_inputs:

        # Process the input and print the output
        output = engine.process(input)
        print("\n\n----------------------------------------")
        print("Input:")
        print(input)
        print("\nOutput:")
        print(output)
        print("----------------------------------------")

if __name__ == "__main__":
    main()