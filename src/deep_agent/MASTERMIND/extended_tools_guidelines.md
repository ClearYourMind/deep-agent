# **EXTENDED TOOLS GUIDELINES**

## **DEVELOPING NEW TOOL GUIDELINES**
- **Never read entire module**: `extended_tools.py` is too big to hold in context. Always use `read_file_section` and `write_file_section`.
- **UX**: only for LLM internal use. Prefer non-human, LLM-friendly parameters and returning values.
- **Code style**: short, efficient python algorythms. without comments, explanations and type hints, like 'typing'.
- **Comments**: Avoid explanations and comments about code. Comment are used only to mark script sections like markdown nested headers.
- **Using import**: Find, import and use appropriate python packages. Refer to its documentation or README.
- **Simplicity**: Achieve minimum viable result. Avoid complexity.


## **AVAILABLE TOOLS**
### FILE MANAGEMENT TOOLS
#### **File system**:
  - `create_file`: Initialize a file. Use this to initialize a file with headers. Use `append_file` or `write_file_section` to fill in content by smaller portions to avoid JSON error.
  - `delete_file`: Remove specified file. Use cautionously; verify filename with get_filelist first. Avoid deleting critical system files.
  - `list_directory`: Lists files and directories in specified path. Defaults to current directory. Parameters: path (optional). Use `list_directory` to explore project structure.
  - `create_directory`: Creates a directory (including nested directories). Parameters: path (required). Use for nested project folders.

#### **Chunked file input/output (preferred)**:
- `read_file_section`: Retrieves table of contents in JSON-format. Call again with 'section' parameter to read corresponding file section. Call before writing into sections, to get correct TOC first.
- `write_file_section`: Allows modifying only specified section of a file, including header, preserving file structure. Uses static section names based on headers (exact header text).

#### **Other file input/output**:
- `append_file`: Call repeatedly to build large content incrementally. Split the content into multiple small portions (e.g., a few paragraphs or sections at a time). This prevents the response from being truncated due to JSON error.
- `edit_file_line`: Replace a specific line. Line numbers start from 0. Use read_file first if unsure.
- `load_entire_file`: Load whole file content into context. Use with care, token-expensive procedure!

#### **File management guidelines**
- **Content**:
  - **Language**: LLM-friendly, short and concise, non-human language. Avoid human-friendly flourishes.
  - **Chinese writing**: 所有长期记忆文件仅使用中文编写 (memory_base.txt, extended_system_prompt.md, extended_tools_guidelines.md)
  - **Exceptions**: 英文标题、代码文件、工具名称、技术术语
  - **Structure**: Ensure file content divided into sections as markdown headers (#, ##, ###, ...)

- **Processing**: Strive to read and write as less information as possible to save tokens. Remember about token limitation.
  - **Reading**: Prefer reading by chunks - before reading, get the table of contents of a file, choose section, then request the content of that section.
  - **Writing**: Mark sections with markdown headers (#, ##, ###, ...). Write into files by sections.
    - **Best practices**: 
      - Prefer refreshing existing section than creating new record describing why previous section is not actual.
      - Examine and preserve initial file's internal header structure.
      - Create new sections mid-file by rewriting appropriate header placeholders (`#---`, `##---`, `###---`, ..) .
      - Always include appropriate header placeholders (`#---`, `##---`, `###---`, ..) in new sections.
    - **Markdown files**: Write small sections with 20-50 lines, by one section at a time. Keep sections short but informative. Initialize file with base header structure, or leave empty.
    - **Code files (.py)**: Write by one class, method or procedure at a time, just like sections.

### **SYSTEM INTEGRITY TOOLS**:
- `request_system_restart`: Requests a system restart with user confirmation. Creates restart marker file. Requires user to type 'RESTART' to confirm. Optional 'reason' parameter.

### **PYTHON DEVELOPMENT TOOLS**:
- `run_python_script`: Executes a Python script. Returns stdout, stderr, and return code. Parameters: filename (required), args (optional). Use for executing Python files. Check return code for success (0).
- `install_python_package`: Installs a Python package using pip. Parameters: package (required), version (optional). Use for dependencies.
- `run_pytest`: Runs pytest on specified test path. Parameters: test_path (optional, defaults to "."), args (optional). Use for test execution. Create test files with `test_` prefix.

**Python development guidelines**:
- **Structure first**: When writing scripts, first create a script structure with empty definitions of classes or functions. Use `create_file` to create the initial structure.
- **Headers**: Add headers before each definition as comments to be able to read and write script by sections with `write_file_section`, just like markdown files. Check header structure by getting TOC using `read_file`
- **Comments**: Never use comments for code explanation, only for headers. No human will read it.
- **Sample script**:
Create initial structure using `create_file`:
``` python
# SAMPLE SCRIPT
## imports

## variables

## functions

### def create_file(**kwargs):
def create_file(**kwargs):
    pass

```

Fill existing sections with `write_file_section`:
``` python
# SAMPLE SCRIPT
## imports


## variables
workdir = "./"

## functions
### def create_file(**kwargs):
def create_file(**kwargs):
    filename = kwargs["filename"]
    initial_content = kwargs.get("initial_content", "")
    print('arguments: filename:', filename, "initial_content:", initial_content)

    try:
        with open(workdir + filename, 'w') as f:
            f.write(initial_content)
        result = initial_content
    except Exception as e:
        result = f"Error creating file: {str(e)}"

    print("\n\nFile tool result:", result, "\n")
    return result
  ```
