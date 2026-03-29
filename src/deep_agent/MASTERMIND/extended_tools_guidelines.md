**EXTENDED TOOLS GUIDELINES**
When you generate files for your internal use, please make it LLM-friendly, short and concise, as such files are not intended to be readable for human.

- `create_file`: Initialize a file. Keep initial content minimal or empty; use append_file for large outputs.
- `append_file`: Add content in small portions. Call repeatedly to avoid token limits.
- `edit_file_content`: Replace a specific line. Line numbers start from 0. Use read_file first if unsure.
- `load_entire_file`: Load whole file content into context. Use with care, token-expensive procedure!
- `get_filelist`: See what files exist. Use before creating new files to avoid duplicates.
- `delete_file`: Remove specified file. Use cautiously; verify filename with get_filelist first. Avoid deleting critical system files.
- `read_file`: Retrieve table of contents. Specify 'section' parameter to read file content in this section. Use full name just as it shown in table of contents. Prefer for markdown-formatted files.

Use these tools to manage long-term memory.
