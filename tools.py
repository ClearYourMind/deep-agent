import os
import requests


def search_web(**kwargs):
    print("called 'search_web' tool!")
    url = "https://google.serper.dev/search"
    payload = {
        'q': kwargs["query"]
    }
    headers = {
        'X-Api-Key': os.environ.get("SERPER_API_KEY"),
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    return response.text


def complete(**kwargs):
    # should ask for next prompt
    print("Filled unused parameter: ", kwargs["placeholder"])
    return ""


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
    {
        "type": "function",
        "function": {
            "name": "complete",
            "description": "Done with the task. Stop invocation cycle",
            "parameters": {
                "type": "object",
                "properties": {
                    "placeholder": {
                        "type": "string",
                        "description": "Just dummy parameter. Do not use"
                    },
                },
            },
        },
    },
]

tool_functions = {
    "search_web": search_web,
    "complete": complete
}
