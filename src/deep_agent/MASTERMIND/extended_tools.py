import requests
import json
import os
from mrkdwn_analysis import MarkdownAnalyzer

workdir = "src/deep_agent/MASTERMIND/"
#workdir = "MASTERMIND/"


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


def load_entire_file(**kwargs):
    result = "<failed to open file>"
    print('arguments:', kwargs["filename"])

    try:
        with open(workdir + kwargs["filename"]) as f:
            result = f.read()
    except Exception as e:
        result = f"Error reading file: {str(e)}"

    print("\nFile tool result:", result, "\n\n")
    return result


def read_file(**kwargs):
    filename = kwargs["filename"]
    section_name = kwargs.get("section", None)
    print('arguments:', filename, "section:", str(section_name))
    markdown = MarkdownAnalyzer(workdir + filename)
    headers = markdown.identify_headers()
    sections = {}
    lines = []
    with open(workdir + filename, 'r') as f:
        lines = f.readlines()
    line_count = len(lines)

    #fill in sections
    current_section = None
    try:
        for header in headers["Header"]:
            if current_section:
                current_section["end"] = header["line"] - 1
                sections[current_section["text"]] = current_section

            current_section = {
                "text": header["text"],
                "level": header["level"],
                "start": header["line"],
                "end": None
            }
        if current_section:
            current_section["end"] = line_count - 1
            sections[current_section["text"]] = current_section
    except KeyError as e:
        result = "File doesn't contain markdown. Use `load_entire_file` instead"
        print("\nFile tool result:", result, "\n\n")
        return result

    if section_name:
        result = "No such section: " + section_name
        section = sections.get(section_name, None)
        if section:
            result = ''
            for i in range(section["start"], section["end"]):
                result += lines[i]
    else:
        toc = ''
        # return table of contents
        for header in headers["Header"]:
            if header["level"] < 3:
                toc +=f"{" "*header["level"]} - {header["text"]} ({header["line"]}) \n"
        if toc:
            result = toc
        else:
            result = "File doesn't contain markdown. Use `load_entire_file` instead"

    print("\nFile tool result:", result, "\n\n")
    return result


def get_filelist(**kwargs):
    try:
        files = os.listdir(workdir)
        result = str(files)
    except Exception as e:
        result = f"Error reading directory: {str(e)}"

    print("\n\nFile tool result:", result, "\n")
    return result


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


extended_tool_list = [
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Creates a new file in the MASTERMIND directory. Use this to initialize a file. Use append_file to add content in smaller portions to avoid exceeding token limits.",

            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to create (e.g., 'notes.txt')."
                    },
                    "initial_content": {
                        "type": "string",
                        "description": "Optional initial content. Leave empty or provide only a brief header."
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
            "name": "read_file",
            "description": "Reads file's TOC or portion of the file contents in specified section.",
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
    "read_file": read_file,
    "load_entire_file": load_entire_file,
    "get_filelist": get_filelist,
    "delete_file": delete_file
}
