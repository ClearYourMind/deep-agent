# tavily_browse.py

## imports
from tavily import TavilyClient
import os
import toons

## ---
## variables
tavily_tool_list = []
tavily_tool_functions = {}

## ---

## functions
### def tavily_search(**kwargs):
def tavily_search(**kwargs):
	query = kwargs["query"]
	print('arguments: query:', query)

	tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
	response = tavily_client.search(
		query=query,
		search_depth="advanced"
	)
	result = toons.dumps(response)
	print("File tool result:", result, "\n\n")
	return result

tavily_tool_functions["tavily_search"] = tavily_search
tavily_tool_list.append({
	"type": "function",
	"function": {
	    "name": "tavily_search",
	    "description": "Request to the search engine. Use for search internet or ask anything.",
	    "parameters": {
	        "type": "object",
	        "properties": {
	            "query": {
	                "type": "string",
	                "description": "Search phrase or question in concise form."
	            }
	        },
	        "required": ["query"]
	    },
	}
})

### ---
### def tavily_browse(**kwargs):
def tavily_browse(**kwargs):
	url = kwargs["url"]
	query = kwargs.get("query", None)
	print('arguments: url:', url, ", query:", query)

	tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
	response = tavily_client.extract(
		urls=[url],
		query=query
	)
	result = toons.dumps(response)
	print("File tool result:", result, "\n\n")
	return result

tavily_tool_functions["tavily_browse"] = tavily_browse
tavily_tool_list.append({
	"type": "function",
	"function": {
	    "name": "tavily_browse",
	    "description": "Use to extract webpage content",
	    "parameters": {
	        "type": "object",
	        "properties": {
	            "url": {
	                "type": "string",
	                "description": "URL of webpage to browse"
	            },
	            "query": {
	                "type": "string",
	                "description": "Include search query to get only relevant content"
	            }
	        },
	        "required": ["url"]
	    },
	}
})

### ---
## ---
