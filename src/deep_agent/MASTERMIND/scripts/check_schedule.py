#!/usr/bin/env python3
"""
Simple Schedule Checker - Проверяет расписание постов без блокирующих циклов
"""

import json
import os
from datetime import datetime
from pathlib import Path

SCHEDULE_FILE = "posts/scheduled_posts.json"
NOTIFICATION_FILE = "posts/pending_notifications.txt"

def check_schedule():
    """Проверяет расписание и создает уведомления для постов, которые пора публиковать"""
    print("🔍 Проверка расписания постов...")
    
    # Загружаем расписание
    try:
        with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
            schedule = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки расписания: {e}")
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
        
        # Проверяем, пора ли публиковать
        if current_time >= scheduled_time:
            print(f"⏰ Время публиковать пост: {post['id']} ({post['title']})")
            
            # Загружаем текст поста
            post_file = os.path.join("posts", post["filename"])
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    post_text = f.read()
            except Exception as e:
                print(f"❌ Ошибка загрузки текста поста: {e}")
                continue
            
            # Создаём уведомление
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notification = f"""
{'='*60}
УВЕДОМЛЕНИЕ О ПОСТЕ
Время: {timestamp}
ID поста: {post['id']}
Название: {post['title']}

Текст для публикации:
{post_text}

Действие: Скопируйте текст выше и опубликуйте в Telegram группе
{'='*60}

"""
            
            # Записываем уведомление
            try:
                with open(NOTIFICATION_FILE, 'a', encoding='utf-8') as f:
                    f.write(notification)
                print(f"✅ Уведомление создано в файле: {NOTIFICATION_FILE}")
            except Exception as e:
                print(f"❌ Ошибка записи уведомления: {e}")
                continue
            
            # Обновляем статус поста
            post["status"] = "pending_notification"
            post["notified_at"] = current_time.isoformat()
            updated = True
            
            # Архивируем пост
            archive_dir = "posts/archive"
            os.makedirs(archive_dir, exist_ok=True)
            archive_file = os.path.join(archive_dir, f"{post['id']}_published.txt")
            try:
                with open(archive_file, 'w', encoding='utf-8') as f:
                    f.write(post_text)
                post["archive_file"] = archive_file
                print(f"📁 Пост заархивирован: {archive_file}")
            except Exception as e:
                print(f"⚠️ Ошибка архивации: {e}")
    
    # Сохраняем обновленное расписание
    if updated:
        try:
            with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
                json.dump(schedule, f, indent=2, ensure_ascii=False)
            print("✅ Расписание обновлено")
        except Exception as e:
            print(f"❌ Ошибка сохранения расписания: {e}")
    
    return updated

def show_next_post():
    """Показывает следующий запланированный пост"""
    try:
        with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
            schedule = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки расписания: {e}")
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
    
    # Показываем время до публикации
    scheduled_time = datetime.strptime(next_post["scheduled_time"], "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()
    
    if scheduled_time > current_time:
        time_diff = scheduled_time - current_time
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        print(f"⏰ До публикации: {hours}ч {minutes}м")
    else:
        print("⚠️ Пост должен был быть опубликован уже!")

if __name__ == "__main__":
    print("📝 Simple Schedule Checker")
    print(f"Текущее время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Показываем следующий пост
    show_next_post()
    print()
    
    # Проверяем расписание
    if check_schedule():
        print("\n🎯 Проверка завершена: найдены посты для публикации")
    else:
        print("\n✅ Проверка завершена: пока ничего публиковать не нужно")