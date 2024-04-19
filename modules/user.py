import json

import requests
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from nba_api.stats.endpoints import LeagueStandings

from config import proxy
from lib.db import UseMySQL
from utils.common import my_md5, generate_token

random_str = 'hytek20@0_solt~%!$#^&*'
user = Blueprint('user', __name__)


def stats_row(row):
    con = UseMySQL()
    sql = f"select id from evaluate where username='{row['username']}'"
    evaluateIds = con.get_mssql_data(sql)
    if evaluateIds.empty:
        return row
    ids = "','".join(evaluateIds['id'].astype(str).tolist())
    sql = f"select category,username from evaluate_stats where evaluateId in ('{ids}')"
    df = con.get_mssql_data(sql)
    if not df.empty:
        category_counts = df['category'].value_counts()
        for category, count in category_counts.iteritems():
            row[category] = count
    sql = f"select count(*) count from evaluate_report where evaluateId in ('{ids}')"
    df = con.get_mssql_data(sql)
    row['report'] = df.iloc[0]['count']
    return row


@user.route('/search', methods=['get'])
def search():
    sql = "select * from sys_user where privilege!=2"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    df['like'] = 0
    df['dislike'] = 0
    df['report'] = 0
    df = df.apply(stats_row, axis=1)
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records'))

@user.route('/register',methods=['get'])
@cross_origin(supports_credentials=True)
def register():
    mssql_connect = UseMySQL()
    username = request.args.get('username')
    name = request.args.get('name')
    passwd = request.args.get('password')
    res_pass = my_md5(passwd, random_str)
    sql = "select password, has_login, privilege, name " \
          "from sys_user " \
          f"where username = '{username}';"
    df = mssql_connect.get_mssql_data(sql)
    return jsonify(code=200, msg='success', has_login='1', token=generate_token(username),
                       privilege='1',name=name)
