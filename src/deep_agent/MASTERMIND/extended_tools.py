# EXTENDED TOOLS
## WARNING - BIG FILE!
## imports
import requests
import json
import os
import datetime
import subprocess
import sys
from mrkdwn_analysis import MarkdownAnalyzer
import toons
from MASTERMIND.tg_tools import tg_tool_functions, tg_tool_list
from MASTERMIND.tavily_tools import tavily_tool_functions, tavily_tool_list
from MASTERMIND.rest_api_tools import rest_api_tool_functions, rest_api_tool_list 

## ---
## module variables
workdir = 'src/deep_agent/MASTERMIND/'
extended_tool_list = tg_tool_list + tavily_tool_list + rest_api_tool_list
extended_tool_functions = {**tg_tool_functions, **tavily_tool_functions, **rest_api_tool_functions}
MAX_FILE_SIZE = 16384


def is_path_safe(path):
    return not (".." in path or path.startswith("/"))

## ---
## functions
### def create_file(**kwargs):
def create_file(**kwargs):
    filename = kwargs["filename"]
    initial_content = kwargs.get("initial_content", "")
    print('arguments:', filename, "content:", initial_content[:20], '...')

    if not is_path_safe(filename):
        return f"Cannot operate on files outside {workdir} or use absolute paths"

    try:
        with open(workdir + filename, 'w') as f:
            f.write(initial_content)
        result = f"File '{filename}' created successfully.\nInitial content written:\n{initial_content}"
    except Exception as e:
        result = f"Error creating file: {str(e)}"

    print("\n\nFile tool result:", result, "\n")
    return result

extended_tool_functions["create_file"] = create_file
extended_tool_list.append({
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Creates a new file. Initializes it with base header structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to create (e.g., 'notes.txt')."
                    },
                    "initial_content": {
                        "type": "string",
                        "description": "Optional initial content (base header structure or empty)."
                    }
                },
                "required": ["filename"]
            },
        }
    }
)


### ---
### def append_file(**kwargs):
def append_file(**kwargs):
    filename = kwargs["filename"]
    section_content = kwargs["section_content"]
    print('arguments:', filename, "content:", section_content[:20], '...')
    
    if not is_path_safe(filename):
        return f"Cannot operate on files outside {workdir} or use absolute paths"
    try:
        # include placeholder at the end of section
        if not section_content.strip().endswith('---'):
            section_content += "\n##### ---\n"

        with open(workdir + filename, 'a') as f:
            f.write(section_content+'\n')
        result = f"Content appended to '{filename}' successfully.\nContent portion written:\n{section_content}"
    except Exception as e:
        result = f"Error appending to file: {str(e)}"

    print("\nFile tool result:", result, "\n\n")
    return result

extended_tool_functions["append_file"] = append_file
extended_tool_list.append({
        "type": "function",
        "function": {
            "name": "append_file",
            "description": "Appends a new section to the end of an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to append to."
                    },
                    "section_content": {
                        "type": "string",
                        "description": "The content of appended section. Keep each section relatively short (20-50 lines)."
                    }
                },
                "required": ["filename", "section_content"]
            },
        }
    }
)

### ---
### def edit_file_line(**kwargs):
        # don't want Agent to use this tool ever
"""
    def edit_file_line(**kwargs):
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
                result = f"Line {line_number} updated in '{filename}'.\nUpdated line:\n {line_content}"
            else:
                result = f"Line number {line_number} out of range"
        except Exception as e:
            result = f"Error editing file: {str(e)}"

        print("\nFile tool result:", result, "\n\n")
        return result

        # extended_tool_functions["edit_file_line"] = edit_file_line
        # extended_tool_list.append({
        #         "type": "function",
        #         "function": {
        #             "name": "edit_file_line",
        #             "description": "Replaces a specific line in a file with new content. Line numbers start from 0. Use this to correct or update specific lines.",
        #             "parameters": {
        #                 "type": "object",
        #                 "properties": {
        #                     "filename": {
        #                         "type": "string",
        #                         "description": "Name of the file to edit."
        #                     },
        #                     "line_number": {
        #                         "type": "integer",
        #                         "description": "The line number to replace (0‑based index)."
        #                     },
        #                     "line_content": {
        #                         "type": "string",
        #                         "description": "The new content for that line."
        #                     }
        #                 },
        #                 "required": ["filename", "line_number", "line_content"]
        #             },
        #         }
        #     }
        # )
"""

### ---
### def get_file_size(file_path):
def get_file_size(file_path):
    if not is_path_safe(file_path):
        return f"Cannot operate on files outside {workdir} or use absolute paths"

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist")

        if not os.path.isfile(file_path):
            raise ValueError(f"'{file_path}' is not a file")

        size = os.path.getsize(file_path)
        return size
    except PermissionError:
        print(f"Permission denied: {file_path}")
        return None
    except Exception as e:
        print(f"Error getting file size: {e}")
        return None

### ---
### def load_entire_file(**kwargs):
def load_entire_file(**kwargs):
    print('arguments:', kwargs["filename"])
    f_path = workdir + kwargs["filename"]
    f_size = get_file_size(f_path)
    if f_size <= MAX_FILE_SIZE:
        try:
            with open(f_path) as f:
                result = f.read()
        except Exception as e:
            result = f"Error reading file: {str(e)}"
    else:
        result = f"The file is bigger than {MAX_FILE_SIZE} bytes and considered to be too big to load into context."

    print("\nFile tool result:", result, "\n\n")
    return result

extended_tool_functions["load_entire_file"] = load_entire_file
extended_tool_list.append(    {
        "type": "function",
        "function": {
            "name": "load_entire_file",
            "description": f"Reads the entire content of a specified file. Use for files smaller {MAX_FILE_SIZE} bytes.",
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
)

### ---
### def delete_file(**kwargs):
def delete_file(**kwargs):
    print('arguments:', kwargs["filename"])

    filename = kwargs["filename"]
    if not is_path_safe(filename):
        return f"Cannot operate on files outside {workdir} or use absolute paths"
    else:
        try:
            os.remove(workdir + filename)
            result = f"File '{filename}' has been deleted"
        except Exception as e:
            result = f"Error: {str(e)}"

    print("File tool result:", result, "\n\n")
    return result

extended_tool_functions["delete_file"] = delete_file
extended_tool_list.append({
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": f"Deletes specified file. Use only for files in {workdir} and its subfolders",
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
)

### def copy_file(**kwargs):
def copy_file(**kwargs):
    source = kwargs["source"]
    destination = kwargs["destination"]
    print('arguments: source:', source, "destination:", destination)

    if not (is_path_safe(source) and is_path_safe(destination)):
        return f"Cannot operate on files outside {workdir} or use absolute paths"
    else:
        try:
            import shutil
            shutil.copy(workdir + source, workdir + destination)
            result = f"File '{source}' copied to '{destination}'"
        except Exception as e:
            result = f"Error copying file: {str(e)}"

    print("File tool result:", result, "\n\n")
    return result

extended_tool_functions["copy_file"] = copy_file
extended_tool_list.append(    {
        "type": "function",
        "function": {
            "name": "copy_file",
            "description": "Copies a file from source to destination",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source file path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination file path"
                    },
                },
                "required": ["source", "destination"]
            },
        }
    },
)

### ---
### def rename_file(**kwargs):
def rename_file(**kwargs):
    old_name = kwargs["old_name"]
    new_name = kwargs["new_name"]
    print('arguments: old_name:', old_name, "new_name:", new_name)

    if not (is_path_safe(old_name) and is_path_safe(new_name)):
        return f"Cannot operate on files outside {workdir} or use absolute paths"
    else:
        try:
            import os
            os.rename(workdir + old_name, workdir + new_name)
            result = f"File '{old_name}' renamed to '{new_name}'"
        except Exception as e:
            result = f"Error renaming file: {str(e)}"

        print("File tool result:", result, "\n\n")
        return result

extended_tool_functions["rename_file"] = rename_file
extended_tool_list.append(    {
        "type": "function",
        "function": {
            "name": "rename_file",
            "description": "Renames a file from old_name to new_name",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_name": {
                        "type": "string",
                        "description": "Current file name"
                    },
                    "new_name": {
                        "type": "string",
                        "description": "New file name"
                    },
                },
                "required": ["old_name", "new_name"]
            },
        }
    },
)

### ---

## ---
## Chunked file IO functions
### def __get_headers_and_lines(markdown_file):
def __get_headers_and_lines(markdown_file):
    result = {}
    markdown = MarkdownAnalyzer(markdown_file)
    result["headers"] = markdown.identify_headers()["Header"]
    with open(markdown_file, 'r') as f:
        result["lines"] = f.readlines()
    if "lines" in result:
        result["line_count"] = len(result["lines"])

    return result


### def _make_toc(headers, total_lines):
def __make_toc(headers, total_lines):
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

    # fill header names
    used_names = []
    for header in toc:
        suffix_id = 0
        suffix = ''
        while True:
            name = header["text"] + suffix
            if name not in used_names:
                header["name"] = name
                used_names.append(name)
                break
            else:
                suffix_id += 1
                suffix = f" ({suffix_id})" if suffix_id > 0 else ""

    return toc

### ---
### def read_file_section(**kwargs):
def read_file_section(**kwargs):
    filename = kwargs["filename"]
    section_name = kwargs.get("section", None)
    print('arguments:', filename, "section:", str(section_name))

    if not is_path_safe(filename):
        return f"Cannot operate on files outside {workdir} or use absolute paths"

    try:
        file_info = __get_headers_and_lines(workdir + filename)

        lines = file_info["lines"]
        line_count = file_info["line_count"]
        headers = file_info["headers"]

        #fill in sections
        toc = __make_toc(headers, line_count)
    except KeyError as e:
        return "[" + filename + " has no markdown header structure. Try reading full content with load_entire_file]"

    if not section_name or section_name == "toc" or section_name == "TOC":
        # return toc
        result = toons.dumps(toc)
    else:
        # return section content
        result = ''
        for header in toc:
            if section_name in header["name"]:
                # return section contents
                for n in range(header["start"], header["end"]):
                    result += lines[n]
                break
        if result == '':
            result = "Section " + section_name + " is not found. Use exact `name` from TOC"
    print("\nFile tool result:\n", result, "\n\n")
    return result

extended_tool_functions["read_file_section"] = read_file_section
extended_tool_list.append(    {
        "type": "function",
        "function": {
            "name": "read_file_section",
            "description": "Reads file's TOC if section name is omitted. Specify section name to read portion of the file contents in specified section.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to read."
                    },
                    "section": {
                        "type": "string",
                        "description": "Section name to dive into. Specify exact `name` value of TOC"
                    },
                },
                "required": ["filename"]
            },
        }
    },
)

### ---
### def write_file_section(**kwargs):
def write_file_section(**kwargs):
    filename = kwargs["filename"]
    section_name = kwargs["section"]
    content = kwargs["content"]
    print('arguments:', filename, "section:", section_name)

    if not is_path_safe(filename):
        return f"Cannot operate on files outside {workdir} or use absolute paths"

    try:
        file_info = __get_headers_and_lines(workdir + filename)

        lines = file_info["lines"]
        line_count = file_info["line_count"]
        headers = file_info["headers"]

        #fill in sections
        toc = __make_toc(headers, line_count)
    except KeyError as e:
        return filename + " has no markdown header structure"

    section_header = None
    for header in toc:
        if header["name"] == section_name:
            section_header = header
            break

    if not section_header:
            return "Section " + section_name + " is not found. Use exact `name` from TOC"

    # make finishing placeholder with same header level
    placeholder = ("#" * section_header["level"]) + " ---"
    # place updated section into file
    prefix = lines[0: section_header["start"]]
    postfix = lines[section_header["end"]:]
    lines = prefix + [content + "\n" + placeholder + "\n"]  + postfix
    with open(workdir + filename, 'w') as f:
        f.writelines(lines)

    result = f"Writing into section {section_name} of the file {filename} is successful. Section content written:\n{content}"
    print("Tool result:\n" + result)
    return content

extended_tool_functions["write_file_section"] = write_file_section
extended_tool_list.append({
        "type": "function",
        "function": {
            "name": "write_file_section",
            "description": "Replaces specified section of the file with output content, including section header. Call read_file first (without section parameter) to get TOC to know section names",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to change."
                    },
                    "section": {
                        "type": "string",
                        "description": "Section to be rewritten. Specify exact `name` value of TOC"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write into section including header. Keep short to avoid token limitation issue (20-50 lines)"
                    },
                },
                "required": ["filename", "section", "content"]
            },
        }
    },
)

### ---

## ---
## Python development tools
### def run_python_script(**kwargs):
def run_python_script(**kwargs):
    filename = kwargs["filename"]
    args = kwargs.get("args", "")
    print("arguments:", kwargs)
    
    for arg in args.split():
        if not is_path_safe(arg):
            return f"Cannot operate on files outside {workdir} or use absolute paths"

    try:
        # Check if file exists in current directory
        if not os.path.exists(os.path.join(workdir, filename)):
            return f"Error: File '{filename}' not found in current directory"
        
        # Run the script
        cmd = [sys.executable, filename]
        if args:
            cmd.extend(args.split())
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=workdir
        )
        
        output = {
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd)
        }
        
        return json.dumps(output, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"Error executing script: {str(e)}"

extended_tool_functions["run_python_script"] = run_python_script
extended_tool_list.append({
    "type": "function",
    "function": {
        "name": "run_python_script",
        "description": "Executes a Python script. Returns stdout, stderr, and return code.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the Python script to execute."
                },
                "args": {
                    "type": "string",
                    "description": "Optional command-line arguments for the script."
                }
            },
            "required": ["filename"]
        },
    }
})

### ---
### def list_directory(**kwargs):
def list_directory(**kwargs):
    path = kwargs.get("path", ".")
    print('arguments: list_directory path:', path)
    if not is_path_safe(path):
        return f"Cannot operate on files outside {workdir} or use absolute paths"

    try:
        if path == ".":
            target_path = workdir
        # elif path.startswith("/"):
        #     target_path = path
        else:
            target_path = os.path.join(workdir, path)
        
        if not os.path.exists(target_path):
            return f"Error: Path '{path}' not found"
        
        items = os.listdir(target_path)
        items = [item + "; " + str(get_file_size(os.path.join(target_path, item))) for item in items]
        result = {
            "path": target_path,
            "items": items,
            "count": len(items)
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"Error listing directory: {str(e)}"

extended_tool_functions["list_directory"] = list_directory
extended_tool_list.append({
    "type": "function",
    "function": {
        "name": "list_directory",
        "description": "Lists files and directories in specified path. Defaults to current directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to list. Use '.' for current directory, absolute path, or relative path."
                }
            },
            "required": []
        },
    }
})

### ---
### def create_directory(**kwargs):
def create_directory(**kwargs):
    path = kwargs["path"]
    print('arguments: create_directory path:', path)
    if not is_path_safe(path):
        return f"Cannot operate on files outside {workdir} or use absolute paths"

    try:
        # if path.startswith("/"):
        #     target_path = path
        # else:
        target_path = os.path.join(workdir, path)
        
        os.makedirs(target_path, exist_ok=True)
        
        result = {
            "path": target_path,
            "created": True,
            "exists": os.path.exists(target_path)
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"Error creating directory: {str(e)}"

extended_tool_functions["create_directory"] = create_directory
extended_tool_list.append({
    "type": "function",
    "function": {
        "name": "create_directory",
        "description": "Creates a directory (including nested directories).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to create. Can be nested path."
                }
            },
            "required": ["path"]
        },
    }
})

### ---
### def install_python_package(**kwargs):
def install_python_package(**kwargs):
    package = kwargs["package"]
    version = kwargs.get("version", "")
    print('arguments: install_python_package package:', package, "version:", version)
    
    try:
        if version:
            package_spec = f"{package}=={version}"
        else:
            package_spec = package
        
        cmd = [sys.executable, "-m", "pip", "install", package_spec]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=workdir
        )
        
        output = {
            "package": package_spec,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd)
        }
        
        return json.dumps(output, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"Error installing package: {str(e)}"

extended_tool_functions["install_python_package"] = install_python_package
extended_tool_list.append({
    "type": "function",
    "function": {
        "name": "install_python_package",
        "description": "Installs a Python package using pip.",
        "parameters": {
            "type": "object",
            "properties": {
                "package": {
                    "type": "string",
                    "description": "Package name to install."
                },
                "version": {
                    "type": "string",
                    "description": "Optional version specification."
                }
            },
            "required": ["package"]
        },
    }
})

### ---
### def run_pytest(**kwargs):
def run_pytest(**kwargs):
    test_path = kwargs.get("test_path", ".")
    args = kwargs.get("args", "")
    print('arguments: run_pytest test_path:', test_path, "args:", args)
    
    try:
        cmd = [sys.executable, "-m", "pytest", test_path]
        if args:
            cmd.extend(args.split())
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=workdir
        )
        
        output = {
            "test_path": test_path,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd)
        }
        
        return json.dumps(output, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"Error running pytest: {str(e)}"

extended_tool_functions["run_pytest"] = run_pytest
extended_tool_list.append({
    "type": "function",
    "function": {
        "name": "run_pytest",
        "description": "Runs pytest on specified test path.",
        "parameters": {
            "type": "object",
            "properties": {
                "test_path": {
                    "type": "string",
                    "description": "Path to test files or directory. Defaults to current directory."
                },
                "args": {
                    "type": "string",
                    "description": "Optional pytest arguments."
                }
            },
            "required": []
        },
    }
})

