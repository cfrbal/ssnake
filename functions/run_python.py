from .file_handler import *
import subprocess

def run_python_file(working_directory, file_path):
    workspace_path = os.path.abspath(working_directory)
    final_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not is_in_scope(workspace_path, final_file_path):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(final_file_path):
        return f'Error: File "{file_path}" not found.'
    if not final_file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    

    try:
        otp = subprocess.run(['python', final_file_path], timeout=30, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workspace_path)
        # print(otp)
        if otp == None:
            output = 'No output produced'
        else:
            output=f"STDOUT: {otp.stdout} | STDERR | {otp.stderr}"

        if otp.returncode != 0:
            output+= f" | Process exited with code {otp.returncode}"
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
    return output