from google.genai import types
from functions.file_handler import *
from functions.run_python import *

function_map = {
    "write_file": write_file,
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
}



def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    args = dict(function_call_part.args)
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    args["working_directory"] = workspace
    fn = function_map.get(function_call_part.name)

    if fn is None:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )
    
    result = fn(**args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": result},
            )
        ],
    )