import pymysql
import sqlite3
import contextlib

@contextlib.contextmanager
def MysqlInit(host='localhost', port=3306, user='wechat', passwd='123456', db='wechat',charset='utf8mb4'):
    mysql_conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db,charset=charset)
    mysql_cur = mysql_conn.cursor()
    try:
        yield mysql_cur
    finally:
        mysql_conn.commit()
        mysql_cur.close()
        mysql_conn.close()

@contextlib.contextmanager
def SqliteInit(db='../../data/MM.sqlite'):
    sqlite_conn = sqlite3.connect(db)
    sqlite_cur = sqlite_conn.cursor()
    try:
        yield sqlite_cur
    finally:
        sqlite_conn.commit()
        sqlite_cur.close()
        sqlite_conn.close()

if __name__=='__main__':
    pass