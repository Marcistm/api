# coding=utf-8
import pandas as pd
import pymysql


class UseMySQL(object):
    def __init__(self, config=None):
        if config is None:
            config = {
                'host': '127.0.0.1',
                'user': 'root',
                'password': '12345678',
                'db': 'attend',
                'port': 3306,
            }
        self.config = config
        self.con = pymysql.connect(**self.config)
        self.cur = self.con.cursor()

    def get_mssql_data(self, sql):
        cur = self.cur
        try:
            cur.execute(sql)
            index = cur.description
            field_names = [field[0] for field in index]
            record = cur.fetchall()
            if len(record) > 0:
                df = pd.DataFrame(list(record))
            else:
                df = pd.DataFrame([''] * len(field_names))
            df.columns = field_names
        except:
            df = pd.DataFrame(columns=['temp', 'none', 'df'])
        # for col in df.columns:
        #     if df[col].dtype == 'object':
        #         df[col] = df[col].fillna('').apply(lambda x: x.encode('latin1').decode('gbk').encode('utf-8').decode('utf-8'))
        return df

    def update_mssql_data(self, sql):
        cur = self.con.cursor()
        try:
            cur.execute(sql)
            self.con.commit()
            return 'success'
        except:
            return 'fail'
        finally:
            cur.close()

    def write_table(self, tb_name, df):
        try:
            columns = ', '.join(df.columns)
            values = ', '.join(['%s' for i in range(len(df.columns))])
            insert_query = f'INSERT INTO {tb_name} ({columns}) VALUES ({values})'
            # 执行INSERT语句
            cursor = self.con.cursor()
            for row in df.itertuples(index=False):
                try:
                    cursor.execute(insert_query, row)
                except Exception as e:
                    print(f"Error writing table {tb_name}: {e}")
                    return False
            self.con.commit()
            return True
        except Exception as e:
            print(f"Error writing table {tb_name}: {e}")
            return False

