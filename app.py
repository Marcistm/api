import json
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import cross_origin, CORS
import redis
from lib.db import UseMySQL
from modules.to_do_list.routes import to_do_list
from utils.common import generate_token, my_md5

app = Flask(__name__)
app.register_blueprint(to_do_list, url_prefix='/to_do_List')
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
print(redis_client)
CORS(app, resources={r"/*": {"origins": "*"}})
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6325)
