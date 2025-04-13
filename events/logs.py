from flask import current_app
from flask_socketio import emit
from utils.log_utils import insert_log
from utils.path import get_user_path
from datetime import datetime
from models.dataclasses.logtypes import LOGTYPES
from models.sql.setup import setup_database
from utils.decorators import authenticated_only
import os

def register_logs_events(socketio):
    
    @socketio.on('insert_log')
    @authenticated_only
    def handle_insert_log(data):
        user = data.get('user')
        log = data.get('log')
        log_name = data.get("log_name", 'default')
        
        if not log:
            return emit('insert_log_response', {'status': 'error', 'message': 'log is required'})
        
        try:
            log_id = insert_log(log, user, log_name)
        except Exception as e:
            return emit('insert_log_response', {'status': 'error', 'message': 'log is invalid', 'error': str(e)})
        emit('insert_log_response', {'status': 'success', 'log_id': log_id, 'data_inserted': log})
    
    @socketio.on('insert_multiple_logs')
    @authenticated_only
    def handle_insert_multiple_logs(data):
        user = data.get('user')
        logs = data.get('logs')
        log_name = data.get("log_name", 'default')
        
        if not logs:
            return emit('insert_multiple_logs_response', {'status': 'error', 'message': 'logs is required'})
        
        if not isinstance(logs, list):
            return emit('insert_multiple_logs_response', {'status': 'error', 'message': 'logs must be a list'})
        
        log_ids = []
        for log in logs:
            log_id = insert_log(log, user, log_name)
            log_ids.append(log_id)
            
        emit('insert_multiple_logs_response', {'status': 'success', 'log_ids': log_ids})
    
    @socketio.on('select_logs')
    @authenticated_only
    def handle_select_logs(data):
        user = data.get('user')
        
        page = data.get("page")
        log_name = data.get("log_name", 'default')
        if not page:
            return emit('select_logs_response', {'status': 'error', 'message': 'page is required'})
        if not str(page).isdigit():
            return emit('select_logs_response', {'status': 'error', 'message': 'page must be a number'})
        if int(page) < 1:
            return emit('select_logs_response', {'status': 'error', 'message': 'page must be greater than 0'})
        page = int(page)

        limit = int(data.get("limit", int(os.getenv('BASE_SELECT_LOGS'))))
        if not str(limit).isdigit():
            return emit('select_logs_response', {'status': 'error', 'message': 'limit must be a number'})

        if limit > int(os.getenv('LIMIT_SELECT_LOGS')):
            limit = int(os.getenv('LIMIT_SELECT_LOGS'))
        if limit < 1:
            limit = 1

        offset = (page - 1) * limit
        if offset < 0:
            offset = 0
        max_offset = offset + limit

        log_types = data.get("types", [])
        LOGTYPES_VAL = [log.value for log in LOGTYPES]

        if any(log not in LOGTYPES_VAL for log in log_types):
            return emit('select_logs_response', {'status': 'error', 'message': 'log type is invalid'})
        if log_types == []:
            log_types = [LOGTYPES.ALL]

        function_name = data.get("function_name")
        if function_name:
            if not isinstance(function_name, str):
                return emit('select_logs_response', {'status': 'error', 'message': 'function_name must be a string'})

        data_start = data.get("data_start")
        if data_start:
            try:
                data_start = datetime.strptime(data_start, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return emit('select_logs_response', {'status': 'error', 'message': 'data_start must be a datetime'})

        data_end = data.get("data_end")
        if data_end:
            try:
                data_end = datetime.strptime(data_end, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return emit('select_logs_response', {'status': 'error', 'message': 'data_end must be a datetime'})

        conn = setup_database(user, log_name)
        cur = conn.cursor()

        query = """
        SELECT * FROM logs
        WHERE 1>0{and_where_clausules}
        ORDER BY id ASC
        LIMIT ? 
        OFFSET ?
        """
        and_clausules = ''
        params = []
        if LOGTYPES.ALL not in log_types:
            if len(log_types) == 0 or 'all' in log_types:
                pass
            elif len(log_types) == 1:
                and_clausule = " AND type = ?"
                and_clausules += and_clausule
                params.append(log_types[0].upper())
            elif len(log_types) > 1:
                and_clausule = " AND (type = ?"
                and_clausules += and_clausule
                params.append(log_types[0].upper())
                for _type in log_types[1:]:
                    and_clausule = " OR type = ?"
                    and_clausules += and_clausule
                    params.append(_type.upper())
                and_clausules += ")"

        if function_name:
            and_clausule = " AND function LIKE ?"
            and_clausules += and_clausule
            params.append(f"%{function_name}%")

        if data_start:
            and_clausule = " AND date >= ?"
            and_clausules += and_clausule
            params.append(data_start)

        if data_end:
            and_clausule = " AND date <= ?"
            and_clausules += and_clausule
            params.append(data_end)
            
        formated_query = query.format(and_where_clausules=and_clausules)
        params.extend([limit, offset])
        response = cur.execute(formated_query, params)
        rows = response.fetchall()
        cur.close()
        conn.close()
        
        if rows == []:
            return emit('select_logs_response', {'status': 'success', 'data': []})
            
        columns = ["id", "data", "type", "function", "message"]
        logs = [dict(zip(columns, row)) for row in rows]

        emit('select_logs_response', {'status': 'success', 'data': logs})
    
    @socketio.on('get_log')
    @authenticated_only
    def handle_get_log(data):
        user = data.get('user')
        log_id = data.get("log_id")
        
        if not log_id:
            return emit('get_log_response', {"status": "error", "message": "log_id is required"})
            
        if not str(log_id).isdigit():
            return emit('get_log_response', {"status": "error", "message": "log_id must be a number"})
            
        log_id = int(log_id)
        if log_id < 1:
            return emit('get_log_response', {"status": "error", "message": "log_id must be greater than 0"})
            
        conn = setup_database(user)
        cur = conn.cursor()
        query = """
        SELECT * FROM logs
        WHERE id = ?
        """
        response = cur.execute(query, (log_id,))

        rows = response.fetchall()
        cur.close()
        conn.close()
        
        if not rows:
            return emit('get_log_response', {"status": "error", "message": "log not found", "data": {}})
            
        columns = ["id", "data", "type", "function", "message"]
        log_data = dict(zip(columns, rows[0]))
        
        emit('get_log_response', {"status": "success", "data": log_data})
