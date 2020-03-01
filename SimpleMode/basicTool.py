import re
import sys
import time
import hashlib
import contextlib
import sqlite3

@contextlib.contextmanager
def SqliteInit(db='./data/MM.sqlite'):
    sqlite_conn = sqlite3.connect(db)
    sqlite_cur = sqlite_conn.cursor()
    try:
        yield sqlite_cur
    finally:
        sqlite_conn.commit()
        sqlite_cur.close()
        sqlite_conn.close()

def GetWXID(chatroom):
    '''
    返回微信号
    '''
    wxid_hashed = {}
    hashed_wxid = {}
    raw_data = {}
    with SqliteInit(db='./data/WCDB_Contact.sqlite') as sqlite_cur:
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
def GetName(attr):
    '''
    返回昵称或群名称
    '''
    if "Chat_" in attr:
        WXID = GetWXID(attr)
    else:
        WXID = attr
    name = WXID
    with SqliteInit(db='./data/WCDB_Contact.sqlite') as sqlite_cur:
        try:
            sqlite_cur.execute("select dbContactRemark,dbContactChatRoom from Friend where userName='"+WXID+"'")
            fetchResult = sqlite_cur.fetchall()
            if fetchResult != []:
                if fetchResult[0][0] != None:
                    namelength = bytearray(fetchResult[0][0])[1]
                    name = bytearray(fetchResult[0][0])[2:2+namelength].decode("utf-8")
        except Exception:
            pass
        
    return name

def GetRowNum(chatroom,Des=2,start_time="1970-01-02",end_time=""):
    '''
    返回表的条数
    Des：0：发出，1：接收，2：全部
    start_time，end_time：开始时间和结束时间，不填则为所有时间，如："1970-01-02"
    '''
    rowNum = []
    #选择时间段
    start_time_stamp =  int(time.mktime(time.strptime(start_time, "%Y-%m-%d")))
    if end_time=="":
        end_time_stamp = int(time.time())
    else:
        end_time_stamp = int(time.mktime(time.strptime(end_time, "%Y-%m-%d")))
    
    with SqliteInit() as sqlite_cur:
        if Des == 2:
            sql = "select count(*) from "+chatroom+" where CreateTime>=? and CreateTime<=?"
            fetchResult = sqlite_cur.execute(sql,(str(start_time_stamp),str(end_time_stamp)))
        else:
            sql = "select count(*) from "+chatroom+" where Des=? and CreateTime>=? and CreateTime<=?"
            fetchResult = sqlite_cur.execute(sql,(str(Des),str(start_time_stamp),str(end_time_stamp)))
        for row in fetchResult:
            rowNum = row[0]
    return int(rowNum)
def getAvgLen(chatroom, Des=2, start_time="1970-01-02", end_time=""):
    sql = "SELECT AVG(LENGTH(Message)) FROM "+chatroom+" WHERE Type=1 and Des=? and CreateTime>=? and CreateTime<=?"

    #选择时间段
    start_time_stamp =  int(time.mktime(time.strptime(start_time, "%Y-%m-%d")))
    if end_time=="":
        end_time_stamp = int(time.time())
    else:
        end_time_stamp = int(time.mktime(time.strptime(end_time, "%Y-%m-%d")))
    
    with SqliteInit() as sqlite_cur:
        if Des == 2:
            sqlite_cur.execute(sql,(str(start_time_stamp),str(end_time_stamp)))
        else:
            sqlite_cur.execute(sql,(str(Des),str(start_time_stamp),str(end_time_stamp)))
        result = sqlite_cur.fetchone()
    return result
def ChatroomType(chatroom):
    '''
    返回聊天类型
    返回值：int，1是群组，2是个人，3是公众号
    '''
    #有一些系统账号需要排除
    special_chatroom = ["Chat_c196266f837d14e0b693f961bee37b66","Chat_9e20f478899dc29eb19741386f9343c8","Chat_f609e8364d7d2e09cc229149079efd76","Chat_a971a8ea24a72bb45e64826275fc017f","Chat_03bbbc131de7fa2f8b53f67eff5abc89","Chat_8993f9ceb2f724dc4405db1711c411d5","Chat_30a234cd4741ede59fe93cd9ed1d76d4","Chat_5a7f6c6bdcf1825ccc5fb0007535a694","Chat_418eb42da7dd369038713c81317d6d17","Chat_ffcc9697ac3309e93d80f7773b133f88","Chat_7fe3dd8f21a72028fe706ebf1ed7316c","Chat_95fc41c839f5aac69f77308240b393a0","Chat_a166f8448e52f66e3223716857672479","Chat_dfdfb8fcb82e634b1be33c02bbf70c4c","Chat_a2283195e3dbccc92d6688df4412d6b8"]
    custom_chatroom = ["Chat_2d5de498c19fac1476f42e2428c51e67","Chat_c376b0ef92a23a9abeac229b752398f2"]
    if chatroom in special_chatroom:
        return 3
    elif chatroom in custom_chatroom:
        return 3
    else:
        if "@chatroom" in GetWXID(chatroom): #群组
            return 1
        else:
            if "gh_" == GetWXID(chatroom)[:3]: #公众号
                return 3
            else: #个人
                return 2

def GetGroupData(chatroom,columns=["id","Type","CreateTime","SentFrom","Message","Des"],Desname=2,start_time="1970-01-02",end_time=""):
    '''
    获得单个群聊的消息
    chatroom：聊天数据表
    columns：需要返回的字段，list，如columns=["id","Type","CreateTime","SentFrom","Message","Des"]
    返回值：list，按照columns顺序返回
    Desname：0：发出，1：接收，2：全部
    start_time，end_time：开始时间和结束时间，不填则为所有时间，如："1970-01-02"
    '''
    pattern1 = re.compile('fromusername.*?"(.*?)"')#匹配
    pattern2 = re.compile('"(.*?)"')
    well_tempered_data = []
    counter = 0

    #选择时间段
    start_time_stamp =  int(time.mktime(time.strptime(start_time, "%Y-%m-%d")))
    if end_time=="":
        end_time_stamp = int(time.time())
    else:
        end_time_stamp = int(time.mktime(time.strptime(end_time, "%Y-%m-%d")))

    with SqliteInit() as sqlite_cur:
        if Desname==2:
            sql = "SELECT Type, CreateTime, Message, Des from "+chatroom+" where CreateTime>=? and CreateTime<=?"
            result = sqlite_cur.execute(sql,(str(start_time_stamp),str(end_time_stamp)))
        else:
            sql = "SELECT Type, CreateTime, Message, Des from "+chatroom+" where Des=? and CreateTime>=? and CreateTime<=?"
            result = sqlite_cur.execute(sql,(str(Desname),str(start_time_stamp),str(end_time_stamp)))
        for row in result:
            counter += 1
            Type = row[0]
            CreateTime = row[1]
            Des = row[3]
            # [3,42,50]
            if (Type == 10000) or (Type == 10002) or (Type==1000):
                #系统消息
                if ("撤回" in row[2]) or ("recalled a message" in row[2]):
                    Message = "撤回消息"
                    if(len(pattern2.findall(row[2]))>0):
                        SentFrom = pattern2.findall(row[2])[0]
                    else:
                        SentFrom = "我"
                        Des = 0
                else:
                    SentFrom = "system"
                    Message = row[2].replace("\n","")
            elif Des == 0:
                #我发出的
                SentFrom = "我"
                Message = row[2].replace("\n","")
            elif "<msg>" == row[2].split(":",1)[0][:5]:
                # 视频、链接
                # if Type not in [43,49]:
                #     print(row)
                if len(pattern1.findall(row[2]))>0:
                    SentFrom = pattern1.findall(row[2])[0]
                    Message = row[2].replace("\n","")
                else:
                    SentFrom = "unknown"
                    Message = row[2]
            elif len(pattern1.findall(row[2]))>0:
                # 语音、表情、定位
                # if Type not in [34,47,48]:
                #     print(row)
                SentFrom = pattern1.findall(row[2])[0]
                Message = row[2].replace(SentFrom+":",'').replace("\n","")
            else:
                # 文字、图片、名片、合并转发
                # if Type not in [1,3,42,49]:
                #     print(row)
                SentFrom = row[2].split(":",1)[0]
                try:
                    Message = row[2].split(":",1)[1].replace("\n","")
                except:
                    # 存在丢失发出人的情况
                    SentFrom = "unknown"
                
                
                
            well_tempered_data.append({"id": counter,"Type": Type,"CreateTime": CreateTime,"SentFrom": SentFrom,"Message": Message,"Des": Des})
        final_data = []
        for i in well_tempered_data:
            temp = []
            for j in columns:
                temp.append(i[j])
            final_data.append(temp)
    return final_data
    
def GetOthersData(chatroom,columns=["id","Type","CreateTime","Message","Des"],Desname=2,start_time="1970-01-02",end_time=""):
    '''
    获取单个聊天或公众号的消息
    chatroom：聊天数据表
    columns：需要返回的字段，list，如columns=["id","Type","CreateTime","Message","Des"]
    返回值：list，按照columns顺序返回
    Desname：0：发出，1：接收，2：全部
    start_time，end_time：开始时间和结束时间，不填则为所有时间，如："1970-01-02"
    '''
    pattern1 = re.compile('"(.*?)"')
    well_tempered_data = []
    counter = 0

    #选择时间段
    start_time_stamp =  int(time.mktime(time.strptime(start_time, "%Y-%m-%d")))
    if end_time=="":
        end_time_stamp = int(time.time())
    else:
        end_time_stamp = int(time.mktime(time.strptime(end_time, "%Y-%m-%d")))

    with SqliteInit() as sqlite_cur:
        if Desname==2:
            sql = "SELECT Type, CreateTime, Message, Des from "+chatroom+" where CreateTime>=? and CreateTime<=?"
            result = sqlite_cur.execute(sql,(str(start_time_stamp),str(end_time_stamp)))
        else:
            sql = "SELECT Type, CreateTime, Message, Des from "+chatroom+" where Des=? and CreateTime>=? and CreateTime<=?"
            result = sqlite_cur.execute(sql,(str(Desname),str(start_time_stamp),str(end_time_stamp)))
        for row in result:
            counter += 1
            Type = row[0]
            CreateTime = row[1]
            Des = row[3]
            if (Type == 10000) or (Type == 10002):
                #系统消息
                if ("撤回" in row[2]) or ("recalled a message" in row[2]):
                    Message = "撤回消息"
                    if not (len(pattern1.findall(row[2]))>0):
                        Des = 0
                else:
                    Message = row[2].replace("\n","")
            else:
                Message = row[2].replace("\n","")
            well_tempered_data.append({"id": counter, "Type": Type,"CreateTime": CreateTime,"Message": Message,"Des": Des})
        final_data = []
        for i in well_tempered_data:
            temp = []
            for j in columns:
                temp.append(i[j])
            final_data.append(temp)
    return final_data

def GetChatrooms(typename=0):
    '''
    获取指定类型的聊天
    0：全部，1：群组，2：个人，3：公众号
    '''
    chatrooms_all = []
    chatrooms_group = []
    chatrooms_single = []
    chatrooms_mp = []
    with SqliteInit() as sqlite_cur:
        find_chatrooms = "select name from sqlite_master where type='table'"
        result = sqlite_cur.execute(find_chatrooms)
        for row in result:
            if row[0].find("Chat_")!=-1:
                chatrooms_all.append(row[0])
    for i in chatrooms_all:
        if ChatroomType(i) == 1:
            chatrooms_group.append(i)
        elif ChatroomType(i) == 2:
            chatrooms_single.append(i)
        elif ChatroomType(i) == 3:
            chatrooms_mp.append(i)
    if typename==0:
        return chatrooms_all
    elif typename==1:
        return chatrooms_group
    elif typename==2:
        return chatrooms_single
    elif typename==3:
        return chatrooms_mp

def GetData(chatroom,columns=["Message"],Des=2,start_time="1970-01-02", end_time="", Type=0):
    if Type == 1:
        return GetGroupData(chatroom=chatroom,columns=columns,Desname=Des,start_time=start_time, end_time=end_time)
    elif Type == 2:
        return GetOthersData(chatroom=chatroom,columns=columns,Desname=Des,start_time=start_time, end_time=end_time)
    else:
        if ChatroomType(chatroom) == 1:
            return GetGroupData(chatroom=chatroom,columns=columns,Desname=Des,start_time=start_time, end_time=end_time)
        else:
            return GetOthersData(chatroom=chatroom,columns=columns,Desname=Des,start_time=start_time, end_time=end_time)

if __name__=='__main__':
    pass