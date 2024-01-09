import json
import datetime
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import cross_origin, CORS
import redis
app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
CORS(app, resources={r"/*": {"origins": "*"}})
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)


def generate_work_order_number():
    now = datetime.datetime.now()
    year = str(now.year)[-2:]
    month = f'{now.month:02d}'
    day = f'{now.day:02d}'
    return year + month + day


@app.route('/create', methods=['get'])
def create():
    item = request.args.get('item')
    if item is None:
        item=''
    remark = request.args.get('remark')
    if remark is None:
        remark=''
    all_keys = redis_client.keys('*')
    if all_keys:
        work_number = str(int(max(all_keys)) + 1)
    else:
        work_number = generate_work_order_number() + f"{1:03d}"
    redis_client.rpush(work_number, item)
    redis_client.rpush(work_number, remark)
    return jsonify(code=200, msg='success'), 200


@app.route('/search', methods=['get'])
def search():
    work_number = request.args.get('item_number')
    data = []
    if work_number:
        all_keys = redis_client.keys(work_number)
    else:
        all_keys = redis_client.keys('*')
    for i in all_keys:
        items = redis_client.lrange(i, 0, -1)
        decoded_items = [item for item in items]
        data.append({'item_number': i, 'item': decoded_items[0], 'remark': decoded_items[1]})
    if len(data) == 0:
        return jsonify(code=404, msg='not found'), 404
    return jsonify(code=200, msg='success', data=data), 200


@app.route('/update', methods=['get'])
def update():
    item_number = request.args.get('item_number')
    if item_number is None:
        return jsonify(code=400, msg='item_number is required'), 400
    if not redis_client.exists(item_number):
        return jsonify(code=404, msg=f'Item number {item_number} not found'), 404
    remark = request.args.get('remark')
    if remark is None:
        remark=''
    item = request.args.get('item')
    if item is None:
        item=''
    redis_client.lset(item_number, 0, item)
    redis_client.lset(item_number, 1, remark)
    return jsonify(code=200, msg='success'), 200


@app.route('/del', methods=['GET'])
def work_del():
    item_number = request.args.get('item_number')
    if item_number is None:
        return jsonify(code=400, msg='item_number is required'), 400
    if not redis_client.exists(item_number):
        return jsonify(code=404, msg=f'Item number {item_number} not found'), 404
    redis_client.delete(item_number)
    return jsonify(code=200, msg='delete success'), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6325)
