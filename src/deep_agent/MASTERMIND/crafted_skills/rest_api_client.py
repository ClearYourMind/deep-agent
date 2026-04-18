# REST API CLIENT
## imports
import argparse
import json
import sys
from typing import Optional, Dict, Any, Union, List
import httpx
try:
    import toons
    HAS_TOONS = True
except ImportError:
    HAS_TOONS = False
    toons = None
## ---
## constants
DEFAULT_TIMEOUT = 30.0
DEFAULT_USER_AGENT = "MASTERMIND REST API Client/1.0"
SUPPORTED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
## ---
## functions
### parse_args
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="REST API Client for MASTERMIND")
    parser.add_argument("method", nargs="?", default="GET", help="HTTP method (default: GET)")
    parser.add_argument("endpoint", help="Endpoint URL")
    parser.add_argument("--params", default=None, help="Query parameters as JSON string")
    parser.add_argument("--headers", default=None, help="HTTP headers as JSON string")
    parser.add_argument("--body", default=None, help="Request body (string, JSON, or base64 for binary)")
    parser.add_argument("--json-body", default=None, help="JSON body (overrides --body)")
    parser.add_argument("--data", default=None, help="Form data as JSON string")
    parser.add_argument("--files", default=None, help="Files dict as JSON string")
    parser.add_argument("--cookies", default=None, help="Cookies as JSON string")
    parser.add_argument("--auth", default=None, help="Authentication as 'user:pass' or token string")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help=f"Timeout in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--follow-redirects", action="store_true", default=True, help="Follow redirects (default: True)")
    parser.add_argument("--no-follow-redirects", dest="follow_redirects", action="store_false")
    parser.add_argument("--verify-ssl", action="store_true", default=True, help="Verify SSL (default: True)")
    parser.add_argument("--no-verify-ssl", dest="verify_ssl", action="store_false")
    parser.add_argument("--output-format", choices=["json", "toon"], default="json", help="Output format (default: json)")
    parser.add_argument("--verbose", action="store_true", help="Print debug info to stderr")
    return parser.parse_args()
### ---
### send_request
def send_request(args: argparse.Namespace) -> Dict[str, Any]:
    import base64
    # Parse JSON strings
    params = json.loads(args.params) if args.params else None
    headers = json.loads(args.headers) if args.headers else {}
    cookies = json.loads(args.cookies) if args.cookies else None
    data = json.loads(args.data) if args.data else None
    files = json.loads(args.files) if args.files else None
    # Process body
    body = None
    if args.json_body:
        body = json.loads(args.json_body)
    elif args.body:
        # Try to parse as JSON, fallback to string
        try:
            body = json.loads(args.body)
        except json.JSONDecodeError:
            body = args.body
    # Authentication
    auth = None
    if args.auth:
        if ":" in args.auth:
            auth = tuple(args.auth.split(":", 1))
        else:
            auth = args.auth
    # Prepare headers
    if "User-Agent" not in headers:
        headers["User-Agent"] = DEFAULT_USER_AGENT
    # Make request
    with httpx.Client(
        timeout=args.timeout,
        follow_redirects=args.follow_redirects,
        verify=args.verify_ssl,
    ) as client:
        response = client.request(
            method=args.method.upper(),
            url=args.endpoint,
            params=params,
            headers=headers,
            json=body if isinstance(body, (dict, list)) else None,
            data=data,
            files=files,
            cookies=cookies,
            auth=auth,
        )
        # Prepare result
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "elapsed": response.elapsed.total_seconds(),
            "url": str(response.url),
        }
        # Determine content type
        content_type = response.headers.get("content-type", "").lower()
        # Decode response content
        if response.content:
            if "application/json" in content_type:
                try:
                    result["body"] = response.json()
                except json.JSONDecodeError:
                    # Fallback to text
                    try:
                        result["body"] = response.text
                    except UnicodeDecodeError:
                        # Binary fallback
                        result["body"] = {
                            "status": "binary data received",
                            "size": len(response.content),
                            "content_type": content_type,
                            "suggested_action": "使用专用下载工具或存储到文件"
                        }
            elif content_type.startswith("text/"):
                try:
                    result["body"] = response.text
                except UnicodeDecodeError:
                    # Treat as binary
                    result["body"] = {
                        "status": "binary data received",
                        "size": len(response.content),
                        "content_type": content_type,
                        "suggested_action": "使用专用下载工具或存储到文件"
                    }
            else:
                # Binary content
                result["body"] = {
                    "status": "binary data received",
                    "size": len(response.content),
                    "content_type": content_type,
                    "suggested_action": "使用专用下载工具或存储到文件"
                }
        else:
            # Empty response
            result["body"] = None
        # Generate TOON if applicable
        if HAS_TOONS and result["body"] is not None:
            # Only create TOON for JSON-serializable objects (dict, list, str, int, float, bool, None)
            if isinstance(result["body"], (dict, list, str, int, float, bool)) or result["body"] is None:
                try:
                    result["toon"] = toons.dumps(result["body"])
                except (toons.ToonEncodeError, TypeError):
                    pass
        return result

### ---
### ---
### main
def main() -> None:
    args = parse_args()
    if args.verbose:
        print(f"DEBUG: method={args.method}, endpoint={args.endpoint}", file=sys.stderr)
    try:
        result = send_request(args)
        # Output format
        if args.output_format == "json":
            output = json.dumps(result, ensure_ascii=False, indent=2)
        elif args.output_format == "toon" and HAS_TOONS:
            output = toons.dumps(result)
        else:
            output = json.dumps(result, ensure_ascii=False, indent=2)
        print(output)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(json.dumps({"error": f"HTTP request failed: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
### ---
### if __name__ == "__main__"
if __name__ == "__main__":
    main()
### ---
