import logging
import argparse
import os
from dotenv import load_dotenv
import google.genai as genai
import google.genai.types as types

from schemas import *

def parse_arguments():
    load_dotenv("prog.env")
    parser = argparse.ArgumentParser(
                        prog=os.environ.get("PROGRAM_NAME"),
                        description=os.environ.get("PROGRAM_DESCRIPTION"),
                        epilog=os.environ.get("PROGRAM_EPILOG"))

    parser.add_argument('user_prompt')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    return args

def initialize_gemini_client():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    return client

def configure_gemini(system_prompt):
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_write_file,
            schema_run_python_file,
            schema_task_complete,
        ]
    )
    config=types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt
    )
    return config

def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()])



def log_error(message):
    logging.error(message)


def log_info(message):
    logging.info(message)
