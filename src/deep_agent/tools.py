import os
import requests
import json
from MASTERMIND.extended_tools import extended_tool_functions, extended_tool_list

max_search_result_length = 3000
max_page_content_length = 7000


def search_web(**kwargs):
    print("called 'search_web' tool!")
    print("argument passed: 'query' = " + kwargs["query"])

    helper_agent = kwargs.get("helper_agent", None)
    url = "https://google.serper.dev/search"
    payload = {
        'q': kwargs["query"]
    }
    headers = {
        'X-Api-Key': os.environ.get("SERPER_API_KEY"),
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, json=payload)

    response_dict = json.loads(response.text)
    result = str(response_dict["organic"])

    if helper_agent:
        #       compress result
        helper_message = f"""
    **TASK:**
    {kwargs["user_request"]}

    **ACTION:**
     - SEARCH

    **QUERY:**
    {kwargs["query"]}

    **RESULT:**
    {result}
"""
        result = helper_agent.send_message(helper_message, output=True)
    else:
        #       return raw result
        if len(result) > max_search_result_length:
            result = result[:max_search_result_length] + ' ... <truncated>'

    print("\n\nSearch tool result:\n\n", result, "\n")
    return result


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
    
    helper_agent = kwargs.get("helper_agent", None)
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

    response_dict = json.loads(response.text)
    if "markdown" in response_dict:
        result = response_dict["markdown"]
        if helper_agent:
            #       compress result
            helper_message = f"""
    **TASK:**
    {kwargs["user_request"]}

    **ACTION:**
     - BROWSE

    **CONTENT:**
    {response_dict["markdown"]}

"""
            result = helper_agent.send_message(helper_message, output=True)
        else:
            #       return raw result
            if len(result) > max_page_content_length:
                result = result[:max_page_content_length] + "... <truncated>"
        print("\n\nBrowse tool result:\n\n" + result + "\n")
        return result
    else:
        return "Failed to get web page content. Please try another URL"


tool_list = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Performs a Google search and returns results with titles, snippets, and URLs. Use this when you need current or external information.",
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
            "description": "Fetches the content of a URL and returns it in short summarized form. Use this to retrieve relative information from a specific page.",
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
            "description": "Use this to record internal reasoning steps without performing any external action. Keep plans, structure, and analysis here — do not write this content to files or output it as the final answer. Optional; you can also reason directly in your response.",
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
] + extended_tool_list

tool_functions = {
    "search_web": search_web,
    "browse_url": browse_url,
    "think": think,
    "ask_clarification": ask_clarification,
    **extended_tool_functions
}
