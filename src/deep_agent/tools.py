import os
import requests
import json

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
    print("search tool result:\n\n" + str(result["organic"]) + "\n")
    return str(result["organic"])


def complete(**kwargs):
    print("called 'complete' tool!")
    print("argument passed: 'final_thought' = " + kwargs.get("final_thought", "--not used--"))
    # should ask for next prompt
    print("Model's final thought: ", kwargs.get("final_thought", "--not used--"))
    return kwargs.get("final_thought", "")
    
    
def think(**kwargs):
    print("called 'think' tool!")
    print("argument passed: 'analysis' = " + kwargs["analysis"])
    # just reasoning step
    print(" >> " + kwargs["analysis"])
    return kwargs["analysis"]
	
	
def ask_clarification(**kwargs):
    print("called 'ask_clarification' tool!")
    print("argument passed: 'question' = " + kwargs["question"])
    # print(" >> " + kwargs["question'])
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
    print("Browse tool result:\n\n" + result["text"] + "\n")
    return result["text"]


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
            "name": "browse_url",
            "description": "View content of web-page at specified URL converted to minimalist markdown format",
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
            "description": "FINAL action - call this ONLY when you are ready to provide the final answer. Please do not invoke any other function call after calling this action, because no other action is neeeded.",
            "parameters": {
                "type": "object",
                "properties": {
                    "final_thought": {
                        "type": "string",
                        "description": "Just dummy parameter. Do not use"
                    },
                },
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
