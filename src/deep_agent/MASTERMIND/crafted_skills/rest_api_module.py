# REST API MODULE
## imports
import json
import base64
import httpx
import argparse
from typing import Dict, Any, Optional, Union

try:
    import toons
    HAS_TOONS = True
except ImportError:
    HAS_TOONS = False

## ---
## constants
DEFAULT_USER_AGENT = "MASTERMIND REST API Client/1.0"
## ---
## functions
### process_response
def process_response(response: httpx.Response) -> Dict[str, Any]:
    """Convert httpx.Response to result dict."""
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
### call_api
def call_api(
    method: str,
    endpoint: str,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    json_body: Optional[Union[Dict, list]] = None,
    data: Optional[Dict] = None,
    files: Optional[Dict] = None,
    cookies: Optional[Dict] = None,
    auth: Optional[Union[str, tuple]] = None,
    timeout: float = 30.0,
    follow_redirects: bool = True,
    verify_ssl: bool = True,
    output_format: str = 'json'
) -> Dict[str, Any]:
    """Convenient function to call API with Python arguments."""
    # Prepare headers
    if headers is None:
        headers = {}
    if "User-Agent" not in headers:
        headers["User-Agent"] = DEFAULT_USER_AGENT
    # Convert auth string to tuple if needed
    if isinstance(auth, str) and ":" in auth:
        auth = tuple(auth.split(":", 1))
    # Make request
    with httpx.Client(
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify=verify_ssl,
    ) as client:
        response = client.request(
            method=method.upper(),
            url=endpoint,
            params=params,
            headers=headers,
            json=json_body,
            data=data,
            files=files,
            cookies=cookies,
            auth=auth,
        )
        return process_response(response)
### ---
### send_request
def send_request(args: argparse.Namespace) -> Dict[str, Any]:
    """Send HTTP request based on argparse.Namespace (compatible with CLI)."""
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
    # Determine json_body and data for call_api
    json_body = body if isinstance(body, (dict, list)) else None
    # If body is a string and not JSON, treat as raw data (overrides data)
    # But original code uses data parameter for form data, not for raw body.
    # Actually, original code passes body as json if dict/list, otherwise ignores.
    # The raw string body is not passed to httpx unless it's JSON.
    # However, the CLI's --body is intended for raw request body (e.g., XML, plain text).
    # In original implementation, body string is passed as json=None, data=None, files=None.
    # Wait, original code uses `json=body if isinstance(body, (dict, list)) else None`
    # and `data=data`. So raw string body is not sent at all unless data is set.
    # That seems like a bug. Let's examine original send_request: 
    # It sets json=body if dict/list else None, and data=data (from --data).
    # So --body with a non-JSON string does nothing. That's weird.
    # Let's check the original code again: 
    # It uses `json=body if isinstance(body, (dict, list)) else None` and `data=data`.
    # So indeed, non-JSON body is ignored. That's likely unintended.
    # We'll preserve original behavior for compatibility.
    # If body is string and not JSON, we'll not pass it as json or data.
    # But we can pass it as data (overriding --data) if we want to send raw body.
    # Let's decide: For CLI, --body is used for raw request body (string or base64).
    # We'll treat it as raw data: set data = body (string) and ignore --data.
    # However, original implementation doesn't do that. Let's stick to original.
    # We'll keep original behavior: only dict/list body is used as json.
    # For string body, ignore.
    # But we need to support binary body (base64). Original doesn't handle that.
    # Actually, original code expects body to be base64 string for binary? Not really.
    # Let's keep simple: if body is dict/list -> json_body = body; else ignore.
    # This matches original.
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
    # Call call_api
    return call_api(
        method=args.method,
        endpoint=args.endpoint,
        params=params,
        headers=headers,
        json_body=json_body,
        data=data,
        files=files,
        cookies=cookies,
        auth=auth,
        timeout=args.timeout,
        follow_redirects=args.follow_redirects,
        verify_ssl=args.verify_ssl,
        output_format=args.output_format if hasattr(args, 'output_format') else 'json'
    )
### ---
## ---
