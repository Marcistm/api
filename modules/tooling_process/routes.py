import datetime
import json
import os
import urllib
import pandas as pd
from flask import Blueprint, request, jsonify, make_response, send_file
from lib.db import UseMySQL
import urllib.parse
from utils.common import find_file

folder_path = 'D:/map'
tooling_process = Blueprint('tooling_process', __name__)




def file_search(file, type):
    data = []
    for file_name in os.listdir(os.path.join(folder_path)):
        if file in file_name:
            for item in os.listdir(os.path.join(folder_path, file_name)):
                if item.endswith('.pdf'):
                    temp = item.rsplit('.', 1)[0]
                    data.append(temp)
    data = list(set(data))
    df = pd.DataFrame(data, columns=['sub_map'])
    return df


@tooling_process.route('/plan/search', methods=['get'])
def plan_search():
    work_number = request.args.get('work_number')
    sql = "select process_num,tooling_name,tooling_no,tooling_map,work_order_memo,type,oa_id from work_order " \
          f"where work_number='{work_number}'"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    if not df.empty:
        process_num = df.iloc[0]['process_num']
        tooling_no = df.iloc[0]['tooling_no']
        tooling_name = df.iloc[0]['tooling_name']
        tooling_map = df.iloc[0]['tooling_map']
        work_order_memo = df.iloc[0]['work_order_memo']
        oa_id = df.iloc[0]['oa_id']
        type = df.iloc[0]['type']
    else:
        return jsonify(code=404, msg='未找到资源'), 404
    df2 = file_search(tooling_map, type)
    df2['process_num'] = df.iloc[0]['process_num']
    df2 = df2.sort_values(by='sub_map')
    sql = f"select work_row_item,is_print,comp_numbers from work_report where work_number='{work_number}' and number=1"
    df1 = con.get_mssql_data(sql)
    if not df1.empty:
        work_row_item = df1['work_row_item'].tolist()
        comp_numbers = df1['comp_numbers'].tolist()
        filtered_df = df1[df1['is_print'] == '已打印']
        print_row_item = filtered_df['work_row_item'].tolist()
    else:
        work_row_item = []
        print_row_item = []
    return jsonify(code=200, msg='成功', process_num=str(process_num), tooling_name=tooling_name,
                   comp_numbers=comp_numbers,
                   print_row_item=print_row_item, tooling_map=tooling_map, work_order_memo=work_order_memo,
                   work_row_item=work_row_item, tooling_no=tooling_no, oa_id=oa_id, data=df2.to_dict('records')), 200


def file_process(file):
    data = []
    for file_name in os.listdir(os.path.join(folder_path, file)):
        if file_name.endswith('.pdf'):
            temp = file_name.rsplit('.', 1)[0]
            data.append(temp)
    data = sorted(list(set(data)))
    df = pd.DataFrame(data, columns=['sub_map'])
    return df


@tooling_process.route('/create', methods=['GET'])
def create():
    work_number = request.args.get('work_number')
    file = request.args.get('file')
    if work_number:
        con = UseMySQL()
        sql = f"select tooling_map,type from work_order where work_number='{work_number}' "
        df = con.get_mssql_data(sql)
        if df.empty:
            return jsonify(code=404, msg='未找到资源'), 404
        tooling_map = df.iloc[0]['tooling_map']
        type = df.iloc[0]['type']
        file = tooling_map

    # 遍历目录中的所有文件和子文件夹
    if file:
        df = file_process(file)
    else:
        df = pd.DataFrame()
    return jsonify(code=200, msg='成功', data=df.to_dict('records')), 200  # 返回数据，转换为字典列表格式


def generate_work_order_number():
    now = datetime.datetime.now()
    year = str(now.year)[-2:]
    month = f'{now.month:02d}'
    day = f'{now.day:02d}'
    return year + month + day


@tooling_process.route('/create/submit', methods=['post'])
def tooling_map_submit():
    now = datetime.datetime.now()
    today = now.date()
    val = json.loads(request.get_data())
    header = pd.DataFrame(val['header'])
    con = UseMySQL()
    if header.iloc[0]['work_number'] == '':
        sql = f"SELECT max(work_number) work_number FROM work_order WHERE CONVERT(date, create_time) = '{today}'"
        df = con.get_mssql_data(sql)
        if df.iloc[0]['work_number'] is None or df.iloc[0]['work_number'] == '':
            work_number = generate_work_order_number() + f"{1:03d}"
        else:
            work_number = int(df.iloc[0]['work_number']) + 1
        header['work_number'] = work_number
        header['type'] = type
        con.write_table('work_order', header)
        return jsonify(code=200, msg='成功', work_number=work_number, tag=True), 200
    else:
        sql = f"update work_order set process_num={header.iloc[0]['process_num']},update_time=getdate()," \
              f"work_order_memo='{header.iloc[0]['work_order_memo']}',oa_id='{header.iloc[0]['oa_id']}' " \
              f"where work_number='{header.iloc[0]['work_number']}'"
        con.update_mssql_data(sql)
        return jsonify(code=200, msg='成功', tag=False), 200


@tooling_process.route('/del', methods=['GET'])
def work_del():
    work_number = request.args.get('work_number')
    sql = f"delete from work_order where work_number='{work_number}'"
    con = UseMySQL()
    df = con.update_mssql_data(sql)
    if df == 'success':
        return jsonify(code=200, msg='删除成功'), 200
    else:
        return jsonify(code=404, msg='删除失败'), 404





