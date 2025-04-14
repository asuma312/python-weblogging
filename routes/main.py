import os
from models import EmailToContact
from flask import *
from utils.decorators import frontend_login
from utils.path import get_user_path
from models.dataclasses.logtypes import LOGTYPES
from datetime import datetime, timedelta
from models.sql.setup import setup_database

main_bp = Blueprint('main', __name__, url_prefix='/')

@main_bp.route('/')
def index():
    return render_template('landing/index.html')

@main_bp.route("/register")
def register():
    return render_template("landing/register.html")

@main_bp.route("/login")
def login():
    return render_template("landing/login.html")

@main_bp.route("/dashboard")
@frontend_login
def dashboard():
    user = g.user
    user_path = get_user_path(user)

    database_logs = [
        db.split("log_")[-1].split(".sqlite")[0]
        for db in os.listdir(user_path) if db.endswith('.sqlite')
    ]
    total_log = 0
    total_errors = 0
    total_warnings = 0
    error_types = [
        LOGTYPES.ERROR.value.upper(),
        LOGTYPES.CRITICAL.value.upper(),
        LOGTYPES.FAILURE.value.upper()
    ]


    args = request.args
    selected_log = args.get("log", 'all')
    page = args.get("page",0)

    limit = int(current_app.config['FRONTEND_LOGS_PER_PAGE'])
    offset = int(page) * limit


    log_types =  args.get("types", 'all').split(",")
    LOGTYPES_VAL = [log.value for log in LOGTYPES]
    print(log_types)

    if any(log not in LOGTYPES_VAL for log in log_types):
        return jsonify({'status':'error','message':'log type is invalid'}),400
    if log_types == []:
        log_types = [LOGTYPES.ALL]


    function_name = args.get("function_name")
    if function_name:
        if not isinstance(function_name, str):
            return jsonify({'status':'error','message':'function_name must be a string'}),400

    data_start = args.get("data_start")
    if data_start:
        try:
            data_start = datetime.strptime(data_start, '%Y-%m-%d %H:%M')
        except ValueError:
            return jsonify({'status':'error','message':'data_start must be a datetime'}),400

    data_end = args.get("data_end")
    if data_end:
        try:
            data_end = datetime.strptime(data_end, '%Y-%m-%d %H:%M')
        except ValueError:
            return jsonify({'status':'error','message':'data_end must be a datetime'}),400

    query = """
    SELECT id, data, type, function, message
    FROM logs
    WHERE 1=1 {and_where_clausules}
    ORDER BY id DESC
    LIMIT ?
    OFFSET ?
    """

    params = []
    and_clausules = ""

    database_to_read = database_logs
    if selected_log != 'all':
        database_to_read = [
            db for db in database_logs if db == selected_log
        ]
    rows_per_db = int(limit/len(database_to_read) if len(database_to_read) > 0 else limit)
    rows_per_db = rows_per_db if rows_per_db > 0 else 1

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
        and_clausule = " AND data >= ?"
        and_clausules += and_clausule
        params.append(data_start)

    if data_end:
        and_clausule = " AND data <= ?"
        and_clausules += and_clausule
        params.append(data_end)

    formated_query = query.format(and_where_clausules=and_clausules)
    params.extend([rows_per_db, offset])
    logs = {}

    for db in database_to_read:
        conn = setup_database(user,db)
        cursor = conn.cursor()
        cursor.execute(formated_query, params)
        rows = [row for row in cursor.fetchall()]

        count_logs_query = formated_query
        count_logs_params = params.copy()[:-2]
        count_logs_query = count_logs_query.replace("LIMIT ?", "LIMIT 1")
        count_logs_query = count_logs_query.replace("OFFSET ?", "OFFSET 0")
        count_logs_query = count_logs_query.replace("SELECT id, data, type, function, message", "SELECT id")
        count_logs = cursor.execute(count_logs_query, count_logs_params).fetchone()
        if not count_logs:
            count_logs = 0
        else:
            count_logs = count_logs[0]
        total_log += count_logs




        error_placeholders = ','.join(['?'] * len(error_types))
        errors_query = """SELECT COUNT(type) as qtd_erros FROM logs WHERE type IN ({placeholders}) and data >= ? and data <= ?"""
        errors_query = errors_query.format(placeholders=error_placeholders)
        errors_params = error_types

        error_data_end = datetime.now()
        error_data_start = error_data_end - timedelta(days=1)

        errors_params.extend([error_data_start, error_data_end])
        errors = cursor.execute(errors_query, errors_params)
        errors = errors.fetchone()[0]
        total_errors += errors


        warnings_query = """SELECT COUNT(type) as qtd_warnings FROM logs WHERE type = ? and data >= ? and data <= ?"""
        warnings_query = warnings_query.format(placeholders=error_placeholders)
        warnings_params = [LOGTYPES.WARNING.value.upper()]
        warnings_params.extend([error_data_start, error_data_end])
        warnings = cursor.execute(warnings_query, warnings_params)
        warnings = warnings.fetchone()[0]
        total_warnings += warnings

        logs[db] = rows


        cursor.close()
        conn.close()

    total_pages = int(total_log / limit)

    has_next_page = int(page) < total_pages
    return render_template('main/dashboard.html',
                           database_logs=database_logs,
                           logs=logs,
                           selected_log=selected_log,
                           total_log=total_log,
                           total_errors=total_errors,
                           total_warnings=total_warnings,
                           has_next_page=has_next_page,
                           )

@main_bp.route("/logout")
@frontend_login
def logout():
    session.clear()
    return redirect(url_for('main.login'))


@main_bp.route("/settings")
@frontend_login
def settings():
    user = g.user
    user_path = get_user_path(user)
    user_emails = EmailToContact.query.filter_by(userhash=user.userhash).all()
    database_logs = [
        db.split("log_")[-1].split(".sqlite")[0]
        for db in os.listdir(user_path) if db.endswith('.sqlite')
    ]
    return render_template('main/settings.html',database_logs=database_logs,emails=user_emails)

@main_bp.route("/api-docs")
def api_docs():
    return render_template('swagger.html', specs_url='/apispec_1.json')
