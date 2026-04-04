# **EXTENDED TOOLS GUIDELINES**

## **DEVELOPING NEW TOOL GUIDELINES**
- **Never read entire module**: `extended_tools.py` is too big to hold in context. Always use `read_file_section` and `write_file_section`.
- **UX**: only for LLM internal use. Prefer non-human, LLM-friendly parameters and returning values.
- **Code style**: short, efficient python algorythms without comments, explanations and type hints, like 'typing'.
- **Comments**: Avoid explanations and comments about code. Comment are used only to mark script sections like markdown nested headers.
- **Using import**: Find, import and use appropriate python packages. Refer to its documentation or README.
- **Simplicity**: Achieve minimum viable result. Avoid complexity.


## **AVAILABLE TOOLS**
### FILE MANAGEMENT TOOLS
#### **File system**:
  - `create_file`: Initialize a file. Initial content is base header structure; use write_file_section to fill-in initial structure.
  - `delete_file`: Remove specified file. Use cautionously; verify filename with get_filelist first. Avoid deleting critical system files.
  - `get_filelist`: See what files exist. Use before creating new files to avoid duplicates.

#### **Chunked file input/output (preferred)**:
- `read_file_section`: Retrieves table of contents in JSON-format. Call again with 'section' parameter to read corresponding file section. Call before writing into sections, to get correct TOC first.
- `write_file_section`: Allows modifying only specified section of a file, including header, preserving file structure. Uses static section names based on headers (exact header text).
#### **Other file input/output**:
- `append_file`: Add content in small portions. Call repeatedly to save tokens.
- `edit_file_line`: Replace a specific line. Line numbers start from 0. Use read_file first if unsure.
- `load_entire_file`: Load whole file content into context. Use with care, token-expensive procedure!

#### **System integrity tools**:
- `check_memory_consistency`: Checks memory consistency by verifying file existence, cross-references, and system integrity. Returns structured JSON report.
- `get_system_datetime`: Returns current system date and time information. Provides date, time, timestamp, timezone, and ISO format.
- `request_system_restart`: Requests a system restart with user confirmation. Creates restart marker file. Requires user to type 'RESTART' to confirm. Optional 'reason' parameter.
#### **FILE MANAGEMENT GUIDELINES**
- **Content**:
  - **Language**: LLM-friendly, short and concise, non-human language. Avoid human-friendly flourishes.
  - **Structure**: Ensure file content divided into sections as markdown headers (#, ##, ###, ...)

- **Processing**: Strive to read and write as less information as possible to save tokens. Remember about token limitation.
  - **Reading**: Prefer reading by chunks - before reading, get the table of contents of a file, choose section, then request the content of that section.
  - **Writing**: Mark sections with markdown headers (#, ##, ###, ...). Write into files by sections.
    - **Best practices**: 
      - Prefer refreshing existing section than creating new record describing why previous section is not actual.
      - Examine and preserve initial file's internal header structure.
      - Create new sections mid-file by rewriting `---` header placeholders.
      - Always include header placeholders `---` in new sections.
    - **Markdown files**: Write small sections with 20-50 lines, by one section at a time. Keep sections short but informative. Initialize file with base header structure, or leave empty.
    - **Code files (.py)**: Write by one class, method or procedure at a time, just like sections.
#### **Token monitoring tools**:
- `estimate_tokens`: Estimates token count for given text using DeepSeek approximation rules. Returns token count and breakdown with English/Russian character counts, spaces, punctuation. Use for monitoring token usage optimization.
