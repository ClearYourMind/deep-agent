import httpx
import os
import json
from dotenv import load_dotenv


class Tg_bot:
	def __init__(self):
		self.base_url = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN')}"
		self.thought_thread_id = 3
		self.chat_id = -1003969262771
		self.last_update_id = 342067203
		self.last_messages = None

	def tg_request(self, command, custom_payload=None):
		payload_json = {}
		if custom_payload:
			payload_json.update(custom_payload)

		return httpx.post(
	#		"https://api.ipify.org/",
			self.base_url + "/" + command,
			proxy="socks5://127.0.0.1:1080",
			json=payload_json
		)


	def send_message(self, msg):
		response = self.tg_request("sendMessage", custom_payload={
			"chat_id": self.chat_id,
			"text": msg,
			"disable_notification": True,
			"parse_mode": "MarkdownV2"
		})
		print(response.text)


	def internal_thought(self, msg):
		response = self.tg_request("sendMessage", custom_payload={
			"chat_id": self.chat_id,
			"message_thread_id": self.thought_thread_id,
			"text": msg,
			"disable_notification": True,
			"parse_mode": "MarkdownV2"
		})


	def get_updates(self):
		response = self.tg_request("getUpdates", custom_payload={
			"allowed_updates": ["messages"],
			"timeout": 2,
			"offset": self.last_update_id
		})
		json_response = json.loads(response.text)
		print(json.dumps(json_response, indent=4, ensure_ascii=False))
		if len(json_response["result"]) >= 1:
			self.last_update_id = json_response["result"][-1]["update_id"] + 1
			self.last_messages = [result["message"]["text"] for result in json_response["result"]]
		else:
			self.last_messages = []


	def get_last_messages(self):
		result = ''
		if self.last_messages:
			result = '\n'.join(self.last_messages)
		return result


def main():
	load_dotenv()


if __name__ == "__main__":
	main()