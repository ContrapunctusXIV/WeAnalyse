import re
import sys
import hashlib
import sqlite3
import pymysql
import sqlInit

def GetWXID(chatroom):
    '''
    返回微信号
    '''
    wxid_hashed = {}
    hashed_wxid = {}
    raw_data = {}
    with sqlInit.SqliteInit(db='WCDB_Contact.sqlite') as sqlite_cur:
        fetchResult = sqlite_cur.execute("select userName,type,dbContactRemark,dbContactProfile from Friend")
        for row in fetchResult:
            wxid = row[0]
            hmd5 = hashlib.md5()
            hmd5.update(wxid.encode(encoding="utf-8"))
            wxid_hashed[row[0]] = "Chat_"+hmd5.hexdigest()
            hashed_wxid["Chat_"+hmd5.hexdigest()] = row[0]
            raw_data[row[0]] = ["Chat_"+hmd5.hexdigest(),row[1],row[2].decode(encoding="utf-8"),row[3]]
    if chatroom in hashed_wxid.keys():
        return hashed_wxid[chatroom]
    else:
        return ""

def GetRowNum(chatroom,db="sqlite"):
    '''
    返回表的条数
    '''
    rowNum = []
    if db=="mysql":
        with sqlInit.MysqlInit() as mysql_cur:
            mysql_cur.execute("select count(*) from "+chatroom)
            fetchResult = mysql_cur.fetchall()
            for row in fetchResult:
                rowNum = row[0]
    else:
        with sqlInit.SqliteInit() as sqlite_cur:
            fetchResult = sqlite_cur.execute("select count(*) from "+chatroom)
            for row in fetchResult:
                rowNum = row[0]
    return int(rowNum)

def ChatroomType(chatroom):
    '''
    返回聊天类型
    返回值：int，1是群组，2是个人，3是公众号
    '''
    Msgcounter = 0
    Typecounter = 0
    if chatroom == "Chat_ffcc9697ac3309e93d80f7773b133f88":
        return 3 #傻逼腾讯新闻把自己的消息类型（type）全设置成了1
    elif chatroom == "Chat_2d5de498c19fac1476f42e2428c51e67" or chatroom == "Chat_c376b0ef92a23a9abeac229b752398f2":
        return 3 #个人原因，如果有些人是复读机，那我建议你把他们视作公众号
    else:
        with sqlInit.SqliteInit() as sqlite_cur:
            fetchResult = sqlite_cur.execute("select Message from "+chatroom+" where Type=1 and Des=1 limit 100")
            for row in fetchResult:
                if ":" in row[0]:
                    Msgcounter += 1
        if Msgcounter/100>0.5: #群组
            return 1
        else:
            with sqlInit.SqliteInit() as sqlite_cur:
                fetchType = sqlite_cur.execute("select Type from "+chatroom+" where Des=1 limit 100")
                for row in fetchType:
                    if row[0] == 49:
                        Typecounter += 1
            if Typecounter/100<0.5: #个人
                return 2
            else: #公众号
                return 3

def InsertFriends(chatroom, Type):
    '''
    将联系人信息导入到数据库
    '''
    sql = "INSERT INTO Friends(Type,EncodeUserName,UserName) VALUES(%s,%s,%s)"
    with sqlInit.MysqlInit() as mysql_cur:
        mysql_cur.execute(sql,[Type,chatroom,GetWXID(chatroom)])

def GetGroupData(chatroom):
    '''
    获取单个群聊的消息
    '''
    pattern1 = re.compile('fromusername.*?"(.*?)"')
    pattern2 = re.compile('"(.*?)"')
    well_tempered_data = []
    with sqlInit.SqliteInit() as sqlite_cur:
        result = sqlite_cur.execute("SELECT Type, CreateTime, Message, Des from "+chatroom)
        for row in result:
            Type = row[0]
            CreateTime = row[1]
            Des = row[3]
            if (Type == 10000) or (Type == 10002) or (Type==1000):
                if "撤回" in row[2]:
                    if(len(pattern2.findall(row[2]))>0):
                        SentFrom = pattern2.findall(row[2])[0]
                        Message = "撤回消息"
                    else:
                        SentFrom = "我"
                        Message = "撤回消息"
                else:
                    SentFrom = "system"
                    Message = row[2].replace("\n","")
            elif Des == 0:
                    SentFrom = "我"
                    Message = row[2].replace("\n","")
            elif "<" in row[2].split(":",1)[0]:
                if len(pattern1.findall(row[2]))>0:
                    SentFrom = pattern1.findall(row[2])[0]
                    Message = row[2].replace("\n","")
                else:
                    SentFrom = "unknow"
                    Message = row[2]
            elif len(pattern1.findall(row[2]))>0:
                SentFrom = pattern1.findall(row[2])[0]
                Message = row[2].replace(SentFrom+":",'').replace("\n","")
            else:
                SentFrom = row[2].split(":",1)[0]
                Message = row[2].split(":",1)[1].replace("\n","")
            
            well_tempered_data.append([Type,CreateTime,SentFrom,Message,Des])
    sql = "INSERT INTO "+chatroom+"(Type,CreateTime,SentFrom,Message,Des) VALUES(%s,%s,%s,%s,%s)"
    with sqlInit.MysqlInit() as mysql_cur:
        for line in well_tempered_data:
            mysql_cur.execute(sql,line)
    
def GetOthersData(chatroom):
    '''
    获取单个单聊或公众号的消息
    '''
    well_tempered_data = []
    with sqlInit.SqliteInit() as sqlite_cur:
        result = sqlite_cur.execute("SELECT Type, CreateTime, Message, Des from "+chatroom)
        for row in result:
            Type = row[0]
            CreateTime = row[1]
            Des = row[3]
            if (Type == 10000) or (Type == 10002):
                if "撤回" or "has recalled a message" in row[2]:
                        Message = "撤回消息"
                else:
                    Message = row[2].replace("\n","")
            else:
                Message = row[2].replace("\n","")
            well_tempered_data.append([Type,CreateTime,Message,Des])
    sql = "INSERT INTO "+chatroom+"(Type,CreateTime,Message,Des) VALUES(%s,%s,%s,%s)"
    with sqlInit.MysqlInit() as mysql_cur:
        for line in well_tempered_data:
            mysql_cur.execute(sql,line)

def GetGeoData():
    '''
    获取地理信息数据
    '''
    geo_dict = {}
    with sqlInit.GeoSqlInit() as sqlite_cur:
        fetchResult1 = sqlite_cur.execute("select code,name from area")
        for row in fetchResult1:
            if len(row[1])<3:
                if row[1] in geo_dict.keys():
                    if len(geo_dict[row[1]])>=len(row[0]):
                        geo_dict[row[1]] = row[0]
                else:
                    geo_dict[row[1]] = row[0]
            elif len(row[1])==3:
                if row[1][:2] in geo_dict.keys():
                    if len(geo_dict[row[1][:2]])>=len(row[0]):
                        geo_dict[row[1][:2]] = row[0]
                else:
                    geo_dict[row[1][:2]] = row[0]
            elif len(row[1])>3:
                if row[1][:3] in geo_dict.keys():
                    if len(geo_dict[row[1][:3]])>=len(row[0]):
                        geo_dict[row[1][:3]] = row[0]
                else:
                    geo_dict[row[1][:3]] = row[0]
        fetchResult2 = sqlite_cur.execute("select code,name from city")
        for row in fetchResult2:
            if len(row[1])<3:
                if row[1] in geo_dict.keys():
                    if len(geo_dict[row[1]])>=len(row[0]):
                        geo_dict[row[1]] = row[0]
                else:
                    geo_dict[row[1]] = row[0]
            elif len(row[1])==3:
                if row[1][:2] in geo_dict.keys():
                    if len(geo_dict[row[1][:2]])>=len(row[0]):
                        geo_dict[row[1][:2]] = row[0]
                else:
                    geo_dict[row[1][:2]] = row[0]
            elif len(row[1])>3:
                if row[1][:3] in geo_dict.keys():
                    if len(geo_dict[row[1][:3]])>=len(row[0]):
                        geo_dict[row[1][:3]] = row[0]
                else:
                    geo_dict[row[1][:3]] = row[0]
        fetchResult3 = sqlite_cur.execute("select code,name from province")
        for row in fetchResult3:
            if len(row[1])<3:
                if row[1] in geo_dict.keys():
                    if len(geo_dict[row[1]])>=len(row[0]):
                        geo_dict[row[1]] = row[0]
                else:
                    geo_dict[row[1]] = row[0]
            elif len(row[1])==3:
                if row[1][:2] in geo_dict.keys():
                    if len(geo_dict[row[1][:2]])>=len(row[0]):
                        geo_dict[row[1][:2]] = row[0]
                else:
                    geo_dict[row[1][:2]] = row[0]
            elif len(row[1])>3:
                if row[1][:3] in geo_dict.keys():
                    if len(geo_dict[row[1][:3]])>=len(row[0]):
                        geo_dict[row[1][:3]] = row[0]
                else:
                    geo_dict[row[1][:3]] = row[0]
        fetchResult4 = sqlite_cur.execute("select code,name from village")
        for row in fetchResult4:
            if len(row[1])<3:
                if row[1] in geo_dict.keys():
                    if len(geo_dict[row[1]])>=len(row[0]):
                        geo_dict[row[1]] = row[0]
                else:
                    geo_dict[row[1]] = row[0]
            elif len(row[1])==3:
                if row[1][:2] in geo_dict.keys():
                    if len(geo_dict[row[1][:2]])>=len(row[0]):
                        geo_dict[row[1][:2]] = row[0]
                else:
                    geo_dict[row[1][:2]] = row[0]
            elif len(row[1])>3:
                if row[1][:3] in geo_dict.keys():
                    if len(geo_dict[row[1][:3]])>=len(row[0]):
                        geo_dict[row[1][:3]] = row[0]
                else:
                    geo_dict[row[1][:3]] = row[0]
    sql = "INSERT INTO geodata(code,name) VALUES(%s,%s)"
    print(len(geo_dict))
    with sqlInit.MysqlInit() as mysql_cur:
        for key,value in geo_dict.items():
            mysql_cur.execute(sql,[value,key])

def CreateTable(chatroom = "",type = 4):
    '''
    创建表
    type：1：群聊，4：联系人表，5：地理信息表，其它：单聊或公众号
    '''
    sql_group = "create table "+chatroom+"""(
                    id             int(11)      unsigned   NOT NULL  AUTO_INCREMENT,
                    Type           int(4)       unsigned   NOT NULL,
                    CreateTime     int(11)      unsigned   NOT NULL,
                    SentFrom       varchar(50),
                    Message        LONGTEXT,
                    Des            tinyint(1)              NOT NULL,
                    PRIMARY KEY ( id ))
                    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
    sql_others = "create table "+chatroom+"""(
                    id             int(11)      unsigned   NOT NULL  AUTO_INCREMENT,
                    Type           int(4)       unsigned   NOT NULL,
                    CreateTime     int(11)      unsigned   NOT NULL,
                    Message        LONGTEXT,
                    Des            tinyint(1)              NOT NULL,
                    PRIMARY KEY ( id ))
                    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""

    sql_friends = """create table Friends(
                    id             int(11)      unsigned   NOT NULL  AUTO_INCREMENT,
                    Type           int(4)       unsigned   NOT NULL,
                    EncodeUserName varchar(50),
                    UserName       varchar(50),
                    Remark         varchar(50),
                    Sign           varchar(50),
                    Location       varchar(50),
                    PRIMARY KEY ( id ))
                    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""

    sql_geodata = """create table Geodata(
                    id             int(50)      unsigned   NOT NULL  AUTO_INCREMENT,
                    code           bigint(50)      unsigned   NOT NULL,
                    name           varchar(50),
                    PRIMARY KEY ( id ))
                    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""

    with sqlInit.MysqlInit() as mysql_cur:
        if chatroom == "":
            if type == 4:
                mysql_cur.execute("DROP TABLE IF EXISTS Friends")
                mysql_cur.execute(sql_friends)
            elif type == 5:
                mysql_cur.execute("DROP TABLE IF EXISTS Geodata")
                mysql_cur.execute(sql_geodata)
        else:
            mysql_cur.execute("DROP TABLE IF EXISTS "+chatroom)
            if type == 1:
                mysql_cur.execute(sql_group)
            else:
                mysql_cur.execute(sql_others)

if __name__=='__main__':
    chatrooms_all = []
    chatrooms = []
    with sqlInit.SqliteInit() as sqlite_cur:
        find_chatrooms = "select name from sqlite_master where type='table'"
        result = sqlite_cur.execute(find_chatrooms)
        for row in result:
            if row[0].find("Chat_")!=-1:
                chatrooms_all.append(row[0])
        for chatroom in chatrooms_all:
            rowNum = GetRowNum(chatroom)
            if rowNum>=100: #对于小于100条的聊天记录，暂时不好判断类型，故不进行统计
                chatrooms.append(chatroom)
    
    print("将要添加的聊天数："+str(len(chatrooms)))
    CreateTable(chatroom = "",type=4) #联系人表
    for chatroom in chatrooms:
        print(chatroom)
        if ChatroomType(chatroom) == 1:
            CreateTable(chatroom,1)
            GetGroupData(chatroom)
            InsertFriends(chatroom,1)
        elif ChatroomType(chatroom) == 2:
            CreateTable(chatroom,2)
            GetOthersData(chatroom)
            InsertFriends(chatroom,2)
        else:
            CreateTable(chatroom,3)
            GetOthersData(chatroom)
            InsertFriends(chatroom,3)

    # CreateTable(chatroom = "",type=5) #地理数据表
    # GetGeoData()