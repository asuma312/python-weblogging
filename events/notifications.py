from flask_socketio import emit, join_room
import os
import sqlite3
from datetime import datetime,timedelta
import time
#pega o parent directory do arquivo atual
cache_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cache')
os.makedirs(cache_root, exist_ok=True)


import json
def register_notification_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        emit('user_id', {'uh': 'please join room'})  # informa que o cliente deve emitir join_room

    @socketio.on('join_room')
    def handle_join_room(data):
        uh = data.get('uh')
        if uh:
            join_room(uh)
            cache_user_path = os.path.join(cache_root, uh)
            os.makedirs(cache_user_path, exist_ok=True)
            cache_db_path = os.path.join(cache_user_path, 'cache.sqlite3')
            with sqlite3.connect(cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT,
                        priority TEXT,
                        read BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                two_days_ago = datetime.now() - timedelta(days=2)
                two_days_ago_str = two_days_ago.strftime('%Y-%m-%d %H:%M:%S')

                data = cursor.execute('''
                    SELECT * FROM notifications
                    WHERE created_at >= ?
                    ORDER BY
                        read ASC,
                        CASE priority
                            WHEN 'red' THEN 1
                            WHEN 'yellow' THEN 2
                            WHEN 'green' THEN 3
                            ELSE 4
                        END,
                        created_at DESC
                    LIMIT 50
                ''', (two_days_ago_str,)).fetchall()
                for row in data:
                    id = row[0]
                    message = row[1]
                    priority = row[2]
                    read = row[3]
                    date = row[4]
                    if read:
                        emit('silent_notification', {'message': message, 'priority': 'grey', "date": date, "read": read}, broadcast=True)
                    else:
                        emit('notification_response', {'message': message,'priority': priority,  "date": date, 'id': id, "read": read}, broadcast=True)
            print(f"User joined room: {uh}")
        else:
            print("No userhash provided for room join.")

    @socketio.on('read_messages')
    def read_messages(data:dict):
        user_hash = data.get('uh')
        messages_id = data.get('messages')
        cache_user_path = os.path.join(cache_root, user_hash)
        cache_db_path = os.path.join(cache_user_path, 'cache.sqlite3')
        with sqlite3.connect(cache_db_path) as conn:
            cursor = conn.cursor()
            for message_id in messages_id:
                print(f"Marking message {message_id} as read")
                cursor.execute('UPDATE notifications SET read = 1 WHERE id = ?', (message_id,))
            conn.commit()

    @socketio.on('notification')
    def handle_notification(data):
        message = data.get('message')
        emit('notification_response', {'message': f'Notificação recebida: {message}'}, broadcast=True)

    def notify_user(uh, message, priority='green'):
        print(f"Notificando usuário {uh} com a mensagem: {message}")
        cache_user_path = os.path.join(cache_root, uh)
        os.makedirs(cache_user_path, exist_ok=True)
        cache_db_path = os.path.join(cache_user_path, 'cache.sqlite3')

        conn = sqlite3.connect(cache_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                priority TEXT,
                read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

        cursor.execute('''
            INSERT INTO notifications (message, priority)
            VALUES (?, ?)
        ''', (message, priority))

        id = cursor.lastrowid

        cursor.execute('''
            SELECT created_at, read FROM notifications WHERE id = ?
        ''', (id,))
        date, read = cursor.fetchone()

        conn.commit()
        conn.close()

        socketio.emit('notification_response',
                      {'message': message, 'priority': priority, "date": date, 'id': id, "read": read}, room=uh)
    socketio.notify_user = notify_user

