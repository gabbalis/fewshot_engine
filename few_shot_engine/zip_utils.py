import json
import os
import argparse
from context_managers.OpenWithHandling import OpenWithHandling as open
from collections import defaultdict
def unzip_examples(zipped_file, unzipped_dir):
    with open(zipped_file, 'r') as f:
        data = json.load(f)
    
    for i, prompt in enumerate(data.get("prompt_history", [])):
        with open(os.path.join(unzipped_dir, f"prompt_{i}.txt"), "w") as f:
            f.write(prompt.replace("\\n", "\n"))
    
    for i, example in enumerate(data.get("confirmed_examples", []) + data.get("unconfirmed_examples", [])):
        with open(os.path.join(unzipped_dir, f"{i}_example.input.txt"), "w") as f:
            f.write(example["input"].replace("\\n", "\n"))

        with open(os.path.join(unzipped_dir, f"{i}_example.output.txt"), "w") as f:
            f.write(example["output"].replace("\\n", "\n"))

        metadata = {
            "name": example.get('name', f"example_{i}"),
            "prompt_history_index": example.get("prompt_history_index", ""),
            "status": "confirmed" if example in data.get("confirmed_examples", []) else "unconfirmed"
        }

        with open(os.path.join(unzipped_dir, f"{i}_example.metadata.json"), "w") as f:
            json.dump(metadata, f, indent=4)

def zip_examples(unzipped_dir, zipped_file):
    prompts = []
    data = {"confirmed_examples": [], "unconfirmed_examples": []}
    example_map = defaultdict(lambda: {"name": None, "prompt_history_index": None, "input": None, "output": None})
    
    for i, fname in enumerate(sorted(os.listdir(unzipped_dir))):
        with open(os.path.join(unzipped_dir, fname), "r") as f:
            content = f.read()
        
            if fname.startswith("prompt_"):
                prompts.append(content.replace("\n", "\\n"))
            elif fname.endswith(".metadata.json"):
                metadata = json.loads(content)
                status = metadata["status"]
                index = int(fname.split("_")[0])
                
                example_map[index].update({
                    "name": metadata["name"],
                    "prompt_history_index": metadata["prompt_history_index"]
                })
                
                if status == "confirmed":
                    data["confirmed_examples"].append(example_map[index])
                else:
                    data["unconfirmed_examples"].append(example_map[index])
            elif fname.endswith(".input.txt") or fname.endswith(".output.txt"):
                example_key = "input" if fname.endswith(".input.txt") else "output"
                index = int(fname.split("_")[0])
                
                example_map[index][example_key] = content.replace("\n", "\\n")

    data["prompt_history"] = prompts

    with open(zipped_file, "w") as f:
        json.dump(data, f, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Zip or unzip example data.")
    parser.add_argument("--zipped_file", type=str, required=True, help="Path to the example JSON file.")
    parser.add_argument("--unzipped_dir", type=str, required=True, help="Directory for zipped/unzipped files.")
    parser.add_argument("--unzip", action="store_true", help="Unzip the example data.")
    parser.add_argument("--zip", action="store_true", help="Zip the example data.")
    args = parser.parse_args()
    
    if args.zip and args.unzip:
        parser.error("Both --zip and --unzip were provided. Please provide only one.")
    elif not args.zip and not args.unzip:
        parser.error("Neither --zip nor --unzip were provided. Please provide one.")
    elif args.zip:
        zip_examples(args.unzipped_dir, args.zipped_file)
    else:
        unzip_examples(args.zipped_file, args.unzipped_dir)

if __name__ == "__main__":
    main()
