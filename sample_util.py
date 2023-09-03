from few_shot_engine.gui import Gui
from few_shot_engine.few_shot_engine import FewShotEngine

gui = Gui()

def utility_function(name, input_string, save_directory='.', num_examples=3, save_examples=True, base_prompt=""):
    # Step 1: Create a new FewShotEngine
    engine = FewShotEngine(name, save_directory, num_examples, save_examples, base_prompt)

    # Step 2: Zip the files
    engine.zip()

    # Step 3: Process
    output = engine.process(input_string)  # Passing the input_string here

    # Step 4: Unzip
    engine.unzip()

    # Step 5: Get last generated directories
    dirs = engine.get_last_gen_dirs()
    if dirs:
        metadata_dir, input_dir, output_dir = dirs  # Adjust depending on your actual structure

        # Step 6: Send to GUI
        gui.display_fewshot(metadata_dir, input_dir, output_dir)

    return output