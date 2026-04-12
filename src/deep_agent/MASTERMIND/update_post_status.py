# UPDATE POST STATUS
## imports
import json
import sys
from datetime import datetime

## variables
POSTS_FILE = "posts/scheduled_posts.json"

## functions
### def update_post_status(post_id, status="published"):
def update_post_status(post_id, status="published"):
    try:
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = False
        for post in data["posts"]:
            if post["id"] == post_id:
                post["status"] = status
                if status == "published" and post["published_at"] is None:
                    post["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated = True
                break
        
        if updated:
            with open(POSTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return f"Updated {post_id} to {status}"
        else:
            return f"Post {post_id} not found"
    
    except Exception as e:
        return f"Error: {str(e)}"

### def main():
def main():
    if len(sys.argv) < 2:
        print("Usage: python update_post_status.py <post_id> [status]")
        return
    
    post_id = sys.argv[1]
    status = sys.argv[2] if len(sys.argv) > 2 else "published"
    
    result = update_post_status(post_id, status)
    print(result)

if __name__ == "__main__":
    main()