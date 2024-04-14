import json
from datetime import datetime, timedelta

import pandas as pd
from flask import Blueprint, jsonify, request

from lib.db import UseMySQL

evaluate = Blueprint('evaluate', __name__)


@evaluate.route('/submit', methods=['post'])
def submit():
    val = json.loads(request.get_data())
    df = pd.DataFrame(val, index=[0])
    con = UseMySQL()
    con.write_table('evaluate', df)
    return jsonify(code=200, msg='success')


@evaluate.route('/search', methods=['get'])
def search():
    username = request.args.get('username')
    sql = f"select * from evaluate where username='{username}'"
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
    return jsonify(code=200, msg='success',data=df.fillna('').to_dict('records'))
