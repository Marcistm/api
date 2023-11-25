import json
import numpy as np
import pandas as pd
import requests
from flask import Flask, jsonify, request
from flask_cors import cross_origin, CORS

from lib.db import UseMySQL
from modules.tooling_process.routes import tooling_process
from utils.common import generate_token, my_md5

app = Flask(__name__)
app.register_blueprint(tooling_process, url_prefix='/tooling_process')
random_str = 'hytek20@0_solt~%!$#^&*'  # 加密 盐
CORS(app, resources={r"/*": {"origins": "*"}})
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)


@app.route('/login', methods=['get'])
@cross_origin(supports_credentials=True)
def login():
    """
    登录
    :param: work_id: 工号
    :param: password: 密码
    :return: JSON
    """
    # wz14142 12345678 2b2786d75fe0463ed7a764532695dae0
    mssql_connect = UseMySQL()
    work_id = request.args.get('work_id')
    passwd = request.args.get('password')
    res_pass = my_md5(passwd, random_str)
    sql = "select password, has_login, gzmap_privilege,auto_privilege,experiment_privilege,tooling_privilege, name " \
          "from sys_user " \
          "where work_id = '{}';".format(work_id)
    df = mssql_connect.get_mssql_data(sql)
    if df.empty:
        return jsonify(code=404, msg='用户不存在')
        # return {'code': 404, 'msg': '用户不存在'}
    res = df.to_dict('records')[0]
    passwd_db = res['password']
    if res_pass == passwd_db:
        return jsonify(code=200, msg='success', has_login=res['has_login'], token=generate_token(work_id),
                       gzmap_privilege=res['gzmap_privilege'], auto_privilege=res['auto_privilege'],
                       tooling_privilege=res['tooling_privilege'], experiment_privilege=res['experiment_privilege'],
                       name=res['name'])
    else:
        return jsonify(code=401, msg='密码不正确')

@app.route('/change_pswd', methods=['put'])
@cross_origin(supports_credentials=True)
def change_passwd():
    """
    更改用户的密码
    :param: work_id: 工号
    :param: password: 密码
    :return: JSON
    """
    mysql_connect = UseMySQL()
    data = json.loads(request.get_data())
    sql = "update sys_user set password = '{}', has_login = {} where work_id = '{}';" \
        .format(my_md5(str(data['password']), random_str), 1, data['work_id'])
    df = mysql_connect.update_mssql_data(sql)
    if df == 'success':
        return jsonify(code=200, msg=df)
    else:
        return jsonify(code=404, msg="can't find resource")



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6325)
