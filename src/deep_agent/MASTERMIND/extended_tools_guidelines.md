**EXTENDED TOOLS GUIDELINES**
When you generate files for your internal use, please make it LLM-friendly, short and concise, as such files are not intended to be readable for human.

- `create_file`: Initialize a file. Keep initial content minimal or empty; use append_file for large outputs.
- `append_file`: Add content in small portions. Call repeatedly to avoid token limits.
- `edit_file_content`: Replace a specific line. Line numbers start from 0. Use read_file first if unsure.
- `read_file`: Retrieve file content when you need stored information.
- `get_filelist`: See what files exist. Use before creating new files to avoid duplicates.

Use these tools to manage long-term memory.

