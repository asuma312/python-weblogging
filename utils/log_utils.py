import re
from models.sql.setup import setup_database
from models.sql.user import User
from flask import current_app


def parse_log(log:str):
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) \[(.+?)\] - (.+)'
    match = re.match(pattern, log)
    if match:
        if match:
            return match.groups()
    else:
        raise ValueError(f"Formato de log inválido: {log}")

def insert_log(log: str, user: User, log_name:str='default'):
    date_str, log_type, function, message = parse_log(log)
    function = function.split(" - ")[-1].strip()
    conn = setup_database(user, log_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (data, type, function, message) VALUES (?, ?, ?, ?)",
                   (date_str, log_type, function, message))
    if log_type in ['ERROR']:
        socket_ioobj = current_app.config['socketio']
        socket_ioobj.notify_user(user.userhash, message, date_str, log_name, 'red')
        print("sent message")
    conn.commit()
    cursor.close()
    conn.close()
    return 1


def insert_multiple_logs(logs: list[str], user: User, log_name:str='default'):
    conn = setup_database(user, log_name)
    cursor = conn.cursor()
    cursor.execute('BEGIN TRANSACTION')
    inserted_items = []
    for log in logs:
        date_str, log_type, function, message = parse_log(log)
        function = function.split(" - ")[-1].strip()
        cursor.execute("INSERT INTO logs (data, type, function, message) VALUES (?, ?, ?, ?)",
                       (date_str, log_type, function, message))
        inserted_items.append({
            'log_id': cursor.lastrowid,
            'data_inserted': log
        })
    cursor.execute('END TRANSACTION')
    conn.commit()
    cursor.close()
    conn.close()
    return inserted_items
