import pymysql
import sqlInit

def GetWXID(chatroom):
    '''
    返回微信号
    从mysql中获取，速度快但只能查找已导入的朋友信息
    '''
    sql = "select UserName from friends where EncodeUserName='"+chatroom+"'"
    with sqlInit.MysqlInit() as mysql_cur:
        mysql_cur.execute(sql)
        result = mysql_cur.fetchone()
        if result != None:
            return result[0]
        else:
            return ""
    

def GetRowNum(chatroom,db="mysql",Des=2):
    '''
    mysql方法
    返回表的条数
    '''
    rowNum = []
    if db=="mysql":
        with sqlInit.MysqlInit() as mysql_cur:
            if Des == 2:
                sql = "select count(*) from "+chatroom
            else:
                sql = "select count(*) from "+chatroom+" where Des="+str(Des)
            mysql_cur.execute(sql)
            fetchResult = mysql_cur.fetchall()
            for row in fetchResult:
                rowNum = row[0]
    else:
        with sqlInit.SqliteInit() as sqlite_cur:
            if Des == 2:
                sql = "select count(*) from "+chatroom
            else:
                sql = "select count(*) from "+chatroom+" where Des="+str(Des)
            fetchResult = sqlite_cur.execute(sql)
            for row in fetchResult:
                rowNum = row[0]
    return int(rowNum)

def GetChatrooms(typename=0):
    '''
    获取指定类型的聊天
    1：群组，2：个人，3：公众号
    '''
    chatrooms = []
    if typename == 0:
        sql = "select EncodeUserName from friends"
    else: 
        sql = "select EncodeUserName from friends where Type="+str(typename)
    with sqlInit.MysqlInit() as mysql_cur:
        mysql_cur.execute(sql)
        result = mysql_cur.fetchall()
        for row in result:
            chatrooms.append(row[0])
    return chatrooms

def GetData(chatroom,columns=["Message"],Desname=2):
    '''
    获取单个聊天的数据
    chatroom：str；
    columns：list，["id","Type","SentFrom","CreateTime","Message","Des"]中选择，其中个人与公众号没有SentFrom；
    Desname：int， 0：发出，1：接收，2：全部。
    '''
    Messages_list = []
    if Desname == 2:
        sql = "select "+",".join(columns)+" from "+chatroom
    else:
        sql = "select "+",".join(columns)+" from "+chatroom+" where Des="+str(Desname)
    with sqlInit.MysqlInit() as mysql_cur:
        mysql_cur.execute(sql)
        result = mysql_cur.fetchall()
        for row in result:
            Messages_list.append(row)
    return Messages_list


if __name__=='__main__':
    pass
