updates = [
  {
    "id": 1,
    "message": {
      "text": "Hello",
      "chat": {
        "id": 1001,
        "name": "john Doe"
      }
    }
  },
  {
    "id": 2,
    "channel_post": {
      "text": "News",
      "chat": {
        "id": 1002,
        "name": "News"
      }
    }
  },
  {
    "id": 3,
    "lost_connect": {
      "reason": "wifi"
    }
  }

]

for update in updates:
  for k,v in update.items():
    if (type(v).__name__ == "dict") and ("chat" in v) and ("id" in v["chat"]):
      print(k, v)


