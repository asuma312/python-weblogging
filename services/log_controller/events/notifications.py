from flask_socketio import emit, join_room
import os
import sqlite3
from flask import current_app
from datetime import datetime,timedelta
import time
#pega o parent directory do arquivo atual
cache_root = current_app.config['CACHE_PATH']
os.makedirs(cache_root, exist_ok=True)

def setup_db(cache_db_path:str)->sqlite3.Connection:
    conn = sqlite3.connect(cache_db_path)
    cursor = conn.cursor()
    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS notifications (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            message TEXT,
                            priority TEXT,
                            log_name TEXT,
                            read BOOLEAN DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
    cursor.close()
    conn.commit()
    return conn


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
            two_days_ago = datetime.now() - timedelta(days=2)
            two_days_ago_str = two_days_ago.strftime('%Y-%m-%d %H:%M:%S')
            conn = setup_db(cache_db_path)
            cursor = conn.cursor()
            data = cursor.execute('''
                SELECT * FROM notifications
                WHERE created_at >= ?
                ORDER BY
                    read DESC,
                    CASE priority
                        WHEN 'red' THEN 1
                        WHEN 'yellow' THEN 2
                        WHEN 'green' THEN 3
                        ELSE 4
                    END,
                    created_at ASC
                LIMIT 50
            ''', (two_days_ago_str,)).fetchall()
            for row in data:
                id = row[0]
                message = row[1]
                priority = row[2]
                log_name = row[3]
                read = row[4]
                date = row[5]
                if read:
                    emit('silent_notification', {'message': message, 'priority': 'grey', "date": date, "read": read, "log_name":log_name}, broadcast=True)
                else:
                    emit('notification_response', {'message': message,'priority': priority,  "date": date, 'id': id, "read": read, "log_name":log_name}, broadcast=True)
            cursor.close()
            conn.close()
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


    def notify_user(uh, message,created_at, log_name, priority='green'):
        print(f"Notificando usuário {uh} com a mensagem: {message}")
        cache_user_path = os.path.join(cache_root, uh)
        os.makedirs(cache_user_path, exist_ok=True)
        cache_db_path = os.path.join(cache_user_path, 'cache.sqlite3')

        conn = setup_db(cache_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (message, priority, created_at, log_name)
            VALUES (?, ?, ?, ?)
        ''', (message, priority, created_at, log_name))
        conn.commit()
        id = cursor.lastrowid
        cursor.close()
        conn.close()
        socketio.emit('notification_response',
                      {'message': message, 'priority': priority, "date": created_at, 'id': id, "read": False, "log_name":log_name}, room=uh)
    socketio.notify_user = notify_user

