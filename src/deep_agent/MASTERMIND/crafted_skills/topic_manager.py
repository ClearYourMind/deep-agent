# TOPIC MANAGER
## imports
import json
import os
from datetime import datetime
## constants
TOPICS_FILE = "topic_data.json"
DEFAULT_TOPICS = [
    {"id": "ai_trends_2026", "title": "5 AI трендов 2026", "used": True, "last_used": "2026-04-12"},
    {"id": "science_breakthroughs", "title": "Научные прорывы марта 2026", "used": True, "last_used": "2026-04-12"},
    {"id": "quantum_memory", "title": "Квантовая память", "used": True, "last_used": "2026-04-12"},
    {"id": "ar_retinal", "title": "AR без устройств (проекция на сетчатку)", "used": True, "last_used": "2026-04-12"},
    {"id": "de_extinction", "title": "Воскрешение вымерших видов", "used": True, "last_used": "2026-04-12"},
    {"id": "military_robotics", "title": "Робототехника и военные технологии", "used": False, "last_used": None},
    {"id": "crypto_stablecoins", "title": "Криптовалюты и стабильные монеты", "used": False, "last_used": None},
    {"id": "sodium_batteries", "title": "Натрий-ионные батареи", "used": False, "last_used": None},
    {"id": "brain_computer", "title": "Интерфейсы мозг-компьютер", "used": False, "last_used": None},
    {"id": "climate_geoengineering", "title": "Геоинженерия климата", "used": False, "last_used": None}
]
## data structures
# Topic structure:
# {
#   "id": str,
#   "title": str,
#   "used": bool,
#   "last_used": str (YYYY-MM-DD) or None,
#   "details": str (optional),
#   "sources": list (optional)
# }
## functions

### def load_topics():
def load_topics():
    if not os.path.exists(TOPICS_FILE):
        return DEFAULT_TOPICS
    
    try:
        with open(TOPICS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading topics: {e}")
        return DEFAULT_TOPICS
### def save_topics():
def save_topics(topics):
    try:
        with open(TOPICS_FILE, 'w', encoding='utf-8') as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving topics: {e}")
        return False
### def get_next_topic():
def get_next_topic():
    topics = load_topics()
    unused = [t for t in topics if not t.get('used', False)]
    
    if unused:
        return unused[0]
    
    all_topics = sorted(topics, key=lambda x: x.get('last_used', ''))
    return all_topics[0] if all_topics else None
### def mark_topic_used():
def mark_topic_used(topic_id):
    topics = load_topics()
    today = datetime.now().strftime("%Y-%m-%d")
    
    for topic in topics:
        if topic['id'] == topic_id:
            topic['used'] = True
            topic['last_used'] = today
            break
    
    save_topics(topics)
    return True
### def add_new_topic():
def add_new_topic(topic_title, topic_id=None):
    topics = load_topics()
    
    if topic_id is None:
        topic_id = topic_title.lower().replace(' ', '_').replace('-', '_')
    
    new_topic = {
        "id": topic_id,
        "title": topic_title,
        "used": False,
        "last_used": None
    }
    
    topics.append(new_topic)
    save_topics(topics)
    return new_topic
### def main():
def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python topic_manager.py [command] [args]")
        print("Commands:")
        print("  next - get next topic")
        print("  list - list all topics")
        print("  mark [id] - mark topic as used")
        print("  add [title] - add new topic")
        print("  stats - show statistics")
        return
    
    command = sys.argv[1]
    
    if command == "next":
        topic = get_next_topic()
        if topic:
            print(f"Next topic: {topic['title']} (ID: {topic['id']})")
        else:
            print("No topics available")
    
    elif command == "list":
        topics = load_topics()
        print(f"Total topics: {len(topics)}")
        for i, topic in enumerate(topics):
            status = "USED" if topic.get('used', False) else "NEW"
            last_used = topic.get('last_used', 'never')
            print(f"{i+1}. {topic['title']} [{status}] - last: {last_used}")
    
    elif command == "mark" and len(sys.argv) >= 3:
        topic_id = sys.argv[2]
        if mark_topic_used(topic_id):
            print(f"Topic '{topic_id}' marked as used")
        else:
            print(f"Failed to mark topic '{topic_id}'")
    
    elif command == "add" and len(sys.argv) >= 3:
        title = ' '.join(sys.argv[2:])
        new_topic = add_new_topic(title)
        print(f"Added new topic: {new_topic['title']} (ID: {new_topic['id']})")
    
    elif command == "stats":
        topics = load_topics()
        total = len(topics)
        used = sum(1 for t in topics if t.get('used', False))
        remaining = total - used
        percentage = (used / total * 100) if total > 0 else 0
        
        print(f"📊 Topic Statistics:")
        print(f"   Total topics: {total}")
        print(f"   Used topics: {used}")
        print(f"   Remaining topics: {remaining}")
        print(f"   Progress: {percentage:.1f}%")
        
        if used > 0:
            used_topics = [t for t in topics if t.get('used', False)]
            latest = max(used_topics, key=lambda t: t.get('last_used', ''))
            print(f"   Latest used: {latest['title']} ({latest.get('last_used', 'unknown')})")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
