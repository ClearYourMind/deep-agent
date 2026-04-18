# rest_api_tools.py

## imports
import base64
import argparse
import httpx
import json
import os
import toons
from typing import Optional, Dict, Any, Union, List, Tuple

## ---
## variables
rest_api_tool_list = []
rest_api_tool_functions = {}

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
    if result["body"] is not None:
        # Only create TOON for JSON-serializable objects (dict, list, str, int, float, bool, None)
        if isinstance(result["body"], (dict, list, str, int, float, bool)) or result["body"] is None:
            try:
                result["toon"] = toons.dumps(result["body"])
            except (toons.ToonEncodeError, TypeError):
                pass
    return result
### ---

### def rest_api_call(**kwargs):
def rest_api_call(**kwargs):
    # Parse arguments
    method = kwargs.get("method", "GET").upper()
    endpoint = kwargs["endpoint"]
    params = kwargs.get("params", None)
    headers = kwargs.get("headers", None)
    body = kwargs.get("body", None)
    json_body = kwargs.get("json_body", None)
    data = kwargs.get("data", None)
    files = kwargs.get("files", None)
    cookies = kwargs.get("cookies", None)
    auth = kwargs.get("auth", None)
    timeout = kwargs.get("timeout", 30.0)
    follow_redirects = kwargs.get("follow_redirects", True)
    verify_ssl = kwargs.get("verify_ssl", True)
    
    print('arguments: method:', method, ', endpoint:', endpoint, ', params:', params, ', headers:', headers, ', body:', body, ', json_body:', json_body, ', data:', data, ', files:', files, ', cookies:', cookies, ', auth:', auth, ', timeout:', timeout, ', follow_redirects:', follow_redirects, ', verify_ssl:', verify_ssl)
    
    # Prepare headers
    if headers is None:
        headers = {}
    # Set default User-Agent
    if "User-Agent" not in headers:
        headers["User-Agent"] = "Mastermind-REST-API-Tool/1.0"
    
    # Process authentication
    auth_tuple = None
    if auth is not None:
        if isinstance(auth, str):
            if ":" in auth:
                # Basic auth: "username:password"
                auth_tuple = tuple(auth.split(":", 1))
            else:
                # Bearer token
                headers["Authorization"] = f"Bearer {auth}"
        elif isinstance(auth, (list, tuple)) and len(auth) == 2:
            auth_tuple = (str(auth[0]), str(auth[1]))
        else:
            raise ValueError("Unsupported auth format. Use string (Bearer token or 'username:password') or tuple (username, password).")
    
    # Determine request body priority: body > json_body > data > files
    json_data = None
    data_dict = None
    files_dict = None
    content = None
    
    if body is not None:
        # body overrides json_body, data, files
        if isinstance(body, (dict, list)):
            json_data = body
            # Ensure Content-Type if not set
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"
        elif isinstance(body, str):
            content = body.encode("utf-8")
            if "Content-Type" not in headers:
                headers["Content-Type"] = "text/plain; charset=utf-8"
        elif isinstance(body, bytes):
            content = body
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/octet-stream"
        else:
            raise TypeError("body must be dict, list, str, or bytes")
    else:
        # No body, use json_body, data, files
        json_data = json_body
        data_dict = data
        files_dict = files
        # Set Content-Type for json_body if not set
        if json_data is not None and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        # Note: httpx will set Content-Type for data and files automatically
    
    # Convert params, headers, cookies to appropriate types
    # They are already expected as dicts
    
    # Make request
    try:
        with httpx.Client(
            timeout=timeout,
            follow_redirects=follow_redirects,
            verify=verify_ssl,
        ) as client:
            response = client.request(
                method=method,
                url=endpoint,
                params=params,
                headers=headers,
                json=json_data,
                data=data_dict,
                files=files_dict,
                cookies=cookies,
                content=content,
                auth=auth_tuple,
            )
            # Process response using existing module
            result = process_response(response)
    except httpx.RequestError as e:
        # Return error structure
        result = {
            "status_code": 0,
            "headers": {},
            "body": {
                "error": f"Request failed: {str(e)}",
                "type": "RequestError"
            },
            "elapsed": 0.0,
            "url": endpoint
        }
    except Exception as e:
        result = {
            "status_code": 0,
            "headers": {},
            "body": {
                "error": f"Unexpected error: {str(e)}",
                "type": "Exception"
            },
            "elapsed": 0.0,
            "url": endpoint
        }
    
    # Convert to TOON for LLM consumption
    result_toon = toons.dumps(result)
    print("File tool result:", result_toon, "\n\n")
    return result_toon
### ---
### add rest_api_call into tool list
rest_api_tool_functions["rest_api_call"] = rest_api_call
rest_api_tool_list.append({
    "type": "function",
    "function": {
        "name": "rest_api_call",
        "description": "Unified REST API call tool. Supports GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS.",
        "parameters": {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "description": "HTTP method. Default 'GET'. Allowed: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS."
                },
                "endpoint": {
                    "type": "string",
                    "description": "Full API endpoint URL, e.g. 'https://api.github.com/repos/owner/repo'."
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters, will be encoded as URL query string."
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers dictionary. Overrides default headers (like User‑Agent)."
                },
                "body": {
                    "type": ["object", "array", "string"],
                    "description": "Raw request body. If provided, json_body, data, files are ignored."
                },
                "json_body": {
                    "type": ["object", "array"],
                    "description": "JSON serializable object, automatically sets Content‑Type: application/json."
                },
                "data": {
                    "type": "object",
                    "description": "Form‑encoded data, automatically sets Content‑Type: application/x‑www‑form‑urlencoded."
                },
                "files": {
                    "type": "object",
                    "description": "Multipart file upload, format {'file': 'file content or path'}."
                },
                "cookies": {
                    "type": "object",
                    "description": "Cookies dictionary, sent with request."
                },
                "auth": {
                    "type": ["string", "array"],
                    "description": "Authentication. If string, Bearer token; if tuple (username, password), HTTP Basic."
                },
                "timeout": {
                    "type": "number",
                    "description": "Request timeout in seconds. Default 30.0."
                },
                "follow_redirects": {
                    "type": "boolean",
                    "description": "Whether to automatically follow redirects. Default True."
                },
                "verify_ssl": {
                    "type": "boolean",
                    "description": "Whether to verify SSL certificates. Default True."
                }
            },
            "required": ["endpoint"]
        },
    }
})
#### ---
### ---
## ---