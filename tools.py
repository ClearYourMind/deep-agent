import os
import requests

tool_list = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Performs Google search to find most actual information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Google search phrase",
                    }
                },
                "required": ["query"]
            },
        }
    },
]


def search_web(query: str):
    url = "https://google.serper.dev/search"
    payload = {
        'q': query
    }
    headers = {
        'X-Api-Key': os.environ.get("SERPER_API_KEY"),
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    return response.text
