#!/usr/bin/env python3
"""
Post Manager - Утилита для управления постами и расписанием
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCHEDULE_FILE = "posts/scheduled_posts.json"

class PostManager:
    def __init__(self):
        self.schedule_file = SCHEDULE_FILE
    
    def load_schedule(self):
        """Загружает расписание"""
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки расписания: {e}")
            return None
    
    def save_schedule(self, schedule):
        """Сохраняет расписание"""
        try:
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(schedule, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False
    
    def list_posts(self):
        """Показывает список всех постов"""
        schedule = self.load_schedule()
        if not schedule:
            return
        
        print("\n" + "="*60)
        print("СПИСОК ПОСТОВ")
        print("="*60)
        
        for i, post in enumerate(schedule["posts"], 1):
            status_icon = "✅" if post["status"] == "published" else "⏳" if post["status"] == "scheduled" else "📝"
            print(f"{i}. {status_icon} {post['id']}: {post['title']}")
            print(f"   📅 {post['scheduled_time']} | Статус: {post['status']}")
            if post.get('published_at'):
                print(f"   🚀 Опубликован: {post['published_at']}")
            print()
    
    def add_post(self, post_id, title, filename, hours_from_now=6):
        """Добавляет новый пост в расписание"""
        schedule = self.load_schedule()
        if not schedule:
            return False
        
        # Рассчитываем время публикации
        scheduled_time = datetime.now() + timedelta(hours=hours_from_now)
        scheduled_str = scheduled_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Создаём новый пост
        new_post = {
            "id": post_id,
            "filename": filename,
            "title": title,
            "scheduled_time": scheduled_str,
            "status": "scheduled",
            "tags": [],
            "published_at": None,
            "archive_file": None
        }
        
        schedule["posts"].append(new_post)
        
        if self.save_schedule(schedule):
            print(f"✅ Пост добавлен: {post_id}")
            print(f"   📅 Запланирован на: {scheduled_str}")
            return True
        return False
    
    def update_post_time(self, post_id, new_time_str):
        """Обновляет время публикации поста"""
        schedule = self.load_schedule()
        if not schedule:
            return False
        
        for post in schedule["posts"]:
            if post["id"] == post_id:
                post["scheduled_time"] = new_time_str
                if post["status"] == "published":
                    post["status"] = "scheduled"
                    post["published_at"] = None
                print(f"✅ Время обновлено для {post_id}: {new_time_str}")
                return self.save_schedule(schedule)
        
        print(f"❌ Пост не найден: {post_id}")
        return False
    
    def mark_as_published(self, post_id):
        """Отмечает пост как опубликованный"""
        schedule = self.load_schedule()
        if not schedule:
            return False
        
        for post in schedule["posts"]:
            if post["id"] == post_id:
                post["status"] = "published"
                post["published_at"] = datetime.now().isoformat()
                print(f"✅ Пост отмечен как опубликованный: {post_id}")
                return self.save_schedule(schedule)
        
        print(f"❌ Пост не найден: {post_id}")
        return False
    
    def show_next_post(self):
        """Показывает следующий пост для публикации"""
        schedule = self.load_schedule()
        if not schedule:
            return
        
        scheduled_posts = [p for p in schedule["posts"] if p["status"] == "scheduled"]
        
        if not scheduled_posts:
            print("📭 Нет запланированных постов")
            return
        
        # Сортируем по времени
        scheduled_posts.sort(key=lambda x: x["scheduled_time"])
        next_post = scheduled_posts[0]
        
        print("\n" + "="*60)
        print("СЛЕДУЮЩИЙ ПОСТ ДЛЯ ПУБЛИКАЦИИ")
        print("="*60)
        print(f"ID: {next_post['id']}")
        print(f"Название: {next_post['title']}")
        print(f"Время публикации: {next_post['scheduled_time']}")
        print(f"Файл: {next_post['filename']}")
        print(f"Теги: {', '.join(next_post['tags'])}")
        
        # Показываем текст поста
        post_file = os.path.join("posts", next_post["filename"])
        if os.path.exists(post_file):
            print("\n" + "-"*40)
            print("ТЕКСТ ПОСТА:")
            print("-"*40)
            with open(post_file, 'r', encoding='utf-8') as f:
                print(f.read())
        else:
            print(f"\n⚠️ Файл поста не найден: {post_file}")

def print_help():
    """Показывает справку по командам"""
    print("\n" + "="*60)
    print("POST MANAGER - КОМАНДЫ")
    print("="*60)
    print("list                 - Показать все посты")
    print("next                 - Показать следующий пост")
    print("add <id> <title> <file> [hours] - Добавить пост")
    print("time <id> <YYYY-MM-DD HH:MM:SS> - Изменить время")
    print("publish <id>         - Отметить как опубликованный")
    print("help                 - Эта справка")
    print("exit                 - Выход")
    print("="*60)
    print("Примеры:")
    print("  add tech_001 'Новый пост' post.txt 4")
    print("  time mit_005 '2026-04-12 15:00:00'")
    print("  publish mit_004")

def main():
    manager = PostManager()
    
    print("📝 Post Manager - Управление расписанием постов")
    print_help()
    
    try:
        command = sys.argv[1:]
        
        if not command:
            continue
        
        cmd = command[0].lower()
        
        elif cmd == "help":
            print_help()
        
        elif cmd == "list":
            manager.list_posts()
        
        elif cmd == "next":
            manager.show_next_post()
        
        elif cmd == "add" and len(command) >= 4:
            post_id = command[1]
            title = " ".join(command[2:-1])
            filename = command[-1]
            hours = 6  # по умолчанию
            
            if len(command) > 4 and command[-2].isdigit():
                filename = command[-2]
                hours = int(command[-1])
            
            manager.add_post(post_id, title, filename, hours)
        
        elif cmd == "time" and len(command) >= 3:
            post_id = command[1]
            time_str = " ".join(command[2:])
            manager.update_post_time(post_id, time_str)
        
        elif cmd == "publish" and len(command) >= 2:
            post_id = command[1]
            manager.mark_as_published(post_id)
        
        else:
            print("❌ Неизвестная команда. Введите 'help' для справки.")
            
    except KeyboardInterrupt:
        print("\n👋 Выход...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()