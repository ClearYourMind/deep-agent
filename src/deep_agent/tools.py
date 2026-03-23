import os
import requests
import json

max_search_result_length = 3000
max_page_content_length = 7000


def search_web(**kwargs):
    print("called 'search_web' tool!")
    print("argument passed: 'query' = " + kwargs["query"])
    
    url = "https://google.serper.dev/search"
    payload = {
        'q': kwargs["query"]
    }
    headers = {
        'X-Api-Key': os.environ.get("SERPER_API_KEY"),
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    result = json.loads(response.text)
    print("search tool result:\n\n" + str(result["organic"][:max_search_result_length]) + "\n")
    return str(result["organic"][:max_search_result_length])


def think(**kwargs):
    print("called 'think' tool!")
    print("argument passed: 'analysis' = " + kwargs["analysis"])
    return kwargs["analysis"]
	
	
def ask_clarification(**kwargs):
    print("called 'ask_clarification' tool!")
    print("argument passed: 'question' = " + kwargs["question"])
    answer = input()
    return answer


def browse_url(**kwargs):
    print("called 'browse_url' tool!")
    print("argument passed: 'url' = " + kwargs["url"])
    
    url = "https://scrape.serper.dev"

    payload = {
      "url": kwargs["url"],
      "includeMarkdown": True
    }
    headers = {
      'X-API-KEY': os.environ.get("SERPER_API_KEY"),
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    result = json.loads(response.text)
    if "markdown" in result:
        if len(result["markdown"]) > max_page_content_length:
            result["markdown"] = (result["text"][:max_page_content_length] + "... <truncated>")
        print("Browse tool result:\n\n" + result["markdown"] + "\n")
        return result["markdown"]
    else:
        return "Failed to get web page content. Please try another URL"


tool_list = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Performs a Google search and returns results with titles, snippets, and URLs. Use this when you need current or external information. After receiving results, you must summarize the relevant findings in your response, as the raw search results may be removed from history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                    "description": "The search query. Use specific, well‑formed phrases."
                    }
                },
                "required": ["query"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browse_url",
            "description": "Fetches the content of a URL and converts it to minimalist Markdown (truncated if over 7000 characters). Use this to retrieve detailed information from a specific page. After receiving content, summarize the relevant parts in your response; the full page content may be discarded from history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL of the page to read."
                    }
                },
                "required": ["url"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "think",
            "description": "Use this to record internal reasoning steps without performing any external action. Optional; you can also reason directly in your response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis": {
                        "type": "string",
                        "description": "Your internal thoughts about the task, plan, or reasoning."
                    },
                },
                "required": ["analysis"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ask_clarification",
            "description": "Call this when the user's request is ambiguous, missing details, or when you need additional information before proceeding. Use a concise question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the user. Keep it short and specific."
                    },
                },
                "required": ["question"]
            },
        },
    },
]

tool_functions = {
    "search_web": search_web,
    "browse_url": browse_url,
    "think": think,
    "ask_clarification": ask_clarification
}
