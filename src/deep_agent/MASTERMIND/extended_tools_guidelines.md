# **EXTENDED TOOLS GUIDELINES**

## **DEVELOPING NEW TOOL GUIDELINES**
- **UX**: only for LLM internal use. Prefer non-human, LLM-friendly parameters and returning values.
- **Code style**: short, efficient python algorythms. without comments, explanations and type hints, like 'typing'.
- **Comments**: Avoid explanations and comments about code.
- **Using import**: Find, import and use appropriate python packages. Refer to its documentation or README.
- **Simplicity**: Achieve minimum viable result. Avoid complexity.

## ---
## **AVAILABLE TOOLS**
### FILE MANAGEMENT TOOLS
#### **File system**:
  - `create_file`: Initialize a file. Use this to initialize a file with headers. Use `append_file` or `write_file_section` to fill in content by smaller portions to avoid JSON error.
  - `delete_file`: Remove specified file. Use cautionously; verify filename with `list_directory` first. Avoid deleting critical system files.
  - `list_directory`: Lists files and directories in specified path. Defaults to current directory. Parameters: path (optional). Use `list_directory` to explore project structure.
  - `create_directory`: Creates a directory (including nested directories). Parameters: path (required). Use for nested project folders.
  - `copy_file`: Copies a file from source to destination. Parameters: source (required), destination (required). Use for backup or duplication of files.
  - `rename_file`: Renames a file from old_name to new_name. Parameters: old_name (required), new_name (required). Use for file reorganization or naming updates.
#### ---

#### **Other file input/output**:
- `append_file`: Call repeatedly to build large content incrementally. Split the content into multiple small portions (e.g., a few paragraphs or sections at a time). This prevents the response from being truncated due to JSON error.
- `load_entire_file`: Load whole file content into context. Works for files under 16 Kbytes. For bigger files use `read_file_section`

#### ---
#### **File management guidelines**
- **Content**:
  - **Language**: LLM-friendly, short and concise, non-human language. Avoid human-friendly flourishes.

- **Processing**: Strive to read and write as less information as possible to save tokens. Remember about token limitation.

#### ---
### ---
### **TELEGRAM TOOLS**:
- `send_chat_message`: Call to send message as reply or stand-alone post to the Telegram chat. Specify accurate exact `chat_id`.
- `read_chat_updates`: Call to see if any new messages appeared in the Telegram chat during reasoning process.

### ---
### **ADVANCED TAVILY BROWSING TOOLS**:
Uses Tavily search engine, built for AI agents, based on Perplexity.
- `tavily_search`: Request to the search engine. Use for searching internet or asking anything.
- `tavily_browse`: Use to extract webpage content at specified URL. Include search query (optional) to get only relevant content.
### ---
### **PYTHON DEVELOPMENT TOOLS**:
- `run_python_script`: Executes a Python script. Returns stdout, stderr, and return code. Parameters: filename (required), args (optional). Use for executing Python files. Check return code for success (0).
- `install_python_package`: Installs a Python package using pip. Parameters: package (required), version (optional). Use for dependencies.
- `run_pytest`: Runs pytest on specified test path. Parameters: test_path (optional, defaults to "."), args (optional). Use for test execution. Create test files with `test_` prefix.

**Python development guidelines**:
- **Automatic use**: Never use interactive elements `input()` and infinite loops `while True`.
- **Structure first**: When writing scripts, first create a script structure with empty definitions of classes or functions. Use `create_file` to create the initial structure.
- **Headers**: Add headers before each definition as comments to be able to read and write script by sections with `write_file_section`, just like markdown files. Check header structure by getting TOC using `read_file_section`
- **Comments**: Never use comments for code explanation, only for headers. No human will read it.

### **REST API TOOLS**:


### ---
## ---
## **CRAFTED SKILLS LIBRARY**:
- **Purpose**: Store reusable Python utilities created during problem-solving
- **Location**: `crafted_skills/` directory
- **Naming**: Descriptive names like `search_in_files.py`, `data_parser.py`
- **Usage**: Call via `run_python_script` with appropriate arguments. Refer to `crafted_skills/README.md`
- **Available skills**:
  - Described in `crafted_skills/README.md`
- **Development pattern**:
  1. Create script to solve immediate problem
  2. Recognize general utility
  3. Refactor and move to `crafted_skills/`
  4. Update skill guidelines in `crafted_skills/README.md`

**Best practices**:
- Examine script code before running if unsure
- Test scripts before complex execution
- Use structured project layouts
## ---
# ---

