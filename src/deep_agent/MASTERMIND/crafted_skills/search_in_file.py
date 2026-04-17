import sys
import re

def search_in_file(filename, pattern):
    """Search for pattern in file, case-insensitive"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        results = []
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                results.append((i+1, line))
        return results
    except Exception as e:
        return f"Error reading file: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_in_files.py <filename> [pattern1 pattern2 ...]")
        print("If no patterns provided, searches for common patterns")
        sys.exit(1)
    
    filename = sys.argv[1]
    if len(sys.argv) > 2:
        patterns = sys.argv[2:]
    else:
        patterns = ['.*']  # match everything
    
    all_results = []
    for pattern in patterns:
        results = search_in_file(filename, pattern)
        if isinstance(results, str):
            print(f"Error with pattern '{pattern}': {results}")
        else:
            for line_num, line in results:
                all_results.append((pattern, line_num, line))
    
    if all_results:
        print(f"\nFound {len(all_results)} matches in {filename}:")
        for pattern, line_num, line in all_results:
            print(f"Pattern '{pattern}' line {line_num}: {line[:100]}...")
    else:
        print(f"No matches found in {filename}")

if __name__ == "__main__":
    main()