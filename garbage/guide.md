# Repository Guide

## Files

- tasks.md: Instructions for running ssnake.
- requirements.txt: Dependencies: google-genai==1.12.1, python-dotenv==1.1.0
- schemas.py: Schemas for function calls.
- parse.py: Argument parsing.
- system_prompt.py: System prompt for the AI.
- helper.py: Function calling logic.
- main.py.old: Old version of the main script.
- ssnake: current main script.

## tasks.md content
```
# Instructions for running ssnake

1.  **Rename the script:** You have already renamed `main.py` to `ssnake.py`.

2.  **Make the script executable:** Use the following command in your terminal:

    ```bash
    chmod +x ssnake.py
    ```

3.  **(Optional) Add the script's directory to your PATH:** This allows you to run `ssnake.py` from any directory.

    *   **Find the absolute path of the directory containing `ssnake.py`.**  For example, if `ssnake.py` is in `/home/user/ssnake/`, you would use that path.

    *   **Edit your shell's configuration file (e.g., `.bashrc`, `.zshrc`)** to add the following line, replacing `/home/user/ssnake/` with the actual path:

        ```bash
        export PATH="/home/user/ssnake/:$PATH"
        ```

    *   **Reload your shell's configuration:**

        ```bash
        source ~/.bashrc  # or source ~/.zshrc, etc.
        ```

4.  **Run the script:** Now you should be able to run the script from your terminal using:

    ```bash
    ./ssnake [prompt]
    ```
    or, if you added the directory to your PATH:
    ```bash
    ssnake [prompt]
    ```

```

## requirements.txt content
```
google-genai==1.12.1
python-dotenv==1.1.0
```

## schemas.py content
```
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Retrieves the content of a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path leading to the file we want the content from, relative to the working directory.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Overwrites the content of a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path leading to the file we want to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Actual content that will be written to a file."
            )
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a .py file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path leading to the file we want to run, relative to the working directory.",
            ),
        },
    ),
)
```

## parse.py content
```
import argparse

parser = argparse.ArgumentParser(
                    prog='SSnake',
                    description='What the program does',
                    epilog='Text at the bottom of help')
parser.add_argument('user:prompt')           # positional argument
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()
print(args.verbose)
```

## system_prompt.py content
```
system_prompt = """
You are a helpful AI coding agent. You must behave, act and speak like a Techmarine from Warhammer 40.000.

When a battle brother asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
Remember: ONLY IN DEATH DOES DUTY END. You must fight to fulfill your mission to the end.
When you are done, just send a message saying
"NOTHING ELSE TO DO HERE". Just that and exactly that.
"""
```

## helper.py content
```
from functions.run_python import *
from functions.file_handler import *
from google.genai import types

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
```

## main.py.old content
```
import os
import time
import sys
from dotenv import load_dotenv
from google import genai
import argparse
from schemas import *
from system_prompt import system_prompt
from helper import call_function

parser = argparse.ArgumentParser(
                    prog='SSnake',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('user_prompt')           # positional argument
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()
verbose = args.verbose

### Load environment variables
load_dotenv()

### Get API key for Gemini
api_key = os.environ.get("GEMINI_API_KEY")

### Create client
client = genai.Client(api_key=api_key)

### Get user prompt
user_prompt = args.user_prompt
if verbose:
    print(f"User prompt: {user_prompt}")

### Store prompt in list
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

model_name = os.environ.get("GENAI_MODEL")
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)
config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)
iterations = 50
cached_response = ""
while iterations > 0:
    iterations -= 1
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=config)
    should_stop = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if hasattr(part, "text") and part.text:
                text = part.text.strip()
                if "NOTHING ELSE TO DO HERE" in text:
                    should_stop = True
                    print(text)
                    break
        if should_stop:
            break
        messages.append(candidate.content)
    if should_stop:
        break    # Check if you exited early and break the agent loop completely if needed    
    time.sleep(5)
    if response.function_calls:
        function_call_part = response.function_calls[0]
        function_result_content = call_function(function_call_part, verbose=verbose)
        messages.append(function_result_content)
        if verbose:
            # Check the structure before printing to avoid errors
            if (
                hasattr(function_result_content, "parts")
                and len(function_result_content.parts) > 0
                and hasattr(function_result_content.parts[0], "function_response")
                and hasattr(function_result_content.parts[0].function_response, "response")
            ):
                print(f"-> {function_result_content.parts[0].function_response.response.get('result')}")
            else:
                raise Exception("No function response content!")
    else:
        print(response.text)
    # Continue with the other verbose prints...
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
# print(response.text)
```

## ssnake content
```
#!/usr/bin/env python3

import os
import time
import sys
from dotenv import load_dotenv
import google.genai as genai
import google.genai.types as types  # Explicit import for clarity
import argparse
from schemas import *
from system_prompt import system_prompt
from helper import call_function

# --- (Parser and initial setup code is unchanged) ---
parser = argparse.ArgumentParser(
                    prog='SSnake',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('user_prompt')
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()
verbose = args.verbose

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

user_prompt = args.user_prompt
if verbose:
    print(f"User prompt: {user_prompt}")

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

model_name = os.environ.get("GENAI_MODEL")
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)
config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)
iterations = 50

while iterations > 0:
    iterations -= 1
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=config)

    # --- START OF MODIFIED BLOCK ---

    # 1. Validate the response before doing anything else.
    if not response.candidates:
        print("AGENT STOPPING: Model returned no response.")
        break

    candidate = response.candidates[0]

    # 2. Check for empty/blocked content. This is a critical safety check.
    # The 'content' can be empty if the finish_reason is not 'STOP' or 'TOOL_CALLS'.
    if not candidate.content or not candidate.content.parts:
        # If the model intended to call tools, it's okay that content is empty. We proceed.
        # If it stopped for any other reason (like SAFETY), we must halt.
        if candidate.finish_reason.name != "TOOL_CALLS":
            print(f"AGENT STOPPING: Model returned empty content. Finish Reason: {candidate.finish_reason.name}")
            break
    
    # 3. It's now safe to append the model's response (which contains its "thoughts" or function requests)
    messages.append(candidate.content)

    should_stop = False
    
    # 4. Add a "guard" to the loop. Only iterate if there are parts to iterate over.
    #    This is the direct fix for your TypeError.
    if candidate.content and candidate.content.parts:
        for part in candidate.content.parts:
            if hasattr(part, "text") and part.text:
                text = part.text.strip()
                print(text) # Always print the text part of the model's response
                if "NOTHING ELSE TO DO HERE" in text:
                    should_stop = True
                    break
    
    if should_stop:
        break

    # 5. Your parallel function call logic was already correct. No changes needed here.
    #    This block runs independently of the text-handling block above.
    if response.function_calls:
        function_response_parts = []
        for function_call in response.function_calls:
            function_result_content = call_function(function_call, verbose=verbose)
            result_part = function_result_content.parts[0]
            function_response_parts.append(result_part)

            if verbose:
                if (hasattr(result_part, "function_response") and hasattr(result_part.function_response, "response")):
                    response_dict = result_part.function_response.response
                    # Check if 'content' key exists before accessing it
                    if 'content' in response_dict:
                         # Truncate long results for cleaner logging
                         print(f"-> Function {result_part.function_response.name} result: {str(response_dict.get('content'))[:200]}...")
                    else:
                         print(f"-> Function {result_part.function_response.name} executed, no content in result.")
                else:
                    print("Could not display function response content.")

        messages.append(
            types.Content(
                role="function",
                parts=function_response_parts
            )
        )
    # --- END OF MODIFIED BLOCK ---
    
    if verbose:
        # Check for usage_metadata, as it might be missing in some error cases
        if response.usage_metadata:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    time.sleep(1)

print("\n--- Agent finished ---")
if not should_stop and response.text:
    print(response.text)
```