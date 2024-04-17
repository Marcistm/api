from datetime import timedelta, datetime

from flask import request, jsonify, Blueprint

from lib.db import UseMySQL

report = Blueprint('report', __name__)


@report.route('/search', methods=['get'])
def search():
    username = request.args.get('username')
    sql = f"select * from evaluate_report where username='{username}'"
    start = request.args.get('start')
    if start:
        end = request.args.get('end')
        end = (datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        sql = sql + f" and time>='{start}' and time<='{end}'"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    if df.empty:
        return jsonify(code=404, msg='error')
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records'))
