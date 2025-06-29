import argparse
import os
import sys
import time
import yaml

from dotenv import load_dotenv
import google.genai as genai
import google.genai.types as types

from helper import call_function
from schemas import *
from system_prompt import system_prompt
from utils import *


class SsnakeAgent:
    def __init__(self, user_prompt, verbose=False):
        load_dotenv()
        with open('config.yaml', 'r') as config_file:
            self.internal_config = yaml.safe_load(config_file)
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.verbose = verbose
        self.args = self.parse_arguments()
        self.client = self.initialize_llm_client()
        self.config = self.configure_llm(system_prompt)
        self.messages = [types.Content(role="user", parts=[types.Part(text=self.user_prompt)])]
        print(self.internal_config)
        self.model_name = self.internal_config["GENAI_MODEL"]
    
    def parse_arguments(self):
        parser = argparse.ArgumentParser(
                            prog='SSnake',
                            description='What the program does',
                            epilog='Text at the bottom of help')

        parser.add_argument('user_prompt')
        parser.add_argument('--verbose', action='store_true')
        args = parser.parse_args()
        return args


    def initialize_llm_client(self):
        if self.internal_config["MODEL_API"] == "GEMINI":
            return initialize_gemini_client()

    def configure_llm(self, system_prompt):
        if self.internal_config["MODEL_API"] == "GEMINI":
            return configure_gemini(system_prompt)

    def process_response(self, response):
        should_stop = False

        if not response.candidates:
            print("AGENT STOPPING: Model returned no response.")
            return True, self.messages

        candidate = response.candidates[0]

        if not candidate.content or not candidate.content.parts:
            if candidate.finish_reason.name != "TOOL_CALLS":
                print(f"AGENT STOPPING: Model returned empty content. Finish Reason: {candidate.finish_reason.name}")
                return True, self.messages

        self.messages.append(candidate.content)

        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    text = part.text.strip()
                    print(text)
                    if "NOTHING ELSE TO DO HERE" in text:
                        should_stop = True
                        break

        if response.function_calls:
            function_response_parts = []
            for function_call in response.function_calls:
                function_result_content = call_function(function_call, verbose=self.verbose)
                result_part = function_result_content.parts[0]
                function_response_parts.append(result_part)

                if self.verbose:
                    if (hasattr(result_part, "function_response") and hasattr(result_part.function_response, "response")):
                        response_dict = result_part.function_response.response
                        if 'content' in response_dict:
                             print(f"-> Function {result_part.function_response.name} result: {str(response_dict.get('content'))[:200]}...")
                        else:
                             print(f"-> Function {result_part.function_response.name} executed, no content in result.")
                    else:
                        print("Could not display function response content.")

            self.messages.append(
                types.Content(
                    role="function",
                    parts=function_response_parts
                )
            )

        return should_stop, self.messages

    def log_usage_metadata(self, response):
        if self.verbose:
            if response.usage_metadata:
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    def run(self):
        iterations = 50

        while iterations > 0:
            iterations -= 1
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.messages,
                config=self.config)

            should_stop, self.messages = self.process_response(response)
            if should_stop:
                break

            self.log_usage_metadata(response)
            time.sleep(1)

        print("\n--- Agent finished ---")

if __name__ == "__main__":
    # Example usage:
    # To run this, you would need to pass user_prompt and verbose as command-line arguments.
    # For example: python ssnake_class.py "Summarize the content of file 'my_file.txt'" --verbose
    if len(sys.argv) < 2:
        print("Usage: python ssnake_class.py <user_prompt> [--verbose]")
        sys.exit(1)

    user_prompt = sys.argv[1]
    verbose = False
    if len(sys.argv) > 2 and sys.argv[2] == '--verbose':
        verbose = True

    agent = SsnakeAgent(user_prompt, verbose)
    agent.run()
