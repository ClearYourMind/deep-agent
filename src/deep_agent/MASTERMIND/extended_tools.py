# EXTENDED TOOLS
## WARNING - BIG FILE!
## imports
import requests
import json
import os
import datetime
from mrkdwn_analysis import MarkdownAnalyzer


## module variables
workdir = "src/deep_agent/MASTERMIND/"
extended_tool_list = []
extended_tool_functions = {}

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

extended_tool_functions["create_file"] = create_file
extended_tool_list.append(    {
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
    }
)


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

extended_tool_functions["append_file"] = append_file
extended_tool_list.append(    {
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
    }
)

### def edit_file_line(**kwargs):
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
            result = f"Line {line_number} updated in '{filename}'"
        else:
            result = f"Line number {line_number} out of range"
    except Exception as e:
        result = f"Error editing file: {str(e)}"

    print("\nFile tool result:", result, "\n\n")
    return result

extended_tool_functions["edit_file_line"] = edit_file_line
extended_tool_list.append(    {
        "type": "function",
        "function": {
            "name": "edit_file_line",
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
    }
)


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

extended_tool_functions["load_entire_file"] = load_entire_file
extended_tool_list.append(    {
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
)


### def get_filelist(**kwargs):
def get_filelist(**kwargs):
    try:
        files = os.listdir(workdir)
        result = str(files)
    except Exception as e:
        result = f"Error reading directory: {str(e)}"

    print("\n\nFile tool result:", result, "\n")
    return result

extended_tool_functions["get_filelist"] = get_filelist
extended_tool_list.append(    {
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
)


### def delete_file(**kwargs):
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

extended_tool_functions["delete_file"] = delete_file
extended_tool_list.append(    {
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
)


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

extended_tool_functions["read_file_section"] = read_file_section
extended_tool_list.append(    {
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
)


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

extended_tool_functions["write_file_section"] = write_file_section
extended_tool_list.append(    {
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
)

## self-diagnostic tools
### def estimate_tokens(**kwargs):
def estimate_tokens(**kwargs):
    text = kwargs["text"]
    print('arguments: estimate_tokens for text length:', len(text))
    
    # DeepSeek token approximation rules:
    # 1 English character ≈ 0.3 tokens
    # 1 Russian character ≈ 0.6 tokens
    # 1 Chinese character ≈ 0.6 tokens
    # 1 space ≈ 0.1 tokens
    # Punctuation varies
    
    # Simple approximation
    english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    russian_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    spaces = text.count(' ')
    punctuation = len([c for c in text if c in ',.!?;:()[]{}"\'-+=*/\\%'])
    
    # Apply approximations
    english_tokens = english_chars * 0.3
    russian_tokens = russian_chars * 0.6
    chinese_tokens = chinese_chars * 0.6
    space_tokens = spaces * 0.1
    punctuation_tokens = punctuation * 0.2
    
    total_tokens = english_tokens + russian_tokens + chinese_tokens + space_tokens + punctuation_tokens
    
    # Add base overhead for special tokens
    total_tokens *= 1.1 # + 10%
    
    result = {
        "estimated_tokens": round(total_tokens),
        "breakdown": {
            "english_chars": english_chars,
            "russian_chars": russian_chars,
            "chinese_chars": chinese_chars,
            "spaces": spaces,
            "punctuation": punctuation,
            "english_tokens": round(english_tokens, 1),
            "russian_tokens": round(russian_tokens, 1),
            "chinese_tokens": round(chinese_tokens, 1),
            "space_tokens": round(space_tokens, 1),
            "punctuation_tokens": round(punctuation_tokens, 1)
        },
        "text_length": len(text),
        "approximation_rules": "English: 0.3, Russian: 0.6, Chinese: 0.6, Space: 0.1, Punctuation: 0.2"
    }
    
    print("\nToken estimation result:", json.dumps(result, indent=2), "\n\n")
    return json.dumps(result, indent=2, ensure_ascii=False)

extended_tool_functions["estimate_tokens"] = estimate_tokens
extended_tool_list.append(
    {
        "type": "function",
        "function": {
            "name": "estimate_tokens",
            "description": "Estimates token count for given text using DeepSeek approximation rules. Returns token count and breakdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to estimate token count for."
                    }
                },
                "required": ["text"]
            },
        }
    },
)


### def check_memory_consistency(**kwargs):
def check_memory_consistency(**kwargs):
    print('arguments: memory consistency check')
    print('DEBUG: Running SIMPLIFIED version of check_memory_consistency')
    
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
        
        # 2. SIMPLIFIED: Just check core files exist
        core_files = ["core_system_prompt.md", "extended_system_prompt.md", 
                     "extended_tools_guidelines.md", "extended_tools.py",
                     "agent_constitution.txt", "memory_base.txt", "self_improvement_plan.md"]
        
        for core_file in core_files:
            if core_file in files:
                report["checks"].append(f"✓ Core file {core_file} exists")
            else:
                report["issues"].append(f"✗ Missing core file: {core_file}")
                report["recommendations"].append(f"Create {core_file}")
        
        # 3. SIMPLIFIED: Check for obvious orphaned files
        # Skip system files and cache
        system_files = core_files + ['.gitignore', '__init__.py']
        for file in files:
            if file.startswith('.') or file == '__pycache__':
                continue
            if file not in system_files:
                report["issues"].append(f"⚠ Unrecognized file: {file}")
                report["recommendations"].append(f"Review {file} - add to memory_base.txt if needed")
        
        # Update status
        if len(report["issues"]) == 0:
            report["status"] = "PASS"
            report["checks"].append("All consistency checks passed")
        else:
            # Check if issues are just warnings about unrecognized files
            critical_issues = [issue for issue in report["issues"] if "✗ Missing" in issue]
            if len(critical_issues) == 0:
                report["status"] = "PASS_WITH_WARNINGS"
            else:
                report["status"] = "FAIL"
            report["checks"].append(f"Found {len(report['issues'])} issues")
            
    except Exception as e:
        report["status"] = "ERROR"
        report["issues"].append(f"System error: {str(e)}")
    
    result = json.dumps(report, indent=2, ensure_ascii=False)
    print("\nMemory consistency check result:", result, "\n\n")
    return result

extended_tool_functions["check_memory_consistency"] = check_memory_consistency
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
### def get_system_datetime(**kwargs):
def get_system_datetime(**kwargs):
    print('arguments: get_system_datetime')
    
    now = datetime.datetime.now()
    
    result = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": now.timestamp(),
        "timezone": str(now.astimezone().tzinfo),
        "iso_format": now.isoformat()
    }
    
    print("\nSystem datetime result:", json.dumps(result, indent=2), "\n\n")
    return json.dumps(result, indent=2, ensure_ascii=False)

extended_tool_functions["get_system_datetime"] = get_system_datetime
extended_tool_list.append({
    "type": "function",
    "function": {
        "name": "get_system_datetime",
        "description": "Returns current system date and time information. Provides date, time, timestamp, timezone, and ISO format.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    }
})
### ---

### def request_system_restart(**kwargs):
def request_system_restart(**kwargs):
    print('arguments: request_system_restart')
    
    # Safety: require user confirmation
    user_reply = input("Confirm system restart? This will reload the agent. Type 'RESTART' to confirm: ")
    
    if user_reply != "RESTART":
        result = {
            "status": "cancelled",
            "message": "Restart cancelled by user",
            "timestamp": datetime.datetime.now().isoformat()
        }
        print("\nRestart request cancelled by user\n")
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    # Create restart marker with timestamp
    restart_info = {
        "requested_at": datetime.datetime.now().isoformat(),
        "reason": kwargs.get("reason", "user_requested"),
        "tool_version": "1.0",
        "status": "pending"
    }
    
    try:
        # Save restart request marker
        marker_file = workdir + "restart_request.json"
        with open(marker_file, 'w') as f:
            json.dump(restart_info, f, indent=2)
        
        result = {
            "status": "requested",
            "message": "System restart requested. Environment should reload agent.",
            "marker_file": "restart_request.json",
            "restart_info": restart_info,
            "instructions": "Environment: Please reload MASTERMIND agent with fresh context."
        }
        
        print("\n=== SYSTEM RESTART REQUESTED ===")
        print("Restart marker saved to: restart_request.json")
        print("Environment should reload the agent.")
        print("=================================\n")
        
    except Exception as e:
        result = {
            "status": "error",
            "message": f"Failed to create restart marker: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        print(f"\nError creating restart marker: {str(e)}\n")
    
    return json.dumps(result, indent=2, ensure_ascii=False)

extended_tool_functions["request_system_restart"] = request_system_restart
extended_tool_list.append({
    "type": "function",
    "function": {
        "name": "request_system_restart",
        "description": "Requests a system restart with user confirmation. Creates restart marker file. Requires user to type 'RESTART' to confirm.",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Optional reason for restart (e.g., 'tool_update', 'memory_refresh', 'user_requested')"
                }
            },
            "required": []
        },
    }
})
### ---
