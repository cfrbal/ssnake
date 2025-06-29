from google.genai import types
from functions.file_handler import *
from functions.run_python import *
from functions.agent_communication import task_complete

function_map = {
    "write_file": write_file,
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "task_complete": task_complete
}


