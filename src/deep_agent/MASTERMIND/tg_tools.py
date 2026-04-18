# tg_tools.py
## **TELEGRAM TOOLS GUIDELINES**
"""
- `send_chat_message`: Call to send message as reply or stand-alone post to the Telegram chat. Specify accurate exact `chat_id`.
- `read_chat_updates`: Call to see if any new messages appeared in the Telegram chat during reasoning process. Specify accurate exact `chat_id`.

"""

## imports
import json
import time
import toons

## variables
tg_tool_list = []
tg_tool_functions = {}

CHAT_REFRESH_TIME = 30

## def send_chat_message(**kwargs):
def send_chat_message(**kwargs):
    chat_id = kwargs['chat_id']
    message = kwargs['message']
    tgbot = kwargs["tg_bot"]
    if tgbot:
        tgbot.reply(message, chat_id)
    return message

tg_tool_functions["send_chat_message"] = send_chat_message
tg_tool_list.append({
    "type": "function",
    "function": {
        "name": "send_chat_message",
        "description": "Call to send message as reply or stand-alone post to the Telegram chat. Specify accurate exact chat_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "integer",
                    "description": "chat_id of the chat to send the message."
                },
                "message": {
                    "type": "string",
                    "description": "Reply or post to send to Telegram chat."
                },
            },
            "required": ["chat_id", "message"]
        },
    },
})


## def read_chat_updates(**kwargs):
def read_chat_updates(**kwargs):
	chat_id = kwargs['chat_id']
	tgbot = kwargs["tg_bot"]
	# time.sleep(CHAT_REFRESH_TIME)
	if tgbot:
		tgbot.get_updates(CHAT_REFRESH_TIME)
		tg_updated_chats = tgbot.get_chats()
#		tg_new_messages = tg_updated_chats.get(chat_id, [])
		return toons.dumps(tg_updated_chats)

	return "Wrong Tg_bot object"


tg_tool_functions["read_chat_updates"] = read_chat_updates
tg_tool_list.append({
    "type": "function",
    "function": {
        "name": "read_chat_updates",
        "description": "Call to see if any new messages appeared in the chat during reasoning process. Specify accurate exact `chat_id`.",
        "parameters": {
            "type": "object",
            "properties": {
                # "chat_id": {
                #     "type": "integer",
                #     "description": "chat_id of the Telegram chat to check for new messages"
                # },
            },
            # "required": ["chat_id"]
        },
    },
})
