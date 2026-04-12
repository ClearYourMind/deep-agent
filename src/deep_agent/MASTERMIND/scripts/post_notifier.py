#!/usr/bin/env python3
"""
Telegram Post Notifier - Вариант B (уведомления)
Мониторит расписание и создаёт уведомления о постах, которые нужно опубликовать
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path

# --- конфигурация ---
SCHEDULE_FILE = "posts/scheduled_posts.json"
NOTIFICATION_FILE = "posts/pending_notifications.txt"
CHECK_INTERVAL = 60  # секунды

class PostNotifier:
    def __init__(self):
        self.schedule_file = SCHEDULE_FILE
        self.notification_file = NOTIFICATION_FILE
        
        # Создаём файл уведомлений, если его нет
        Path(self.notification_file).parent.mkdir(parents=True, exist_ok=True)
    
    def load_schedule(self):
        """Загружает расписание из JSON файла"""
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Ошибка: файл расписания не найден: {self.schedule_file}")
            return None
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            return None
    
    def save_schedule(self, schedule):
        """Сохраняет обновлённое расписание"""
        try:
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(schedule, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения расписания: {e}")
            return False
    
    def add_notification(self, post_id, post_title, post_text):
        """Добавляет уведомление о посте"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        notification = f"""
{'='*60}
УВЕДОМЛЕНИЕ О ПОСТЕ
Время: {timestamp}
ID поста: {post_id}
Название: {post_title}

Текст для публикации:
{post_text}

Действие: Скопируйте текст выше и опубликуйте в Telegram группе
{'='*60}

"""
        
        try:
            with open(self.notification_file, 'a', encoding='utf-8') as f:
                f.write(notification)
            print(f"✅ Создано уведомление для поста: {post_id} ({post_title})")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания уведомления: {e}")
            return False
    
    def load_post_text(self, filename):
        """Загружает текст поста из файла"""
        post_path = os.path.join("posts", filename)
        try:
            with open(post_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Файл поста не найден: {post_path}")
            return None
    
    def archive_post(self, post_id, post_text, filename):
        """Архивирует опубликованный пост"""
        archive_dir = "posts/archive"
        os.makedirs(archive_dir, exist_ok=True)
        
        archive_file = os.path.join(archive_dir, f"{post_id}_published.txt")
        try:
            with open(archive_file, 'w', encoding='utf-8') as f:
                f.write(post_text)
            return archive_file
        except Exception as e:
            print(f"⚠️ Ошибка архивации поста {post_id}: {e}")
            return None
    
    def check_schedule(self):
        """Проверяет расписание и обрабатывает посты для публикации"""
        schedule = self.load_schedule()
        if not schedule:
            return False
        
        current_time = datetime.now()
        updated = False
        
        for post in schedule["posts"]:
            if post["status"] != "scheduled":
                continue
            
            scheduled_time = datetime.strptime(
                post["scheduled_time"], 
                "%Y-%m-%d %H:%M:%S"
            )
            
            if current_time >= scheduled_time:
                print(f"⏰ Время публиковать пост: {post['id']} ({post['title']})")
                
                # Загружаем текст поста
                post_text = self.load_post_text(post["filename"])
                if not post_text:
                    continue
                
                # Создаём уведомление
                if self.add_notification(post["id"], post["title"], post_text):
                    # Обновляем статус поста
                    post["status"] = "pending_notification"
                    post["notified_at"] = current_time.isoformat()
                    updated = True
                    
                    # Архивируем пост
                    archive_file = self.archive_post(
                        post["id"], 
                        post_text, 
                        post["filename"]
                    )
                    if archive_file:
                        post["archive_file"] = archive_file
        
        if updated:
            self.save_schedule(schedule)
        
        return updated
    
    def run(self):
        print("="*60)
        print("Telegram Post Notifier запущен")
        print(f"Режим: Уведомления (Вариант B)")
        print(f"Файл расписания: {self.schedule_file}")
        print(f"Файл уведомлений: {self.notification_file}")
        print(f"Интервал проверки: {CHECK_INTERVAL} секунд")
        print("="*60)
        print()
        
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Проверка расписания...")
            
            self.check_schedule()
            
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")

def main():
    """Точка входа"""
    notifier = PostNotifier()
    
    # Проверяем существование файла расписания
    if not os.path.exists(SCHEDULE_FILE):
        print(f"❌ Файл расписания не найден: {SCHEDULE_FILE}")
        print("Создайте файл расписания или проверьте путь.")
        return
    
    # Запускаем монитор
    notifier.run()

if __name__ == "__main__":
    main()