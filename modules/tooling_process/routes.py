import datetime
import json
import os
import urllib
import pandas as pd
from flask import Blueprint, request, jsonify, make_response, send_file
from lib.db import UseMySQL
import urllib.parse
from utils.common import find_file

folder_path = 'address'
tooling_process = Blueprint('tooling_process', __name__)


@tooling_process.route('/report/pause', methods=['get'])
def report_pause():
    number = request.args.get('number')
    work_row_item = request.args.get('work_row_item')
    con = UseMySQL()
    sql = "DECLARE @current_time DATETIME = GETDATE(); UPDATE work_report SET condition='已暂停'," \
          "pause_time = @current_time," \
          "time = time + IIF(pause_time IS NULL, DATEDIFF(second , start_time, @current_time)," \
          "DATEDIFF(second , pause_time, @current_time)) " \
          f"WHERE work_row_item='{work_row_item}' AND number='{number}' and condition='已开始'"
    con.update_mssql_data(sql)
    return jsonify(code=200, msg='success'), 200


@tooling_process.route('/report/restart', methods=['get'])
def report_restart():
    number = request.args.get('number')
    work_row_item = request.args.get('work_row_item')
    sql = "UPDATE work_report SET condition='已开始',pause_time=getdate() " \
          f"WHERE work_row_item='{work_row_item}' AND number='{number}'"
    con = UseMySQL()
    con.update_mssql_data(sql)
    return jsonify(code=200, msg='success'), 200


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
    if condition == '技术完成':
        df = df[df['order_condition'] == '技术完成']
        df['work_procedure'] = '技术完成'
        df = df.sort_values(by='finish_time', ascending=False)
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
    con = UseMySQL(sqlserver_config)
    sql = f"select mainid process_id,zgs work_time from formtable_main_422_dt1 where gdhm='{work_row_item}'"
    df1 = con.get_mssql_data(sql)
    if not df1.empty:
        df = pd.merge(df, df1, on='process_id', how='left')
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
    work_row_items = "','".join(df['work_row_item'].unique())
    con = UseMySQL(sqlserver_config)
    sql = f"select mainid process_id,zgs work_time from formtable_main_422_dt1 where gdhm in ('{work_row_items}')"
    df1 = con.get_mssql_data(sql)
    df = pd.merge(df, df1, on='process_id', how='left')
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/examine/search', methods=['get'])
def examine_search():
    con = UseMySQL()
    sql = "SELECT t.work_row_memo,t.work_row_item,t.comp_numbers*a.process_num comp_numbers,t.sub_map,t.work_procedure," \
          "t.number FROM work_report t inner join work_order a on a.work_number=t.work_number WHERE t.condition = '未检验'"
    df = con.get_mssql_data(sql)
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/examine/finish', methods=['get'])
def examine_finish():
    number = request.args.get('number')
    work_procedure = request.args.get('work_procedure')
    work_row_item = request.args.get('work_row_item')
    qualified_num = request.args.get('qualified_num')
    unqualified_num = request.args.get('unqualified_num')
    reuse_num = request.args.get('reuse_num')
    rework_num = request.args.get('rework_num')
    key_size = request.args.get('key_size')
    work_number = request.args.get('work_number')
    sql_insert = f"""INSERT INTO work_examine (work_row_item, qualified_num, unqualified_num, number, work_number,
     key_size, rework_num, reuse_num,work_procedure) VALUES('{work_row_item}', '{qualified_num}', '{unqualified_num}', 
    '{number}', '{work_number}','{key_size}','{rework_num}','{reuse_num}','{work_procedure}');"""
    con = UseMySQL()
    df = con.update_mssql_data(sql_insert)
    if df == 'success':
        sql = f"update work_report set condition='已结束' where number='{number}' and work_row_item='{work_row_item}'"
        df = con.update_mssql_data(sql)
        if df == 'fail':
            return jsonify(code=404, msg='fail'), 404
        sql = f"select count(1) result from work_report where condition!='已结束' and work_number='{work_number}'"
        df = con.get_mssql_data(sql)
        if df.iloc[0]['result'] == 0:
            sql = f"update work_order set finish_time=getdate(),condition='已完成' where work_number='{work_number}'"
            con.update_mssql_data(sql)
        return jsonify(code=200, msg='success'), 200
    else:
        return jsonify(code=404, msg='fail'), 404


@tooling_process.route('/report/tech_end', methods=['get'])
def report_tech_end():
    con = UseMySQL()
    work_number = request.args.get('work_row_item')
    sql = f"update work_report set condition='技术完成' where work_number='{work_number}' and condition!='已结束'"
    df = con.update_mssql_data(sql)
    if df == 'success':
        sql = f"update work_order set finish_time=getdate(),condition='技术完成' where work_number='{work_number}'"
        con.update_mssql_data(sql)
        return jsonify(code=200, msg='success'), 200
    else:
        return jsonify(code=404, msg='fail'), 404


def file_search(file, type):
    data = []
    if type == '临时图纸':
        for file_name in os.listdir(os.path.join(folder_path, type)):
            if file in file_name:
                if file_name.endswith('.pdf'):
                    temp = file_name.rsplit('.', 1)[0]
                    data.append(temp)
    else:
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
    return jsonify(code=200, msg='成功', process_num=str(process_num), tooling_name=tooling_name,comp_numbers=comp_numbers,
                   print_row_item=print_row_item,tooling_map=tooling_map, work_order_memo=work_order_memo,
                   work_row_item=work_row_item,tooling_no=tooling_no,oa_id=oa_id, data=df2.to_dict('records')), 200


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
        if type == '临时图纸':
            return jsonify(code=200, msg='成功', sub_map=tooling_map), 200
        else:
            file = tooling_map
    # 遍历目录中的所有文件和子文件夹
    if file:
        df = file_process(file)
    else:
        df = pd.DataFrame()
    return jsonify(code=200, msg='成功', data=df.to_dict('records')), 200  # 返回数据，转换为字典列表格式


@tooling_process.route('/preview', methods=['get'])
def get_file_stream():
    local_path = 'temp_paper.pdf'
    map = urllib.parse.unquote(request.args.get('map'))
    if '装配图' in map or '总装图' in map:
        map += '-000'
    map = map + '.pdf'
    name = find_file(folder_path, map)
    response = make_response(send_file(local_path))
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', 'attachment', filename=local_path)
    os.remove(local_path)
    return response


@tooling_process.route('/get_other_file', methods=['get'])
def get_other_file():
    def get_pdf_files(directory):
        pdf_file_names = []
        for root, directories, files in os.walk(directory):
            for file in files:
                if file.endswith(".pdf"):
                    file_name = os.path.splitext(file)[0]
                    pdf_file_names.append(file_name)
        return pdf_file_names

    map = request.args.get('map')
    map += '-000.pdf'
    map_path = find_file(folder_path, map)
    parent_directory = os.path.dirname(map_path)
    if parent_directory == '临时图纸':
        related_pdfs = get_pdf_files(parent_directory)
    else:
        related_pdfs = []
    return jsonify(code=200, msg='success', data=related_pdfs), 200


@tooling_process.route('/search_version', methods=['GET'])
def search_version():
    type = request.args.get('type')
    data = []
    if type == '正式图纸':
        for item in os.listdir(folder_path):
            if '-' in item:
                data.append(item)
    else:
        df = file_process('临时图纸')
        data = df['sub_map'].tolist()
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


def get_pdf_files_in_parent_directory(path):
    parent_directory = os.path.dirname(path)
    file_list = os.listdir(parent_directory)
    pdf_files = [file for file in file_list if
                 os.path.isfile(os.path.join(parent_directory, file)) and file.lower().endswith('.pdf')]
    return pdf_files


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


@tooling_process.route('/work_row_item/history/get', methods=['get'])
def work_row_item_history_get():
    index = request.args.get('index')
    tooling_no = request.args.get('tooling_no')
    work_number = request.args.get('work_number')
    sql = "SELECT a.work_procedure,a.work_memo FROM work_report a " \
          "INNER JOIN work_order wo ON a.work_number = wo.work_number " \
          f"WHERE wo.tooling_no = '{tooling_no}' AND a.work_row_item = (SELECT MAX(work_number) + '-{index}' " \
          f"FROM work_order WHERE work_number < '{work_number}' AND tooling_no = '{tooling_no}') "
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


@tooling_process.route('/report/oa', methods=['get'])
def report_oa():
    work_row_item = request.args.get('work_row_item')
    number = request.args.get('number')
    con = UseMySQL()
    oa_con = UseMySQL(sqlserver_config)
    sql = "select max(id) process_id from formtable_main_422"
    process_id = oa_con.get_mssql_data(sql).iloc[0]['process_id']
    sql = f"update work_report set process_id='{process_id}' where work_row_item='{work_row_item}' AND number='{number}'"
    df = con.update_mssql_data(sql)
    if df == 'fail':
        return jsonify(code=404, msg='操作失败'), 404
    return jsonify(code=200, msg='操作成功'), 200


@tooling_process.route('/print/get', methods=['get'])
def print_get():
    con = UseMySQL()
    work_row_item = request.args.get('work_row_item')
    sql = f"update work_report set is_print='已打印' where work_row_item='{work_row_item}' and is_print is null"
    df = con.update_mssql_data(sql)
    if df == 'fail':
        return jsonify(code=404, msg='操作失败'), 404
    work_number = request.args.get('work_number')
    sql = f"select * from work_order where work_number='{work_number}' "
    df = con.get_mssql_data(sql)
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/work_time/get', methods=['get'])
def work_time_get():
    index = (int(request.args.get('page')) - 1) * 9
    process = request.args.get('tooling_process')
    sql = "select tooling_process,work_time,work_type,work_process,part,rules from work_process_time "
    if process:
        sql = sql + f" where tooling_process like '%{process}%' "
    sql = sql + f"order by id OFFSET {index} ROWS FETCH NEXT 9 ROWS ONLY"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    sql = "select count(1) res from work_process_time"
    if process:
        sql = sql + f" where tooling_process like '%{process}%' "
    total = int(con.get_mssql_data(sql).iloc[0]['res'])
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records'), total=total), 200


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


@tooling_process.route('/report/revoke', methods=['get'])
def report_revoke():
    work_row_item = request.args.get('work_row_item')
    number = request.args.get('number')
    condition = request.args.get('condition')
    sql = f"update work_report set condition='未开始',time=0,start_time=null,end_time=null,pause_time=null,worker=null," \
          f"process_id=null where work_row_item='{work_row_item}' and number={number}"
    con = UseMySQL()
    df = con.update_mssql_data(sql)
    if df == 'fail':
        return jsonify(code=404, msg='fail'), 404
    if condition == '已结束':
        sql = f"delete from work_examine where work_row_item='{work_row_item}' and number={number}"
        df = con.update_mssql_data(sql)
        if df == 'fail':
            return jsonify(code=404, msg='fail'), 404
    return jsonify(code=200, msg='success'), 200


@tooling_process.route('/parts_tooling/get', methods=['get'])
def parts_tooling_get():
    sql = "select item,pjgzmc from parts_tooling"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/purpose_equip/get', methods=['get'])
def purpose_equip_get():
    sql = "select item,ytsb from purpose_equip"
    con = UseMySQL()
    df = con.get_mssql_data(sql)
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200


@tooling_process.route('/report/num', methods=['get'])
def report_num():
    scrap_num = request.args.get('scrap_num')
    finish_num = request.args.get('finish_num')
    number = request.args.get('number')
    work_row_item = request.args.get('work_row_item')
    sql = f"update work_report set scrap_num={scrap_num},finish_num={finish_num} " \
          f"where work_row_item='{work_row_item}' and number={number}"
    con = UseMySQL()
    df = con.update_mssql_data(sql)
    if df == 'fail':
        return jsonify(code=404, msg='fail'), 404
    return jsonify(code=200, msg='success'), 200


@tooling_process.route('/examine/record', methods=['get'])
def examine_record():
    work_number = request.args.get('work_number')
    con = UseMySQL()
    sql = "SELECT e.work_row_item,e.qualified_num,e.unqualified_num,e.reuse_num,e.rework_num,t.work_row_memo," \
          "t.sub_map,e.work_procedure,e.number,e.key_size FROM work_examine e inner join work_report t " \
          f"on e.work_row_item=t.work_row_item WHERE e.work_procedure is not null and e.work_number='{work_number[:9]}'"
    df = con.get_mssql_data(sql)
    df['comp_numbers'] = df['qualified_num'] + df['unqualified_num'] + df['reuse_num'] + df['rework_num']
    if len(work_number) > 9:
        df = df[df['work_row_item'] == work_number]
    work_procedure = request.args.get('work_procedure')
    if work_procedure != '':
        df = df[df['work_procedure'] == work_procedure]
    df = df.drop_duplicates(subset=['work_row_item', 'number'])
    df['ten'] = df['work_row_item'].str.slice(start=10).astype(int)
    df = df.sort_values(by=['ten', 'number'])
    return jsonify(code=200, msg='success', data=df.fillna('').to_dict('records')), 200
