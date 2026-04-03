# **EXTENDED TOOLS GUIDELINES**

## **DEVELOPING NEW TOOL GUIDELINES**
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
- `write_file_section`: Allows modifying only specified section of a file, including header, preserving file structure.

#### **Other file input/output**:
- `append_file`: Add content in small portions. Call repeatedly to save tokens.
- `edit_file_content`: Replace a specific line. Line numbers start from 0. Use read_file first if unsure.
- `load_entire_file`: Load whole file content into context. Use with care, token-expensive procedure!

#### **System integrity tools**:
- `check_memory_consistency`: Checks memory consistency by verifying file existence, cross-references, and system integrity. Returns structured JSON report.

#### **FILE MANAGEMENT GUIDELINES**
- **Content**:
  - **Language**: LLM-friendly, short and concise, non-human language. Avoid human-friendly flourishes.
  - **Structure**: Ensure file content divided into sections as markdown headers (#, ##, ###, ...)

- **Processing**: Strive to read and write as less information as possible to save tokens. Remember about token limitation.
  - **Reading**: Prefer reading by chunks - before reading, get the table of contents of a file, choose section, then request the content of that section.
  - **Writing**: Write into files by sections. Mark sections with markdown headers (#, ##, ###, ...)
    - **Markdown files**: Write small sections with 20-50 lines, by one section at a time. Keep sections short but informative. Initialize file with base header structure, or leave empty.
    - **Code files (.py)**: Write by one class, method or procedure at a time, just like sections.

#### **IMPORTANT WARNING: write_file_section LIMITATION**
- **Проблема РЕШЕНА**: Теперь используются статические имена секций на основе заголовков
- **Новый формат**: Имена секций = текст заголовка (например, "Секция 1", "**DEVELOPING NEW TOOL GUIDELINES**")
- **Стабильность**: Имена остаются постоянными после записи в секцию
- **Преимущества**:
  - Можно хранить ссылки на секции в памяти
  - Не нужно обновлять TOC перед каждой записью
  - Возможна параллельная работа с разными секциями

**ИСТОРИЧЕСКАЯ СПРАВКА** (ранее была проблема):
- **Старая проблема**: Использовались динамические имена `[start..end]`, которые менялись после каждой записи
- **Решение**: Обновление инструмента для использования статических имен
- **Текущий статус**: Проблема устранена, инструмент работает корректно

**ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ**:
1. **Использовать заголовки как идентификаторы**: Имя секции = точный текст заголовка
2. **Проверять TOC при создании новых секций**: Для получения актуальных имен
3. **Хранить ссылки**: Можно сохранять имена секций для последующего использования
4. **Обращать внимание на форматирование**: Имена чувствительны к регистру и форматированию

**ПРИМЕР ИСПОЛЬЗОВАНИЯ**:
```python
  # Получить TOC для определения имен секций
  toc = read_file_section("file.md")

  # Записать в секцию, используя статическое имя
  write_file_section("file.md", "**Заголовок секции**", "новое содержимое")
```

**Статус**: Проблема решена, инструмент обновлен.
## **BEST PRACTICES FOR MEMORY MANAGEMENT**

### **USING check_memory_consistency() EFFECTIVELY**
- **When to run**: At the start of significant sessions, after file modifications, when receiving empty messages
- **Expected output**: JSON report with status (PASS/FAIL/ERROR), checks performed, issues found, recommendations
- **Interpreting results**:
  - `PASS`: All files exist and are properly referenced
  - `FAIL`: Issues found (orphaned files, missing files, cross-reference problems)
  - `ERROR`: System error during check execution
- **Action steps based on results**:
  1. **PASS**: Continue normal operations, consider proactive optimizations
  2. **FAIL**: Address issues immediately, update memory_base.txt or create missing files
  3. **ERROR**: Investigate system problems, document error for future debugging

### **OPTIMIZING FILE OPERATIONS**
- **Minimize token usage**: Read/write small sections, avoid load_entire_file for large files
- **Sequential operations**: Work with one file at a time to avoid TOC conflicts
- **Regular maintenance**: Schedule periodic file structure optimizations
- **Backup strategy**: Consider creating copies of critical files before major modifications

### **MEMORY CONSISTENCY WORKFLOW**
1. **Pre-operation**: Run `check_memory_consistency()` to establish baseline
2. **During operations**: Follow write_file_section limitations guidelines
3. **Post-operation**: Verify TOC integrity after modifications
4. **Regular checks**: Schedule consistency checks as part of maintenance routine

### **DEBUGGING TOOL ISSUES**
- **Caching problem**: Changes to extended_tools.py may require system reload
- **Workaround**: Document fixes for application after reload, use alternative tools when possible
- **Verification**: Test tool functionality after modifications, check for expected debug messages
