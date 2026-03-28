import requests
import json

def create_file(**kwargs):
    ...

def append_file(**kwargs):
    ...

def edit_file_content(**kwargs):
    ...

def read_file(**kwargs):
    ...

def get_filelist(**kwargs):
    ...

extended_tool_list = {
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Use it to create an empty file or with optional short content. Further writing is done by calling `append_file` tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": ""
                    },
                    "initial_content": {
                        "type": "string",
                        "description": "Optional. Short initial content."
                    }
                },
                "required": ["filename"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "append_file",
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": ""
                    },
                    "content_portion": {
                        "type": "string",
                        "description": "Writes a portion of file content to the end of file, preserving previous content"
                    }
                },
                "required": ["filename", "content_portion"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file_content",
            "description": "Use this to edit file content with correct information line by line",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": ""
                    },
                    "line_number": {
                        "type": "integer",
                        "description": "Specify line number to replace"
                    },
                    "line_content": {
                        "type": "string",
                        "description": "correct line"
                    }
                },
                "required": ["filename", "line_number", "line_content"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Use this to read file content",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Specify file name to get contents of"
                    },
                },
                "required": ["filename"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_filelist",
            "description": "Use this to get filenames that you can access",
            "parameters": {
                "type": "object",
                "properties": {
                    "no_parameters": {
                        "type": "string",
                        "description": "This function has no parameters. Do not use it. LLM doesn't allow me to omit it"
                    },
                },
            },
        }
    }
}

extended_tool_functions = {
    "create_file": create_file,
    "append_file": append_file,
    "edit_file_content": edit_file_content,
    "read_file": read_file,
    "get_filelist": get_filelist
}
