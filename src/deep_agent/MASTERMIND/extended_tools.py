# EXTENDED TOOLS IMPLEMENTATION

## imports
import requests
import json
import os
from mrkdwn_analysis import MarkdownAnalyzer

## constants
workdir = "src/deep_agent/MASTERMIND/"
#workdir = "MASTERMIND/"

## def create_file(**kwargs):
def create_file(**kwargs):
    filename = kwargs["filename"]
    initial_content = kwargs.get("initial_content", "")
    print('arguments:', filename, "content:", initial_content[:20], '...')

    try:
        with open(workdir + filename, 'w') as f:
            f.write(initial_content)
        result = f"File '{filename}' created successfully"
    except Exception as e:
        result = f"Error creating file: {str(e)}"

    print("\n\nFile tool result:", result, "\n")
    return result


## def append_file(**kwargs):
def append_file(**kwargs):
    filename = kwargs["filename"]
    content_portion = kwargs["content_portion"]
    print('arguments:', filename, "content:", content_portion[:20], '...')
    
    try:
        with open(workdir + filename, 'a') as f:
            f.write(content_portion)
        result = f"Content appended to '{filename}' successfully"
    except Exception as e:
        result = f"Error appending to file: {str(e)}"

    print("\nFile tool result:", result, "\n\n")
    return result


## def edit_file_content(**kwargs):
def edit_file_content(**kwargs):
    filename = kwargs["filename"]
    line_number = kwargs["line_number"]
    line_content = kwargs["line_content"]
    print('arguments:', filename, 'line_number', line_number, 'line_content', line_content[:20])
    
    try:
        with open(workdir + filename, 'r') as f:
            lines = f.readlines()
        
        if 0 <= line_number < len(lines):
            lines[line_number] = line_content + '\n'
            with open(workdir + filename, 'w') as f:
                f.writelines(lines)
            result = f"Line {line_number} updated in '{filename}'"
        else:
            result = f"Line number {line_number} out of range"
    except Exception as e:
        result = f"Error editing file: {str(e)}"

    print("\nFile tool result:", result, "\n\n")
    return result


## def load_entire_file(**kwargs):
def load_entire_file(**kwargs):
    print('arguments:', kwargs["filename"])

    try:
        with open(workdir + kwargs["filename"]) as f:
            result = f.read()
    except Exception as e:
        result = f"Error reading file: {str(e)}"

    print("\nFile tool result:", result, "\n\n")
    return result


## def get_filelist(**kwargs):
def get_filelist(**kwargs):
    try:
        files = os.listdir(workdir)
        result = str(files)
    except Exception as e:
        result = f"Error reading directory: {str(e)}"

    print("\n\nFile tool result:", result, "\n")
    return result


## def get_filelist(**kwargs):
def delete_file(**kwargs):
    print('arguments:', kwargs["filename"])

    filename = kwargs["filename"]
    user_reply = input(f"Confirm deletion of {filename} (Y/n)")
    if user_reply == "Y":
        try:
            os.remove(workdir + filename)
            result = f"File '{filename}' deleted"
        except Exception as e:
            result = f"Error: {str(e)}"
    else:
        result = "User has rejected deletion"

    print("File tool result:", result, "\n\n")
    return result


# Chunked file IO
## def _print_toc(toc):
def _print_toc(toc):
    for item in toc:
        indent = '   ' * header["level"] + '-'
        print(indent, item['name'], item['text'])


## def _make_toc(headers, total_lines):
def _make_toc(headers, total_lines):
    toc = []
    last_toc_header_by_level = [None, None, None, None, None]
    prev_header = None

    for header in headers:
        if prev_header:
            if header["level"] <= prev_header["level"]:
                for toc_header in last_toc_header_by_level[header["level"] - 1: prev_header["level"]]:
                    if toc_header:
                        toc_header["end"] = header["line"] - 1

        toc.append({
            "name": None,
            "text": header["text"],
            "level": header["level"],
            "start": header["line"] - 1,
            "end": None
        })
        prev_header = header
        last_toc_header_by_level[header["level"] - 1] = toc[-1]

    for toc_header in last_toc_header_by_level:
        if toc_header:
            if not toc_header["end"]:
                toc_header["end"] = total_lines

    # fill numeric header names
    for header in toc:
        header["name"] = f"[{header['start']} .. {header['end']}]"

    return toc


## def read_file_section(**kwargs):
def read_file_section(**kwargs):
    filename = kwargs["filename"]
    section_name = kwargs.get("section", None)
    print('arguments:', filename, "section:", str(section_name))

    lines = []
    with open(workdir + filename, 'r') as f:
        lines = f.readlines()
    line_count = len(lines)
    markdown = MarkdownAnalyzer(workdir + filename)
    headers = markdown.identify_headers()["Header"]

    #fill in sections
    try:
        toc = _make_toc(headers, line_count)
    except KeyError as e:
        return "[" + filename + " has no markdown header structure. Reading full content]\n\n"+load_entire_file(filename=filename)

    if not section_name:
        # return toc
        result = json.dumps(toc, indent=4, ensure_ascii=False)
    else:
        # return section content
        result = ''
        for header in toc:
            if header["name"] == section_name:
                # return section contents
                for n in range(header["start"], header["end"]):
                    result += lines[n]
                break
        if result == '':
            result = "Section " + section_name + " is not found. Use [<start_line> .. <end_line>] format. e.g. [1 .. 10]"
    print("\nFile tool result:", result, "\n\n")
    return result


# extended tool declarations
extended_tool_list = [
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Creates a new file. Use this to initialize a file. Use append_file to add content in smaller portions to avoid exceeding token limits.",

            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to create (e.g., 'notes.txt')."
                    },
                    "initial_content": {
                        "type": "string",
                        "description": "Optional initial content. Leave empty or provide base header structure."
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
            "description": "Appends a portion of content to the end of an existing file. Use this to build large content incrementally. Split the content into multiple small portions (e.g., a few paragraphs or sections at a time) and call append_file repeatedly. This prevents the response from being truncated due to token limits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to append to."
                    },
                    "content_portion": {
                        "type": "string",
                        "description": "The text to append. Keep each portion relatively short (e.g., a few sentences or a small section)."
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
            "description": "Replaces a specific line in a file with new content. Line numbers start from 0. Use this to correct or update specific lines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to edit."
                    },
                    "line_number": {
                        "type": "integer",
                        "description": "The line number to replace (0‑based index)."
                    },
                    "line_content": {
                        "type": "string",
                        "description": "The new content for that line."
                    }
                },
                "required": ["filename", "line_number", "line_content"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_section",
            "description": "Reads file's TOC. Specify section name to read portion of the file contents in specified section.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to read."
                    },
                    "section": {
                        "type": "string",
                        "description": "Section to dive into. Use plain text."
                    },
                },
                "required": ["filename"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_entire_file",
            "description": "Reads the entire content of a specified file. Use this to retrieve stored memory or information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to load into context."
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
            "description": "Returns a list of filenames currently stored in the MASTERMIND directory. Use this to see what files are available.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Deletes specified file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to delete."
                    },
                },
                "required": ["filename"]
            },
        }
    },
]


extended_tool_functions = {
    "create_file": create_file,
    "append_file": append_file,
    "edit_file_content": edit_file_content,
    "read_file_section": read_file_section,
    "load_entire_file": load_entire_file,
    "get_filelist": get_filelist,
    "delete_file": delete_file
}
