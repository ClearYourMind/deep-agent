# Crafted Skills Library

A collection of Python utilities developed for the MASTERMIND autonomous agent system. These tools solve common problems and provide reusable functionality.

## Available Tools

### 1. topic_manager.py
**Purpose**: Manages a collection of topics for Telegram posts. Helps maintain topic variety and track usage.

**Commands**:
- `next` - Get the next unused topic (or oldest used if all are used)
- `list` - List all topics with usage status
- `mark <topic_id>` - Mark a topic as used (updates last_used date)
- `add <title>` - Add a new topic (auto-generates ID)
- `stats` - Show usage statistics

**Usage Examples**:
```bash
python topic_manager.py next
	# Output: Next topic: Робототехника и военные технологии (ID: military_robotics)

python topic_manager.py list
python topic_manager.py mark military_robotics
python topic_manager.py add "Новая тема для обсуждения"
python topic_manager.py stats
```

**Data Storage**: Topics are stored in `topic_data.json` (created automatically with default topics).

### 2. file_reader.py
**Purpose**: Safely read specific lines from a file with bounds checking.

**Usage**: `python file_reader.py <filename> <start_line> <line_count>`

**Features**:
- Limits reading to 50 lines maximum
- 0-based line numbering
- Error handling for missing files and invalid ranges
- Returns file metadata and content

**Example**:
```bash
python file_reader.py "memory.txt" 10 20
	# Reads lines 10-29 (20 lines total)
```

### 3. search_in_file.py
**Purpose**: Search for patterns in a file using regular expressions.

**Usage**: `python search_in_file.py <filename> [pattern1 pattern2 ...]`

**Features**:
- Case-insensitive search
- Multiple pattern support
- Line number reporting
- Returns first 100 characters of matching lines

**Examples**:
```bash
	# Search for "memory" or "agent"
python search_in_file.py "notes.txt" memory agent

	# Search for any line (no pattern)
python search_in_file.py "notes.txt"
```

### 4. rest_api_client.py
**Purpose**: Universal REST API client with support for multiple HTTP methods, authentication, file uploads, and binary data.

**Import as Module**:
The functionality is also available as a Python module for programmatic use within MASTERMIND.
```python
from crafted_skills.rest_api_module import call_api, send_request

# Convenient API with native Python types
result = call_api(
    method='GET',
    endpoint='https://api.example.com/data',
    params={'page': 1},
    headers={'X-Custom': 'value'},
    json_body={'key': 'value'},
    timeout=10.0
)

# CLI-compatible function (accepts argparse.Namespace)
# Used by rest_api_client.py script
```

**Usage**: `python rest_api_client.py [method] <endpoint> [options]`

**Options**:
- `--params <json>` - Query parameters as JSON string
- `--headers <json>` - HTTP headers as JSON string
- `--body <string>` - Request body (string, JSON, or base64 for binary)
- `--json-body <json>` - JSON body (overrides --body)
- `--data <json>` - Form data as JSON string
- `--files <json>` - Files dict as JSON string
- `--cookies <json>` - Cookies as JSON string
- `--auth <string>` - Authentication as 'user:pass' or token string
- `--timeout <float>` - Timeout in seconds (default: 30.0)
- `--follow-redirects/--no-follow-redirects` - Follow redirects (default: True)
- `--verify-ssl/--no-verify-ssl` - Verify SSL (default: True)
- `--output-format <json|toon>` - Output format (default: json)
- `--verbose` - Print debug info to stderr

**Output Format**:
- With `--output-format json` (default) the script outputs a JSON object with the following structure:
  - `status`: HTTP status code
  - `headers`: response headers as dict
  - `body`: response body (string, JSON object, or metadata dict for binary data)
  - `toon`: TOON-serialized body (if `toons` package is available)
- For binary responses (non-JSON, non-text) the `body` field contains a metadata dictionary:
  - `status`: "binary data received"
  - `size`: size in bytes
  - `content_type`: content type from headers
  - `suggested_action`: recommendation (e.g., "使用专用下载工具或存储到文件")
- With `--output-format toon` the output is serialized in TOON binary format.

**Example output for binary response**:
```json
{
  "status": 200,
  "headers": {"content-type": "image/png"},
  "body": {
    "status": "binary data received",
    "size": 1024,
    "content_type": "image/png",
    "suggested_action": "使用专用下载工具或存储到文件"
  },
  "toon": null
}
```

**Features**:
- Supports GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
- Automatic JSON parsing of response
- Binary response encoding as base64
- TOON serialization for token efficiency (if `toons` package installed)
- Error handling with JSON error output

**Examples**:
```bash
	# GET request with query parameters
python rest_api_client.py GET "https://api.example.com/data" --params '{"page": 1, "limit": 10}'

	# POST JSON request
python rest_api_client.py POST "https://api.example.com/create" --json-body '{"name": "test"}'

	# POST with file upload
python rest_api_client.py POST "https://api.example.com/upload" --files '{"file": "/path/to/file.txt"}'

	# GET with authentication
python rest_api_client.py GET "https://api.example.com/private" --auth "user:pass"
```

**Dependencies**: `httpx` (required), `toons` (optional for TOON serialization)


### ---
### ---
### ---
## ---
## Integration with MASTERMIND

These tools are designed to be called via the `run_python_script` tool:

```python
# Example: Get next topic
run_python_script("crafted_skills/topic_manager.py", "next")

# Example: Read lines from file
run_python_script("crafted_skills/file_reader.py", "memory.txt 0 10")

# Example: Search in file
run_python_script("crafted_skills/search_in_file.py", "notes.txt AI automation")
```

## Best Practices

1. **Examine scripts** before running if unsure about functionality
2. **Test with simple commands** before complex operations
3. **Use appropriate error handling** - all scripts return error messages
4. **Check return codes** - scripts exit with code 0 on success, 1 on error
5. **Maintain topic variety** - use `topic_manager.py stats` to track usage

## Development Guidelines

- New tools should follow the same pattern: single-purpose, command-line interface
- Include proper error handling and user feedback
- Document usage in this README
- Keep scripts under 2000 bytes when possible for easier loading
- Use UTF-8 encoding for text files

## Future Extensions

Potential tools to add:
- Data analysis utilities
- Web scraping helpers
- File conversion tools
- Task automation scripts

## ---

*Last updated: 2026-04-18*
