import os
import requests
import json

max_search_result_length = 3000
max_page_content_length = 5000


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


def complete(**kwargs):

    print("called 'complete' tool!")
    print("argument passed: 'final_thought' = " + kwargs.get("final_thought", "--not used--"))
    return kwargs.get("final_thought", "")
    
    
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
    if "text" in result:
        if len(result["text"]) > max_page_content_length:
            result["text"] = (result["text"][:max_page_content_length] + "... <truncated>")
        print("Browse tool result:\n\n" + result["text"] + "\n")
        return result["text"]
    # else:
    return "Failed to get web page content. Please try another URL"


tool_list = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": """
                Performs Google search to find most actual information.
                Along with thought about your next step please specify following information:
                - summary of search results containing only relevant information for current task.
                - one or two urls if you are going to visit some links from search results.
                That information will remain in message history while other search results will be erased.
                NOTE: snippets of multiple search results may already contain desired info, so actual visiting links is not nessesary in most cases
            """,
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
            "name": "browse_url",
            "description": """
                View content of web-page at specified URL converted to minimalist markdown format. It can be truncated if contents exceed 5000 characters.
                Along with thought about your next step please specify following information:
                - summary of content that you are provided containing only information that is relevant to current task in one or two sentences.
                That summary will persist in message history, while all web-page content will be erased.
                NOTE: It doesn't return full HTML content.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL address of page to read content of",
                    }
                },
                "required": ["url"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete",
            "description": """
                FINAL action - call this ONLY when you are ready to provide the final answer.
                Please summarize the work that has been done during completing task, what actions has been taken and the final result in short.
                **Example compression:**

                ```
                The user requested the current date and year.

                Actions performed:
                1. Search "current date and year today" - 10 results found, key information: March 22, 2026
                2. Visit https://calendar.yoip.ru/today.html - confirmation: Sunday, March 22, 2026

                Result: today is March 22, 2026 (Sunday)
                ```
                That summary will persist in message history while all previous messages are likely to be removed to keep message history as short as possible.
                Please do not invoke any other function call after calling this action, because no other action is neeeded.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "final_thought": {
                        "type": "string",
                        "description": "Result of a completed task as summary of performed actions"
                    },
                },
                "required": ["final_thought"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "think",
            "description": "Just reasoning step with no actions",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis": {
                        "type": "string",
                        "description": "Your thoughts about the reasoning process and current task. Feel free to pass here anything you want"
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
            "description": "Call this to get clarification about current task or some other information from user. Additional opportunity to talk to user and ask about anything you want",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "A short form of your question that user should answer"
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
    "ask_clarification": ask_clarification,
    "complete": complete
}
