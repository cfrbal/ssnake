import os

def is_in_scope(workspace_path, final_directory_path=None):
    return final_directory_path.startswith(workspace_path)

def is_directory(path):
    return os.path.isdir(path)

def is_file(path):
    return os.path.isfile(path)

def get_files_info(working_directory, directory="."):
    workspace_path = os.path.abspath(working_directory)
    final_directory_path = os.path.abspath(os.path.join(working_directory, directory))
    if not is_in_scope(workspace_path, final_directory_path):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not is_directory(final_directory_path):
        return f'Error: "{directory}" is not a directory'
    dir_contents = os.listdir(os.path.join(working_directory, directory))
    output = ''
    for dir in dir_contents:
        file_with_path = os.path.join(final_directory_path, dir)
        print(file_with_path)
        output += f'- {dir}: file_size={os.path.getsize(file_with_path)}, is_dir={os.path.isdir(file_with_path)}\n'
    return output

def get_file_content(working_directory, file_path):
    workspace_path = os.path.abspath(working_directory)
    final_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not is_in_scope(workspace_path, final_file_path):
        return f'Error: Cannot read "{final_file_path}" as it is outside the permitted working directory'
    if not is_file(final_file_path):
        return f'Error: File not found or is not a regular file: "{final_file_path}"'
    MAX_CHARS = 10000

    try:
        with open(final_file_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)
    except Exception as e:
        return f"Error: {e}"
    return file_content_string

def write_file(working_directory, file_path, content):
    workspace_path = os.path.abspath(working_directory)
    final_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not is_in_scope(workspace_path, final_file_path):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(os.path.dirname(final_file_path)):
        try:
            os.makedirs(os.path.dirname(final_file_path))
        except Exception as e:
            return f'Error: File not found and cannot be created: "{e}"'
    try:
        with open(final_file_path, "w") as f:
            file_content_string = f.write(content)
    except Exception as e:
        return f"Error: {e}"
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
