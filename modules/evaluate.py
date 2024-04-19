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
    sql = "select * from evaluate where 1=1"
    start = request.args.get('start')
    if username:
        sql = sql + f" and username='{username}'"
    if start:
        end = request.args.get('end')
        end = (datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        sql = sql + f" and time>='{start}' and time<='{end}'"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    if df.empty:
        return jsonify(code=404, msg='error')
    df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records'))


def stats_row(row):
    sql = f"select category,username from evaluate_stats where evaluateId='{row['id']}'"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    if not df.empty:
        category_counts = df['category'].value_counts()
        for category, count in category_counts.iteritems():
            row[category] = count
    sql = f"select count(*) count from evaluate_report where evaluateId='{row['id']}'"
    df = con.get_mssql_data(sql)
    row['report'] = df.iloc[0]['count']
    return row


@evaluate.route('/player/comment/search', methods=['get'])
def plater_comment_search():
    gameId = request.args.get('gameId')
    name = request.args.get('player').replace('\'', '\'\'')
    sql = f"select * from evaluate where gameId='{gameId}' and name='{name}'"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    df['like'] = 0
    df['dislike'] = 0
    df = df.apply(stats_row, axis=1)
    if not df.empty:
        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records'))
