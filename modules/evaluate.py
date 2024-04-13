import json

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
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    if df.empty:
        return jsonify(code=404, msg='error')
    return jsonify(code=200, msg='success',data=df.fillna('').to_dict('records'))
