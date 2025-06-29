# Refactoring Guide for Ssnake

This guide outlines the steps to refactor the `ssnake` script into a more modular and maintainable structure, without altering its core functionality.

## Goals

*   Improve code readability and maintainability.
*   Encapsulate specific logic blocks into reusable functions.
*   Reduce code duplication.

## Refactoring Strategy

The following sections detail the functions to be extracted and the steps to integrate them.

### 1. `parse_arguments()`

**Purpose:** Handles argument parsing using `argparse`.

**Specification:**

*   **Name:** `parse_arguments`
*   **Arguments:** None
*   **Return Value:** A namespace object containing the parsed arguments (e.g., `args`).
*   **Logic:** Extract the current `argparse` block into this function.
*   **Integration:** Replace the original `argparse` block with a call to `parse_arguments()`.
    ```python
    def parse_arguments():
        parser = argparse.ArgumentParser(
                            prog='SSnake',
                            description='What the program does',
                            epilog='Text at the bottom of help')

        parser.add_argument('user_prompt')
        parser.add_argument('--verbose', action='store_true')
        args = parser.parse_args()
        return args

    args = parse_arguments()
    verbose = args.verbose
    ```

### 2. `initialize_gemini_client()`

**Purpose:** Initializes the Gemini client with API key and model name.

**Specification:**

*   **Name:** `initialize_gemini_client`
*   **Arguments:** None
*   **Return Value:** A Gemini client object.
*   **Logic:** Extract the code that loads the environment variables, retrieves the API key, and initializes the Gemini client.
*   **Integration:** Replace the original initialization code with a call to `initialize_gemini_client()`.
    ```python
    def initialize_gemini_client():
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        return client

    client = initialize_gemini_client()
    ```

### 3. `prepare_model_configuration()`

**Purpose:** Prepare the model configuration, including tools (function declarations) and system instruction.

**Specification:**

*   **Name:** `prepare_model_configuration`
*   **Arguments:** `system_prompt` (string).
*   **Return Value:** A `types.GenerateContentConfig` object.
*   **Logic:** Includes creating `available_functions` and `config` objects.
*   **Integration:**
    ```python
    def prepare_model_configuration(system_prompt):
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
        return config

    config = prepare_model_configuration(system_prompt)
    ```

### 4. `process_response(response, messages, verbose)`

**Purpose:** Processes the Gemini model's response, including handling text and function calls.

**Specification:**

*   **Name:** `process_response`
*   **Arguments:** `response` (Gemini response object), `messages` (list of messages), `verbose` (boolean).
*   **Return Value:** A tuple containing:
    *   `should_stop` (boolean): Indicates whether the main loop should stop.
    *   `updated_messages` (list): Updated message list.
*   **Logic:** Encapsulates the entire "MODIFIED BLOCK" in the original code.
*   **Integration:** Replace the original block with a call to `process_response()`. The function must handle validation, empty content, message appending, text processing, and function calls.

    ```python
    def process_response(response, messages, verbose):
        should_stop = False

        # 1. Validate the response before doing anything else.
        if not response.candidates:
            print("AGENT STOPPING: Model returned no response.")
            return True, messages

        candidate = response.candidates[0]

        # 2. Check for empty/blocked content. This is a critical safety check.
        # The 'content' can be empty if the finish_reason is not 'STOP' or 'TOOL_CALLS'.
        if not candidate.content or not candidate.content.parts:
            # If the model intended to call tools, it's okay that content is empty. We proceed.
            # If it stopped for any other reason (like SAFETY), we must halt.
            if candidate.finish_reason.name != "TOOL_CALLS":
                print(f"AGENT STOPPING: Model returned empty content. Finish Reason: {candidate.finish_reason.name}")
                return True, messages

        # 3. It's now safe to append the model's response (which contains its "thoughts" or function requests)
        messages.append(candidate.content)


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

        return should_stop, messages

    # In main loop:
    should_stop, messages = process_response(response, messages, verbose)
    if should_stop:
        break

    ```

### 5. `log_usage_metadata(response, verbose)`

**Purpose:** Logs the usage metadata if verbose is True.

**Specification:**

*   **Name:** `log_usage_metadata`
*   **Arguments:** `response` (Gemini response object), `verbose` (boolean).
*   **Return Value:** None
*   **Logic:** Extract the code that prints prompt and response tokens.
*   **Integration:**
    ```python
    def log_usage_metadata(response, verbose):
        if verbose:
            # Check for usage_metadata, as it might be missing in some error cases
            if response.usage_metadata:
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    log_usage_metadata(response, verbose)
    ```

### Main Loop Refactoring

The main loop should be refactored as follows:

```python
# Initial setup (parse arguments, initialize client, prepare config)

iterations = 50

while iterations > 0:
    iterations -= 1
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=config)

    should_stop, messages = process_response(response, messages, verbose)
    if should_stop:
        break

    log_usage_metadata(response, verbose)
    time.sleep(1)

print("\n--- Agent finished ---")
if not should_stop and response.text:
    print(response.text)

```

## Notes

*   Ensure that each function is thoroughly tested after extraction to maintain existing functionality.
*   Pay close attention to variable scope when moving code into functions.
*   This guide provides a high-level overview; further modularization may be beneficial depending on the complexity of the individual functions.
