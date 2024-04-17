import base64
import hmac
import os
import time
import hashlib
from datetime import datetime, timedelta, date
from re import search, I


class RegexMap:
    def __init__(self, n_dic, val):
        self._items = n_dic
        self.__val = val

    def __getitem__(self, key):
        for regex in self._items.keys():
            if search(regex, key, I):
                return self._items[regex]
        return self.__val


def generate_token(key, expire=3600):
    """
    :param key: 用户给定的用于生成token的key
    :param expire: token过期时间，默认1小时，单位为s
    :return: token:str
    """
    ts_str = str(time.time() + expire)
    ts_byte = ts_str.encode("utf-8")
    sha1_tshexstr = hmac.new(key.encode("utf-8"), ts_byte, 'sha1').hexdigest()
    token = ts_str + ':' + sha1_tshexstr
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")


def days_cur_month():
    m = datetime.now().month
    y = datetime.now().year
    if m == 12:
        ndays = 31
    else:
        ndays = (date(y, m + 1, 1) - date(y, m, 1)).days
    d1 = date(y, m, 1)
    d2 = date(y, m, ndays)
    delta = d2 - d1
    return [(d1 + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]


def certify_token(key, token):
    """
    :param key: 生成token时指定的key
    :param token: 要检验的token
    :return: bool
    """
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    if len(token_list) != 2:
        return False
    ts_str = token_list[0]
    if float(ts_str) < time.time():
        # token expired
        return False
    known_sha1_tsstr = token_list[1]
    sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
    calc_sha1_tsstr = sha1.hexdigest()
    if calc_sha1_tsstr != known_sha1_tsstr:
        # token certification failed
        return False
    # token certification success
    return True


def my_md5(s, salt=''):
    """
    :param s: 要加密的字符串
    :param salt: 加密的盐，默认无
    :return: res: str
    """
    s = s + salt
    news = str(s).encode()
    m = hashlib.md5(news)
    return m.hexdigest()


def deal_time(start, end):
    noon_start = datetime.strptime('11:30:00', '%H:%M:%S')
    noon_end = datetime.strptime('13:00:00', '%H:%M:%S')
    eve_start = datetime.strptime('17:30:00', '%H:%M:%S')
    eve_end = datetime.strptime('18:00:00', '%H:%M:%S')
    yb_start = datetime.strptime('22:30:00', '%H:%M:%S')
    yb_end = datetime.strptime('23:00:00', '%H:%M:%S')
    start = datetime.strptime(start, '%H:%M:%S')
    end = datetime.strptime(end, '%H:%M:%S')
    temp = (end - start).total_seconds() / 60
    if temp < 0:
        temp += 24 * 60
    if start < noon_start:
        if end > yb_end or end < start:
            return '%.2f' % (temp - 150)
        elif end > eve_end:
            return '%.2f' % (temp - 120)
        elif end > noon_end:
            return '%.2f' % (temp - 90)
    elif start < eve_start:
        if end > yb_end or end < start:
            return '%.2f' % (temp - 60)
        elif end > eve_end:
            return '%.2f' % (temp - 30)
    elif start < yb_start:
        if end > yb_end or end < start:
            return '%.2f' % (temp - 30)
    return '%.2f' % temp


def split_file_name(file_name):
    """拆分文件名和后缀"""
    name, ext = os.path.splitext(file_name)
    return name, ext


import shutil


def find_file(folder_path, file_name):
    """
    在整个文件夹查找文件
    :param folder_path: 要查找的文件夹路径
    :param file_name: 要查找的文件名
    :return: 文件路径，如果找不到则返回None
    """
    for root, dirs, files in os.walk(folder_path):
        for name in files:
            if name == file_name:
                return os.path.join(root, name)
    return None


def download_file(local_path, remote_path):
    """
    从共享文件夹下载文件到本地
    :param local_path: 本地文件路径
    :param remote_path: 共享文件夹中的文件路径
    """
    if os.path.isfile(local_path) and os.path.getsize(local_path) == os.path.getsize(remote_path):
        return
    else:
        try:
            with open(local_path, 'wb') as f:
                with open(remote_path, 'rb') as f2:
                    shutil.copyfileobj(f2, f)
        except Exception as err:
            return


def construct_update_statement(table_name, field_value_pairs, id_column='id'):
    """
    构造一个基于给定表名、字段-值对和条件的SQL更新语句。

    Args:
    table_name (str): 要更新的表的名称。
    field_value_pairs (dict): 要更新的字段-值对的字典。
    condition (str): 用于更新语句的条件。
    id_column (str): 用于更新语句的id列名，默认为'id'。

    Returns:
    str: 构造的SQL更新语句。
    """
    set_clause = ", ".join([f"{field} = '{value}'" for field, value in field_value_pairs.items() if field != id_column])
    update_statement = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = '{field_value_pairs[id_column]}' "
    return update_statement


def generate_date_sequence(start_date_str, end_date_str):
    date_format = '%Y-%m-%d'
    start_date = datetime.strptime(start_date_str, date_format)
    end_date = datetime.strptime(end_date_str, date_format)

    date_list = []
    current_date = start_date

    while current_date < end_date:
        date_list.append(current_date.strftime(date_format))
        current_date += timedelta(days=1)

    return date_list
