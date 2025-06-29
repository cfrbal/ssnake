from helper import call_function
import utils
from google.genai import types

def process_function_calls(response, messages, verbose):
    if response.function_calls:
        function_response_parts = []
        for function_call in response.function_calls:
            function_result_content = call_function(function_call, verbose=verbose)
            result_part = function_result_content.parts[0]
            function_response_parts.append(result_part)

            if verbose:
                if (hasattr(result_part, "function_response") and hasattr(result_part.function_response, "response")):
                    response_dict = result_part.function_response.response
                    if 'content' in response_dict:
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

