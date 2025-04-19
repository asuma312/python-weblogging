from flask_socketio import emit, join_room
import os
import sqlite3
from flask import current_app
from datetime import datetime,timedelta
from utils.resend_wrapper import send_email
import time
#pega o parent directory do arquivo atual
cache_root:str = current_app.config['CACHE_PATH']
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
        with socketio.app.app_context():
            from models.sql import EmailToContact
            emails:list[EmailToContact] = EmailToContact.query.filter_by(userhash=uh).all()
            message_html = """
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Notificação PyWebLog</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333333;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                    <div style="background-color: #0056b3; padding: 20px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">Notificação PyWebLog</h1>
                    </div>

                    <div style="padding: 20px;">
                        <div style="background-color: #f9f9f9; border-left: 4px solid {{'#e74c3c' if priority == 'red' else '#f39c12' if priority == 'yellow' else '#2ecc71'}}; padding: 15px; margin-bottom: 20px;">
                            <p style="font-size: 16px; line-height: 1.5; margin: 0;">{message}</p>
                        </div>

                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold; width: 30%;">Prioridade:</td>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;">
                                    <span style="display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; text-transform: uppercase; background-color: {{'#e74c3c' if priority == 'red' else '#f39c12' if priority == 'yellow' else '#2ecc71'}}; color: white;">
                                        {priority}
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Data:</td>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;">{created_at}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Log:</td>
                                <td style="padding: 8px; border-bottom: 1px solid #eee;">{log_name}</td>
                            </tr>
                        </table>
                                                                    <h1 style="color: white; margin: 0; font-size: 24px;text-align: center;">
                                            <button style="background-color: #0056b3; color: white; border: none; padding: 10px 20px; font-size: 16px; cursor: pointer; border-radius: 5px;">
                                            <a href="https://pythonweblog.com/dashboard" style="color: white; text-decoration: none;">Acesse o PyWebLog</a>
                                            </button>
                                            </h1>
                    </div>

                    <div style="background-color: #0056b3; padding: 20px; text-align: center;">
                        <p>Esta é uma mensagem automática do sistema PyWebLog. Por favor, não responda a este e-mail.</p>
                    </div>


                </div>
            </body>
            </html>
            """
            for email in emails:
                print("sending email to", email.email)
                send_email(email.email, 'Notificação PyWebLog', message_html.format(message=message, priority=priority, created_at=created_at, log_name=log_name))
    socketio.notify_user = notify_user

