import sys
import os

def read_lines(file_name, start_line, line_count):
    if line_count > 50:
        line_count = 50
    
    if not os.path.exists(file_name):
        return f"Error: file '{file_name}' not found"
    
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return f"Error reading file: {e}"
    
    total_lines = len(lines)
    if start_line < 0 or start_line >= total_lines:
        return f"Error: start_line {start_line} out of range (0-{total_lines-1})"
    
    end_line = start_line + line_count
    if end_line > total_lines:
        end_line = total_lines
        line_count = end_line - start_line
    
    selected_lines = lines[start_line:end_line]
    content = ''.join(selected_lines).rstrip('\n')
    
    result = []
    result.append(f"файл {file_name} содержит {total_lines} строк.")
    result.append(f"запрошены строки: с {start_line} по {end_line-1}")
    result.append("считанное содержимое:")
    result.append("")
    result.append(content)
    if end_line == total_lines:
        result.append("*конец файла*")
    
    return '\n'.join(result)

def main():
    if len(sys.argv) != 4:
        print("Usage: python file_reader.py <file_name> <start_line> <line_count>")
        print("start_line: 0-based line number")
        print("line_count: max 50 lines")
        sys.exit(1)
    
    file_name = sys.argv[1]
    try:
        start_line = int(sys.argv[2])
        line_count = int(sys.argv[3])
    except ValueError:
        print("Error: start_line and line_count must be integers")
        sys.exit(1)
    
    result = read_lines(file_name, start_line, line_count)
    print(result)

if __name__ == "__main__":
    main()