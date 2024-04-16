import json
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import cross_origin, CORS

from lib.db import UseMySQL
from modules.evaluate import evaluate

from modules.game import game
from modules.rank import rank
from utils.common import generate_token, my_md5, construct_update_statement

app = Flask(__name__)
random_str = 'hytek20@0_solt~%!$#^&*'  # 加密 盐
CORS(app, resources={r"/*": {"origins": "*"}})
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)
app.register_blueprint(rank, url_prefix='/rank')
app.register_blueprint(game, url_prefix='/game')
app.register_blueprint(evaluate, url_prefix='/evaluate')


@app.route('/login', methods=['get'])
@cross_origin(supports_credentials=True)
def login():
    mssql_connect = UseMySQL()
    username = request.args.get('username')
    passwd = request.args.get('password')
    res_pass = my_md5(passwd, random_str)
    sql = "select password, has_login, privilege, name " \
          "from sys_user " \
          f"where username = '{username}';"
    df = mssql_connect.get_mssql_data(sql)
    if df.empty:
        return jsonify(code=404, msg='user is not exist')
    res = df.to_dict('records')[0]
    passwd_db = res['password']
    if res_pass == passwd_db:
        return jsonify(code=200, msg='success', has_login=res['has_login'], token=generate_token(username),
                       privilege=res['privilege'],
                       name=res['name'])
    else:
        return jsonify(code=401, msg='password is not correct')


@app.route('/change_pswd', methods=['put'])
@cross_origin(supports_credentials=True)
def change_passwd():
    mysql_connect = UseMySQL()
    data = json.loads(request.get_data())
    sql = "update sys_user set password = '{}', has_login = {} where username = '{}';" \
        .format(my_md5(str(data['password']), random_str), 1, data['username'])
    df = mysql_connect.update_mssql_data(sql)
    if df == 'success':
        return jsonify(code=200, msg=df)
    else:
        return jsonify(code=404, msg="can't find resource")


@app.route('/delete', methods=['get'])
def delete():
    id = request.args.get('id')
    table = request.args.get('table')
    con = UseMySQL()
    sql = f"delete from {table} where id='{id}'"
    df = con.update_mssql_data(sql)
    if df == 'fail':
        return jsonify(code=404, msg='error'), 404
    return jsonify(code=200, msg='success'), 200


@app.route('/save', methods=['post'])
def save():
    val = json.loads(request.get_data())
    sql = construct_update_statement(val['table'],val['row'])
    con = UseMySQL()
    df = con.update_mssql_data(sql)
    if df == 'fail':
        return jsonify(code=404, msg='error'), 404
    return jsonify(code=200, msg='success'), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6325)
