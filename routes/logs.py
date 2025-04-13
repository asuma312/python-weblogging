from flask import *
from utils.log_utils import insert_log
from utils.path import get_user_path
from datetime import datetime
from models.dataclasses.logtypes import LOGTYPES
from utils.decorators import verify_token
from models.sql.setup import setup_database
import os

logs_bp = Blueprint('logs', __name__)



@logs_bp.route('/insert_log',methods=['PUT'])
@verify_token()
def insert_log_to_backend():
    """
    Insert a log.
    ---
    tags:
      - logs
    parameters:
      - name: body
        in: body
        required: true
        description: "The logstring needs to be in this specific pattern (date time - type [parent:parent - function name] - message), its better to use the SDK client for this"
        schema:
          type: object
          properties:
            log:
              type: string
    description: Inserts a log into the backend.
    responses:
      200:
        description: Returns the inserted log ID
        schema:
          type: object
          properties:
            status:
              type: string
            log_id:
              type: integer
            data_inserted:
              type: string
      400:
        description: Validation error
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
    """
    user = g.user
    data = request.get_json()
    log = data.get('log')
    if not log:
        return jsonify({'status':'error','message':'log is required'}),400
    log_name = data.get("log_name", 'default')
    log_id = insert_log(log,user,log_name)
    return jsonify({'status':'success','log_id':log_id,'data_inserted':log}),200

@logs_bp.route("/insert_multiple_logs",methods=['PUT'])
@verify_token()
def insert_multiple_logs():
    """
    Insert multiple logs.
    ---
    tags:
      - logs
    parameters:
      - name: body
        in: body
        required: true
        description: "Body containing a list of logs"
        schema:
          type: object
          properties:
            logs:
              type: array
              items:
                type: string
    description: Inserts a list of logs into the backend.
    responses:
      200:
        description: List of inserted logs
        schema:
          type: object
          properties:
            status:
              type: string
            inserted:
              type: array
              items:
                type: object
      400:
        description: Validation error
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
    """
    user = g.user
    data = request.get_json()
    logs:list = data.get('logs')
    log_name:str = data.get('log_name')
    if not logs:
        return jsonify({'status':'error','message':'logs is required'}),400
    if not isinstance(logs, list):
        return jsonify({'status':'error','message':'logs must be a list'}),400
    from utils.log_utils import insert_multiple_logs as insert_multi
    inserted_data = insert_multi(logs, user, log_name)
    return jsonify({'status':'success','inserted':inserted_data}),200


@logs_bp.route('/select_logs',methods=['POST'])
@verify_token()
def select_logs():
    """
    Select logs.
    ---
    tags:
      - logs
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            page:
              type: integer
            limit:
              type: integer
            types:
              type: array
              items:
                type: string
            function_name:
              type: string
            data_start:
              type: string
            data_end:
              type: string
    description: Filters and paginates logs.
    responses:
      200:
        description: Returns the log list
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: array
              items:
                type: object
      400:
        description: Validation error
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
    """
    user = g.user
    data = request.get_json()

    log_name = data.get("log_name", 'default')

    page = data.get("page")
    if not page:
        return jsonify({'status':'error','message':'page is required'}),400
    if not str(page).isdigit():
        return jsonify({'status':'error','message':'page must be a number'}),400
    if int(page) < 1:
        return jsonify({'status':'error','message':'page must be greater than 0'}),400
    page = int(page)

    limit = data.get("limit",int(os.getenv('BASE_SELECT_LOGS')))
    if not str(limit).isdigit():
        return jsonify({'status':'error','message':'limit must be a number'}),400

    if limit > int(os.getenv('LIMIT_SELECT_LOGS')):
        limit = int(os.getenv('LIMIT_SELECT_LOGS'))
    if limit < 1:
        limit = 1

    offset = (page - 1) * limit
    if offset < 0:
        offset = 0
    max_offset = offset + limit

    log_types =  data.get("types", [])
    LOGTYPES_VAL = [log.value for log in LOGTYPES]

    if any(log not in LOGTYPES_VAL for log in log_types):
        return jsonify({'status':'error','message':'log type is invalid'}),400
    if log_types == []:
        log_types = [LOGTYPES.ALL]


    function_name = data.get("function_name")
    if function_name:
        if not isinstance(function_name, str):
            return jsonify({'status':'error','message':'function_name must be a string'}),400

    data_start = data.get("data_start")
    if data_start:
        try:
            data_start = datetime.strptime(data_start, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({'status':'error','message':'data_start must be a datetime'}),400

    data_end = data.get("data_end")
    if data_end:
        try:
            data_end = datetime.strptime(data_end, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({'status':'error','message':'data_end must be a datetime'}),400
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
        if len(log_types) == 0:
            pass
        elif len(log_types) == 1:
            and_clausule = " AND type = ?"
            and_clausules += and_clausule
            params.append(log_types[0].upper())
        elif len(log_types) > 1:
            and_clausule = " AND TYPE = ?"
            and_clausules += and_clausule
            params.append(log_types[0].upper())
            for _type in log_types[1:]:
                and_clausule = " OR type = ?"
                and_clausules += and_clausule
                params.append(_type.upper())

    if function_name:
        and_clausule = " AND function = ?"
        and_clausules += and_clausule
        params.append(function_name)

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
        return jsonify({'status':'success','data':[]}),200
    columns = ["id", "data", "type", "function", "message"]

    logs = [dict(zip(columns, row)) for row in rows]

    return jsonify({'status':'success','data':logs}),200

@logs_bp.route("/get_log")
@verify_token()
def get_specific_log():
    """
    Get a specific log.
    ---
    tags:
      - logs
    parameters:
      - name: log_id
        in: query
        required: true
        description: "ID of the log to be retrieved"
        schema:
          type: integer
    description: Returns a log by the provided ID.
    responses:
      200:
        description: Log found
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: object
      400:
        description: Validation error
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      404:
        description: Log not found
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
            data:
              type: object
    """
    user = g.user
    args = request.args
    log_id = args.get("log_id")
    if not log_id:
        return jsonify({"status": "error", "message": "log_id is required"}), 400
    if not str(log_id).isdigit():
        return jsonify({"status": "error", "message": "log_id must be a number"}), 400
    log_id = int(log_id)
    if log_id < 1:
        return jsonify({"status": "error", "message": "log_id must be greater than 0"}), 400
    conn = setup_database(user)
    cur = conn.cursor()
    query = """
    SELECT * FROM logs
    WHERE id = ?
    """
    response = cur.execute(query.format(log_id=log_id), (log_id,))

    rows = response.fetchall()
    cur.close()
    conn.close()
    if not rows:
        return jsonify({"status": "error", "message": "log not found", "data":{}}), 404
    columns = ["id", "data", "type", "function", "message"]
    json = [dict(zip(columns, row)) for row in rows]
    return jsonify({"status": "success", "data": json[0]}), 200

