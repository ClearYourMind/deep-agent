# REST API CLIENT
## imports
import json
import argparse
from rest_api_module import send_request

## ---
## ---
## ---
## ---
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
# Imported from rest_api_module
### ---
### ---
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
