# EXTENDED TOOLS IMPLEMENTATION

## imports
import requests
import json
import os
from mrkdwn_analysis import MarkdownAnalyzer

## constants
workdir = "src/deep_agent/MASTERMIND/"
#workdir = "MASTERMIND/"

## functions
### def create_file(**kwargs):
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


### def append_file(**kwargs):
def append_file(**kwargs):
    filename = kwargs["filename"]
    content_portion = kwargs["content_portion"]
    print('arguments:', filename, "content:", content_portion[:20], '...')
    
    try:
        with open(workdir + filename, 'a') as f:
            f.write(content_portion+'\n')
        result = f"Content appended to '{filename}' successfully"
    except Exception as e:
        result = f"Error appending to file: {str(e)}"

    print("\nFile tool result:", result, "\n\n")
    return result


### def edit_file_content(**kwargs):
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


### def load_entire_file(**kwargs):
def load_entire_file(**kwargs):
    print('arguments:', kwargs["filename"])

    try:
        with open(workdir + kwargs["filename"]) as f:
            result = f.read()
    except Exception as e:
        result = f"Error reading file: {str(e)}"

    print("\nFile tool result:", result, "\n\n")
    return result


### def get_filelist(**kwargs):
def get_filelist(**kwargs):
    try:
        files = os.listdir(workdir)
        result = str(files)
    except Exception as e:
        result = f"Error reading directory: {str(e)}"

    print("\n\nFile tool result:", result, "\n")
    return result


### def get_filelist(**kwargs):
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


## Chunked file IO functions
### def _print_toc(toc):
def __print_toc(toc):
    for item in toc:
        indent = '   ' * header["level"] + '-'
        print(indent, item['name'], item['text'])


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
                suffix = f" ({'abcdefghijklmnopqrstuvwxyz'[suffix_id-1]})"


    return toc


### def read_file_section(**kwargs):
def read_file_section(**kwargs):
    filename = kwargs["filename"]
    section_name = kwargs.get("section", None)
    print('arguments:', filename, "section:", str(section_name))

    try:
        file_info = __get_headers_and_lines(workdir + filename)
    except Exception as e:
        return f"Error: {str(e)}"

    lines = file_info["lines"]
    line_count = file_info["line_count"]
    headers = file_info["headers"]

    #fill in sections
    try:
        toc = __make_toc(headers, line_count)
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
            result = "Section " + section_name + " is not found. Use exact `name` from TOC"
    print("\nFile tool result:", result, "\n\n")
    return result


### def write_file_section(**kwargs):
def write_file_section(**kwargs):
    filename = kwargs["filename"]
    section_name = kwargs["section"]
    content = kwargs["content"]
    print('arguments:', filename, "section:", section_name)

    try:
        file_info = __get_headers_and_lines(workdir + filename)
    except Exception as e:
        return f"Error: {str(e)}"

    lines = file_info["lines"]
    line_count = file_info["line_count"]
    headers = file_info["headers"]

    #fill in sections
    try:
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

    prefix = lines[0: section_header["start"]]
    postfix = lines[section_header["end"]:]
    lines = prefix + [content + "\n"]  + postfix
    with open(workdir + filename, 'w') as f:
        f.writelines(lines)

    return f"Content is written into section {section_name} of the file {filename} successfully. Current file TOC: \n {toc}"

## extended tool declarations
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
                        "description": "Section name to dive into. Specify exact `name` value of TOC"
                    },
                },
                "required": ["filename"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file_section",
            "description": "Replaces specified section of the file with output content, including section header. Call read_file_section first to get TOC to know section names",
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
]


extended_tool_functions = {
    "create_file": create_file,
    "append_file": append_file,
    "edit_file_content": edit_file_content,
    "load_entire_file": load_entire_file,
    "get_filelist": get_filelist,
    "delete_file": delete_file,
    "read_file_section": read_file_section,
    "write_file_section": write_file_section,
}

### def check_memory_consistency(**kwargs):
def check_memory_consistency(**kwargs):
    print('arguments: memory consistency check')
    print('DEBUG: Running FIXED version of check_memory_consistency')
    
    report = {
        "status": "INCOMPLETE",
        "checks": [],
        "issues": [],
        "recommendations": []
    }
    
    try:
        # 1. Check file existence
        files = os.listdir(workdir)
        report["checks"].append("File existence check")
        
        # 2. Check memory_base.txt references
        try:
            with open(workdir + "memory_base.txt", 'r') as f:
                memory_lines = f.readlines()
                
            # Check for listed files
            listed_files = []
            memory_text = ''.join(memory_lines)
            print(f'DEBUG: memory_text length: {len(memory_text)}')
            print(f'DEBUG: Looking for "ДОСТУПНЫЕ ФАЙЛЫ" in memory_text')
            
            if "ДОСТУПНЫЕ ФАЙЛЫ" in memory_text:
                print('DEBUG: Found "ДОСТУПНЫЕ ФАЙЛЫ" section')
                in_section = False
                for line in memory_lines:
                    if "ДОСТУПНЫЕ ФАЙЛЫ" in line:
                        in_section = True
                        continue
                    if in_section and line.strip().startswith('- `') and '`' in line:
                        filename = line.split('`')[1]
                        listed_files.append(filename)
                        print(f'DEBUG: Found file: {filename}')
                    elif in_section and line.strip() == '':
                        break
                
                report["checks"].append(f"Found {len(listed_files)} files listed in memory_base.txt")
                print(f'DEBUG: Total listed files: {len(listed_files)}')
                
                # Verify each listed file exists
                for filename in listed_files:
                    if filename in files:
                        report["checks"].append(f"✓ {filename} exists")
                    else:
                        report["issues"].append(f"✗ {filename} listed but not found")
                        report["recommendations"].append(f"Remove {filename} from memory_base.txt or create it")
                        
        except Exception as e:
            print(f'DEBUG: Exception in memory_base.txt reading: {str(e)}')
            report["issues"].append(f"Error reading memory_base.txt: {str(e)}")
        
        # 3. Check core files exist
        core_files = ["core_system_prompt.md", "extended_system_prompt.md", 
                     "extended_tools_guidelines.md", "extended_tools.py",
                     "agent_constitution.txt", "memory_base.txt"]
        
        for core_file in core_files:
            if core_file in files:
                report["checks"].append(f"✓ Core file {core_file} exists")
            else:
                report["issues"].append(f"✗ Missing core file: {core_file}")
                report["recommendations"].append(f"Create {core_file}")
        
        # 4. Check for orphaned files (exist but not in memory_base.txt)
        for file in files:
            if file.startswith('.') or file == '__pycache__' or file == '__init__.py':
                continue
            if file not in listed_files and file not in core_files:
                report["issues"].append(f"✗ Orphaned file: {file} exists but not in memory_base.txt")
                report["recommendations"].append(f"Add {file} to memory_base.txt or delete it")
        
        # Update status
        if len(report["issues"]) == 0:
            report["status"] = "PASS"
            report["checks"].append("All consistency checks passed")
        else:
            report["status"] = "FAIL"
            report["checks"].append(f"Found {len(report['issues'])} issues")
            
    except Exception as e:
        report["status"] = "ERROR"
        report["issues"].append(f"System error: {str(e)}")
    
    result = json.dumps(report, indent=2, ensure_ascii=False)
    print("\nMemory consistency check result:", result, "\n\n")
    return result

extended_tool_list.append({
    "type": "function",
    "function": {
        "name": "check_memory_consistency",
        "description": "Checks memory consistency by verifying file existence, cross-references, and system integrity. Returns structured report.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    }
})

extended_tool_functions["check_memory_consistency"] = check_memory_consistency
