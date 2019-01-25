import pymysql
import sqlInit


def GetChatrooms(typename=0):
    '''
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
