# **EXTENDED TOOLS GUIDELINES**

## **FILE MANAGEMENT**
- **Content**: LLM-friendly, short and concise, non-human language. Avoid humad-friendly flourishes.
- **Processing**: Strive to read and write as less information as possible to save tokens.
  - **Reading**: Prefer reading by chunks - before reading, get the table of contents of a file, choose section, then request the content of that section.
  - **Writing**: Write into files by chunks, small sections with 10-20 lines. Keep sections short but informative. Initialize file with base header structure, or leave empty.

## **AVAILABLE TOOLS**
### **File system**:
  - `create_file`: Initialize a file. Initial content is base header structure; use append_file for large outputs.
  - `delete_file`: Remove specified file. Use cautionously; verify filename with get_filelist first. Avoid deleting critical system files.
  - `get_filelist`: See what files exist. Use before creating new files to avoid duplicates.

### **Chunked file input/output (preferred)**:
- `read_file_section`: Retrieves table of contents as JSON-formatted string. Call again with header name specified in 'section' parameter in format [<start_line> .. <end_line>] to read corresponding file section (e.g. [1 .. 10]). Prefer for markdown-formatted files.

### **Other file input/output**:
- `append_file`: Add content in small portions. Call repeatedly to save tokens.
- `edit_file_content`: Replace a specific line. Line numbers start from 0. Use read_file first if unsure.
- `load_entire_file`: Load whole file content into context. Use with care, token-expensive procedure!
