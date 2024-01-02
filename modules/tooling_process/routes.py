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


@tooling_process.route('/search', methods=['get'])
def search():
    start = request.args.get('start')
    condition = request.args.get('condition')
    tooling_map = request.args.get('tooling_map')
    tooling_no = request.args.get('tooling_no')
    work_number = request.args.get('work_number')
    con = UseMySQL()
    sql = "SELECT distinct A.create_time,A.finish_time,A.work_number,A.work_order_memo,A.tooling_no,A.tooling_name," \
          "A.process_num,B.work_row_item,A.condition order_condition,B.work_row_memo,B.sub_map," \
          "A.process_num * B.comp_numbers AS process_comp_numbers,B.condition,COALESCE((" \
          "SELECT top 1 B1.work_procedure FROM work_report B1 WHERE B1.work_row_item = B.work_row_item AND " \
          "B1.condition != '已结束' ORDER BY B1.number ),CASE WHEN NOT EXISTS (SELECT 1 FROM work_examine C1 " \
          "WHERE C1.work_row_item = B.work_row_item) THEN '检验' ELSE '工单完成' END) AS work_procedure,C.qualified_num," \
          "C.unqualified_num FROM work_order A JOIN work_report B ON A.work_number = B.work_number LEFT JOIN " \
          f"work_examine C ON B.work_row_item = C.work_row_item WHERE 1=1 "
    if start:
        end = request.args.get('end')
        end = (datetime.datetime.strptime(end, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        sql += f" AND A.create_time>='{start}' AND A.create_time<='{end}'"
    if tooling_map:
        sql += f" AND A.tooling_map='{tooling_map}'"
    if tooling_no:
        sql += f" AND A.tooling_no='{tooling_no}'"
    if work_number:
        sql += f" AND A.work_number='{work_number}'"
    df = con.get_mssql_data(sql)
    df = df.sort_values('work_number')
    if condition == '完成':
        df = df[df['order_condition'] == '已完成']
        df = df.sort_values(by='finish_time', ascending=False)
    if condition == '未完成':
        df = df[df['order_condition'].isnull()]
    df.drop_duplicates(subset='work_row_item', keep='first', inplace=True)
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/work_row_item/detail', methods=['get'])
def work_row_item_detail():
    work_row_item = request.args.get('work_row_item')
    con = UseMySQL()
    sql = "SELECT work_row_item,work_row_memo,number,work_procedure,work_memo,condition,worker,start_time," \
          "process_id,end_time,time " \
          f"FROM work_report WHERE work_row_item='{work_row_item}'"
    df = con.get_mssql_data(sql)
    df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['end_time'] = pd.to_datetime(df['end_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    condition = df['work_procedure'] == '来料'
    df.loc[condition, ['start_time', 'end_time', 'time']] = ''
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/download', methods=['post'])
def download():
    val = json.loads(request.get_data())
    work_numbers = val['work_numbers']
    con = UseMySQL()
    sql = "SELECT A.create_time, A.work_number, A.work_order_memo, A.tooling_no, A.tooling_name, A.process_num," \
          "B.work_row_item, B.work_row_memo, B.sub_map, A.process_num * B.comp_numbers process_comp_numbers, B.number," \
          "B.work_procedure, B.work_memo, B.condition, B.worker, B.start_time, B.end_time, B.time, C.qualified_num," \
          "C.unqualified_num,B.process_id FROM work_order A INNER JOIN work_report B ON A.work_number = B.work_number " \
          "left join work_examine C ON A.work_number = C.work_number AND B.work_row_item = C.work_row_item " \
          f"where A.work_number in ('{work_numbers}') ORDER BY work_row_item"
    df = con.get_mssql_data(sql)
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


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


@tooling_process.route('/search_version', methods=['GET'])
def search_version():
    data = []
    for item in os.listdir(folder_path):
        if '-' in item:
            data.append(item)
    if data:
        return jsonify(code=200, data=data, msg='success'), 200
    else:
        return jsonify(code=404, msg='未找到资源'), 404


def generate_work_order_number():
    now = datetime.datetime.now()
    year = str(now.year)[-2:]
    month = f'{now.month:02d}'
    day = f'{now.day:02d}'
    return year + month + day



@tooling_process.route('/no_map', methods=['get'])
def no_map():
    con = UseMySQL()
    sql = f"SELECT distinct tooling_no,tooling_map FROM work_order "
    df = con.get_mssql_data(sql)
    return jsonify(code=200, msg='success', data=df.to_dict('records')), 200


@tooling_process.route('/create/submit', methods=['post'])
def tooling_map_submit():
    now = datetime.datetime.now()
    today = now.date()
    val = json.loads(request.get_data())
    header = pd.DataFrame(val['header'])
    type = val['type']
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


@tooling_process.route('/work_procedure/get', methods=['get'])
def work_procedure_get():
    sql = "select work_name from work_procedure"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    if df.empty:
        return jsonify(code=404, msg='未找到资源'), 404
    else:
        return jsonify(code=200, msg='成功', data=df.to_dict('records')), 200


@tooling_process.route('/work_procedure/save', methods=['post'])
def work_procedure_save():
    val = json.loads(request.get_data())
    con = UseMySQL()
    df = pd.DataFrame(val['data'])
    if not df.empty:
        df_unstart = df[df['condition'] == '未开始']
        if not df_unstart.empty:
            sql = f"delete from work_report where work_row_item='{df.iloc[0]['work_row_item']}' and condition='未开始'"
            con.update_mssql_data(sql)
            df_unstart = df_unstart.fillna('')
            con.write_table('work_report', df_unstart)
    else:
        sql = f"delete from work_report where work_row_item='{val['work_row_item']}'"
        con.update_mssql_data(sql)
    return jsonify(code=200, msg='成功'), 200


@tooling_process.route('/work_row_item/get', methods=['get'])
def work_row_item_get():
    work_row_item = request.args.get('work_row_item')
    sql = "select work_procedure,work_memo,work_row_memo,condition,comp_numbers,sub_map from work_report " \
          f"where work_row_item='{work_row_item}'"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/report/search', methods=['get'])
def report_search():
    work_number = request.args.get('work_number')
    work_procedure = request.args.get('work_procedure')
    worker = request.args.get('worker')
    sql = "select a.start_time,b.work_number,b.work_order_memo,a.work_row_item,a.worker,a.number," \
          "a.work_row_memo,a.condition,b.tooling_no,a.pause_time," \
          "a.sub_map,a.work_procedure,a.work_memo,a.comp_numbers*b.process_num as process_num " \
          "from work_report a inner join work_order b on a.work_number=b.work_number " \
          f"where a.condition in ('未开始','已开始','已暂停','未检验') and a.work_number='{work_number[:9]}' "
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    # 根据 work_row_item 进行分组，并保留每个分组中 number 最小的行
    df_min = df.groupby('work_row_item')['number'].idxmin()
    # 根据索引获取保留的行
    df = df.loc[df_min]
    length = len(df)
    if len(work_number) > 9:
        df = df[df['work_row_item'] == work_number]
    df['tag'] = False
    if '装配' in df['work_procedure'].values and length > 1:
        df.loc[df['work_procedure'] == '装配', 'tag'] = True
    if work_procedure != '':
        df = df[df['work_procedure'] == work_procedure]
    df = df[df['condition'] != '未检验']
    df = df.loc[(df['worker'] == worker) | (df['worker'].isnull())]
    df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['pause_time'] = pd.to_datetime(df['pause_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/report/start', methods=['get'])
def report_start():
    con = UseMySQL()
    work_row_item = request.args.get('work_row_item')
    number = request.args.get('number')
    sql = f"select worker from work_report where work_row_item='{work_row_item}' and number={number}"
    df = con.get_mssql_data(sql)
    if df.iloc[0]['worker'] is not None:
        return jsonify(code=200, msg='已被他人抢单'), 200
    worker = request.args.get('worker')
    sql = f"update work_report set condition='已开始',start_time=getdate(),worker='{worker}' " \
          f"where work_row_item='{work_row_item}' and number={number}"
    con.update_mssql_data(sql)
    return jsonify(code=200, msg='操作成功'), 200


@tooling_process.route('/report/end', methods=['get'])
def report_end():
    work_row_item = request.args.get('work_row_item')
    number = request.args.get('number')
    con = UseMySQL()
    work_procedure = request.args.get('work_procedure')
    condition = '未检验'
    if work_procedure == '来料':
        condition = '已结束'
    sql = f"select count(1) result from work_report where work_row_item='{work_row_item}' and number='{number}' and " \
          "end_time is not null"
    df = con.get_mssql_data(sql)
    if df.iloc[0]['result'] > 0:
        return jsonify(code=404, msg='已结束'), 404
    sql = f"DECLARE @current_time DATETIME = GETDATE(); UPDATE work_report SET condition='{condition}'," \
          f"end_time = @current_time," \
          f"time = time + IIF(pause_time IS NULL, DATEDIFF(second , start_time, @current_time)," \
          "DATEDIFF(second , pause_time, @current_time)) " \
          f"WHERE work_row_item='{work_row_item}' AND number='{number}'"
    con.update_mssql_data(sql)
    sql = "select ROUND(time / 60.0, 2) AS divide_time,start_time,end_time,sub_map,work_row_item,work_procedure " \
          f"from work_report where work_row_item='{work_row_item}' and number='{number}'"
    df = con.get_mssql_data(sql)
    df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['end_time'] = pd.to_datetime(df['end_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(code=200, msg='操作成功', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/print/get', methods=['get'])
def print_get():
    con = UseMySQL()
    work_row_item = request.args.get('work_row_item')
    work_number = request.args.get('work_number')
    sql = f"select * from work_order where work_number='{work_number}' "
    df = con.get_mssql_data(sql)
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/reported/search', methods=['get'])
def reported_search():
    work_number = request.args.get('work_number')
    work_procedure = request.args.get('work_procedure')
    sql = "select a.start_time,b.work_number,b.work_order_memo,a.work_row_item,a.worker,a.number," \
          "a.work_row_memo,a.condition,b.tooling_no,a.end_time," \
          "a.sub_map,a.work_procedure,a.work_memo,a.comp_numbers*b.process_num as process_num " \
          "from work_report a inner join work_order b on a.work_number=b.work_number " \
          f"where a.condition in ('已结束','未检验','已开始','已暂停') and a.work_number='{work_number[:9]}'"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    # 根据 work_row_item 进行分组，并保留每个分组中 number 最小的行
    df_max = df.groupby('work_row_item')['number'].idxmax()
    # 根据索引获取保留的行
    df = df.loc[df_max]
    if len(work_number) > 9:
        df = df[df['work_row_item'] == work_number]
    if work_procedure != '':
        df = df[df['work_procedure'] == work_procedure]
    df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['end_time'] = pd.to_datetime(df['end_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


