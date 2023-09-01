# a Strategy helper function that dynamically creates and uses memoized few shot templates 
import textwrap
from few_shot_engine.context_managers.OpenWithHandling import OpenWithHandling as open
import os
import json

class EngineFactory(object):
    def __init__(self, few_shot_root, args):
        self.example_dir = os.path.join(few_shot_root, 'examples')
        self.save_directory = os.path.join(few_shot_root, 'factory')
        self.memo_file = os.path.join(self.save_directory, 'memo.json')
        # self.rebuild = rebuild
        try:
            with open(self.memo_file, 'r') as file:
                self.memo = json.load(file)
        except Exception:
            self.memo = {}

        self.engine = self.load_engine(args)
        if not self.engine: #or self.rebuild:
            self.check_fields(*args)
            self.engine = self.make_engine(args)

    def run(self, context):
        return self.engine(context)


    def check_fields(self, field=None, name=None, provided=[], final=[], notes=[], template = ""):
        if not field or not name:
            raise ValueError("field, name. and example_dir are all required.")

    def save_engine(self, args, code):
        name = args['name']
        new_entry = {'args': args, 'version': 1}
        
        if name in self.memo:
            for existing_entry in self.memo[name]:
                if existing_entry['args'] == args:
                        raise ValueError("Unreachable code error? save_engine called for existing version.")
            new_entry['version'] = len(self.memo[name]) + 1
            self.memo[name].append(new_entry)
        else:
            self.memo[name] = [new_entry]

        with open(self.memo_file, 'w') as file:
            json.dump(self.memo, file)

        file_path = os.path.join(self.save_directory, f"{name}_{new_entry['version']}.py")
        with open(file_path, 'w') as file:
            file.write(code)

    def load_engine(self, args):
        name = args['name']
        if name not in self.memo:
            return None

        for existing_entry in self.memo[name]:
            if existing_entry['args'] == args:
                file_path = os.path.join(self.save_directory, f"{name}_{existing_entry['version']}.py")
                with open(file_path, 'r') as file:
                    code = file.read()

                exec_globals = {}
                exec(code, exec_globals)
                generated_function = exec_globals[f"{name}_fn"]

                return lambda arg: generated_function(arg)
        return None

    def make_engine(self, args):
        # need this later
        def get_do(tabs=0):
            # add args to the code that may be needed. Note that the resolver can use Context, or field[0], field[1], or previous provideds here.
            # name_value = "f"{name}""
            LB = "{"
            RB = "}"
            r = f"""
    {"    "*(tabs)}{ (NL+"    "*(tabs+1)).join([f"{name} = {resolver}" for name, resolver in args['provided'].items()])}
    {"    "*(tabs)}{args['name']} = {args['name']}_engine.process(f\"\"\"
{ NL.join([f"Here's the {name}:{NL}{LB}{name}{RB}" for name in args['provided'].keys() ])}

Here is a template of exactly what you should return:
{args['template']}
\"\"\")
    {"    "*(tabs)}return_val += {args['name']}
    {"    "*(tabs)}{ ("{NL}"+"    "*(tabs+1)).join([f"{fin}" for fin in args['final']])}
"""
            return r

        code = f"from few_shot_engine.few_shot_engine import FewShotEngine\nNL = \"\\n\"\n"
        NL = "\n"
        # First we add the base prompt and FewShotEngine code.
        code += f"""
def {args['name']}_fn(context):
    return_val = ''
    base_prompt=\"\"\"
Your output should look excactly like the template, including whitespace, except with additional input at '''ADD HERE'''
Dont return any comments or additional explaination. Just the requested code.

{ NL.join([f"{name} will be provided." for name in args['provided'].keys()])}

{ NL.join([f"{note}" for note in args['notes']])}
\"\"\"
    {args['name']}_engine = FewShotEngine("{args['name']}", r"{self.example_dir}", save_examples=True, base_prompt = base_prompt)
"""
        # Now we add different things depending on whether this completion is being looped.
        fields = args['field'].split(':')
        if len(fields)==1:
            code += f"""
    {fields[0]} = context.get('{fields[0]}')
{get_do()}
    return return_val
"""
        elif len(fields)==2:
            code += f"""
    {fields[1].split('.')[0]} = context.get('{fields[1]}')
    for {fields[0]} in {fields[1].split('.')[0]}:
{get_do(tabs=1)}
    return return_val
"""
        else:
            raise ValueError("fields should be for format 'name' or 'name:names' to represent a for loop.")
    

#         def get_do():
#             # add args to the code that may be needed. Note that the resolver can use Context, or field[0], field[1], or previous provideds here.
#             name_value = "{name}"
#             code += f"""
#         { NL.join([f"{name} = {resolver}" for name, resolver in args['provided'].items()])}
#         {args['name']} = {args['name']}_engine.process(f\"\"\"
#     { NL.join([f"Here's the {name}:{NL}{name_value}" for name in args['provided'].keys() ])}

# Here is a template of exactly what you should return:
# {args['template']}
# \"\"\")
# """
        self.save_engine(args, code)
        return self.load_engine(args)