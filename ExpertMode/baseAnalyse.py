import operator
import re
import numpy as np
import sqlInit
import toMySQL
import getChat
import wordcloudAnalyse
import time
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime
from pyecharts import Bar, Line, Grid, Pie

def BaseAnalyse():
    '''
    个人总数
    群聊总数
    总发出消息（个人+群组）
    总发出消息（个人）
    总接收消息（个人+群组）
    总接收消息（个人）
    总撤回消息（自己）
    总撤回消息（个人）
    '''
    counter1 = 0
    counter2 = 0
    counter3 = 0
    counter4 = 0
    recall_to = {}
    recall_from = {}
    recall_to_rate = {}
    recall_from_rate = {}
    chatrooms_group = getChat.GetChatrooms(typename=1)
    chatrooms_single = getChat.GetChatrooms(typename=2)
    print("个人总数："+str(len(chatrooms_single)))
    print("群聊总数："+str(len(chatrooms_group)))
    chatrooms_all = chatrooms_group + chatrooms_single
    message_length_to = []
    message_length_from = []
    for chatroom in chatrooms_single:
        sql3 = "SELECT AVG(CHAR_LENGTH(Message)) FROM "+chatroom+" WHERE Type=1 and Des=0"
        sql4 = "SELECT AVG(CHAR_LENGTH(Message)) FROM "+chatroom+" WHERE Type=1 and Des=1"
        with sqlInit.MysqlInit() as mysql_cur:
            mysql_cur.execute(sql3)
            result = mysql_cur.fetchone()
            if result[0]!=None:
                message_length_to.append(float(result[0]))
        with sqlInit.MysqlInit() as mysql_cur:
            mysql_cur.execute(sql4)
            result = mysql_cur.fetchone()
            if result[0]!=None:
                message_length_from.append(float(result[0]))
    print("平均发出消息长度为："+"%.2f"%np.mean(message_length_to))
    print("平均接收消息长度为："+"%.2f"%np.mean(message_length_from))
    for chatroom in chatrooms_all:
        counter1 += getChat.GetRowNum(chatroom,Des=0)
        counter3 += getChat.GetRowNum(chatroom,Des=1)
    for chatroom in chatrooms_single:
        sql1 = "select count(*) from "+chatroom+" where Message='撤回消息' and Des=0"
        sql2 = "select count(*) from "+chatroom+" where Message='撤回消息' and Des=1"

        counter2 += getChat.GetRowNum(chatroom,Des=0)
        counter4 += getChat.GetRowNum(chatroom,Des=1)
        with sqlInit.MysqlInit() as mysql_cur:
            mysql_cur.execute(sql1)
            result = mysql_cur.fetchone()
            if result != None:
                if result[0] != 0:
                    rownum = getChat.GetRowNum(chatroom)
                    recall_to[chatroom] = result[0]
                    if rownum>100:
                        recall_rate = 1000*result[0]/rownum
                        recall_to_rate[chatroom] = round(recall_rate, 2)
        with sqlInit.MysqlInit() as mysql_cur:
            mysql_cur.execute(sql2)
            result = mysql_cur.fetchone()
            if result != None:
                if result[0] != 0:
                    rownum = getChat.GetRowNum(chatroom)
                    recall_from[chatroom] = result[0]
                    if rownum>100:
                        recall_rate = 1000*result[0]/rownum
                        recall_from_rate[chatroom] = round(recall_rate, 2)
    recall_to_sum = sum(list(recall_to.values()))
    recall_from_sum = sum(list(recall_from.values()))
    sorted_recall_to = sorted(recall_to_rate.items(), key=operator.itemgetter(1),reverse=True)
    sorted_recall_from = sorted(recall_from_rate.items(), key=operator.itemgetter(1),reverse=True)
    print(sorted_recall_to)
    print(sorted_recall_from)
    print("总共发出："+str(counter1))
    print("总共发出（个人）："+str(counter2))
    print("总共接收："+str(counter3))
    print("总共接收（个人）："+str(counter4))
    print("我总共撤回："+str(recall_to_sum))
    print("总共被撤回："+str(recall_from_sum))
def MostEmoji():
    chatrooms_group = getChat.GetChatrooms(typename=1)
    chatrooms_single = getChat.GetChatrooms(typename=2)
    chatrooms_all = chatrooms_group + chatrooms_single
    pattern = re.compile(' md5="(.*?)"')
    emoji_dict_to = {}
    emoji_dict_from = {}
    for chatroom in chatrooms_all:
        sql = "SELECT Message,CreateTime as num FROM "+chatroom+" WHERE Type=47 and Des=0"
        with sqlInit.MysqlInit() as mysql_cur:
            mysql_cur.execute(sql)
            result = mysql_cur.fetchall()
            for row in result:
                emoji_md5 = pattern.findall(row[0])[0]
                if len(emoji_md5)>0:
                    if emoji_md5 in emoji_dict_to.keys():
                        emoji_dict_to[emoji_md5][0] += 1
                    else:
                        emoji_dict_to[emoji_md5] = [1,chatroom,row[1]]
    sorted_list_to = sorted(emoji_dict_to.items(), key=lambda x: x[1][0],reverse=True)
    print(sorted_list_to)
    for chatroom in chatrooms_single:
        sql = "SELECT Message,CreateTime as num FROM "+chatroom+" WHERE Type=47 and Des=1"
        with sqlInit.MysqlInit() as mysql_cur:
            mysql_cur.execute(sql)
            result = mysql_cur.fetchall()
            for row in result:
                emoji_md5 = pattern.findall(row[0])[0]
                if len(emoji_md5)>0:
                    if emoji_md5 in emoji_dict_from.keys():
                        emoji_dict_from[emoji_md5][0] += 1
                    else:
                        emoji_dict_from[emoji_md5] = [1,chatroom,row[1]]
    sorted_list_from = sorted(emoji_dict_from.items(), key=lambda x: x[1][0],reverse=True)
    print(sorted_list_from)
def TypeAnalyse():
    chatrooms_single = getChat.GetChatrooms(typename=2)
    single_type_counter_to = {}
    single_type_counter_from = {}
    for i in chatrooms_single:
        sql1 = "SELECT Type,count(*) as num FROM "+i+" WHERE Des=0 GROUP BY Type"
        sql2 = "SELECT Type,count(*) as num FROM "+i+" WHERE Des=1 GROUP BY Type"
        with sqlInit.MysqlInit() as mysql_cur:
            mysql_cur.execute(sql1)
            result = mysql_cur.fetchall()
            for j in result:
                if j[0] in single_type_counter_to.keys():
                    single_type_counter_to[j[0]] += j[1]
                else:
                    single_type_counter_to[j[0]] = j[1]
        with sqlInit.MysqlInit() as mysql_cur:
            mysql_cur.execute(sql2)
            result = mysql_cur.fetchall()
            for j in result:
                if j[0] in single_type_counter_from.keys():
                    single_type_counter_from[j[0]] += j[1]
                else:
                    single_type_counter_from[j[0]] = j[1]

    if 10002 in single_type_counter_to.keys():
        if not 10000 in single_type_counter_to.keys():
            single_type_counter_to[10000] = single_type_counter_to[10002]
        else:
            single_type_counter_to[10000] += single_type_counter_to[10002]
            del single_type_counter_to[10002]
    if 10002 in single_type_counter_from.keys():
        if not 10000 in single_type_counter_from.keys():
            single_type_counter_from[10000] = single_type_counter_from[10002]
        else:
            single_type_counter_from[10000] += single_type_counter_from[10002]
            del single_type_counter_from[10002]

    if 62 in single_type_counter_to.keys():
        if not 43 in single_type_counter_to.keys():
            single_type_counter_to[43] = single_type_counter_to[62]
        else:
            single_type_counter_to[43] += single_type_counter_to[62]
            del single_type_counter_to[62]
    if 62 in single_type_counter_from.keys():
        if not 43 in single_type_counter_from.keys():
            single_type_counter_from[43] = single_type_counter_from[62]
        else:
            single_type_counter_from[43] += single_type_counter_from[62]
            del single_type_counter_from[62]
    define_dict = {"文字":1,"图片":3,"语音":34,"名片":42,"视频":43,"表情":47,"定位":48,"链接":49,"微信电话":50,"系统消息":10000}
    attr = ["文字", "表情", "图片", "视频", "语音", "名片", "定位", "链接", "微信电话", "系统消息"]
    v1 = [single_type_counter_to[define_dict[i]] for i in attr]
    v2 = [single_type_counter_from[define_dict[i]] for i in attr]
    pie = Pie("", width=1000,height=400)
    pie.add(
        "发出",
        attr,
        v1,
        center=[25, 50],
        is_random=True,
        radius=[30, 75],
        is_legend_show=True,
        is_label_show=True,
        legend_top="bottom"
    )
    pie.add(
        "接收",
        attr,
        v2,
        center=[75, 50],
        is_random=True,
        radius=[30, 75],
        is_legend_show=True,
        is_label_show=True,
        legend_top="bottom"
    )
    pie.render(path="../../output/type_ana.html")
    pie.render(path="../../output/type_ana.pdf")

def RowAnalyse():
    '''
    统计聊天条数分布
    个人
    '''
    chatrooms = getChat.GetChatrooms(typename=2)
    RowNum = {}

    print("总聊天数："+str(len(chatrooms)))
    for chatroom in chatrooms:
        RowNum[chatroom]=toMySQL.GetRowNum(chatroom)
    # sorted_list = sorted(RowNum.items(), key=operator.itemgetter(1),reverse=True)
    # f = open("../../rows.txt","w+",encoding="utf-8")
    # for i in sorted_list:
    #     f.write(i[0]+","+str(getChat.GetWXID(i[0]))+","+str(i[1])+"\n")
    # f.close()
    data = sorted(RowNum.values(),reverse=True)
    x_axis = list(range(len(chatrooms)))
    y_axis = data
    bar_top = Bar("条数统计",title_pos="10%")
    bar_top.add(
        "",
        x_axis,
        y_axis,
        yaxis_name="条数",
        is_xaxislabel_align=True
    )
    bar_bottom = Bar("条数统计-对数坐标", title_top="55%",title_pos="10%")
    bar_bottom.add(
        "",
        x_axis,
        y_axis,
        yaxis_name="条数",
        yaxis_type='log',
        is_xaxislabel_align=True
    )
    grid = Grid(width=1920, height=1080)
    grid.add(bar_top, grid_bottom="60%")
    grid.add(bar_bottom, grid_top="60%")
    grid.render(path="../../output/row_analyse.html")
    grid.render(path="../../output/row_analyse.pdf")

def LateChat():
    '''
    返回深夜的聊天内容
    '''
    # 发出
    chatrooms_single = getChat.GetChatrooms(typename=2)
    my_message = []
    with open("../../output/latechat.txt","w+",encoding="utf-8") as f:
        for i in chatrooms_single:
            for j in getChat.GetData(i,["CreateTime","Message","Des","Type"],Desname=2):
                time_array = time.localtime(j[0])
                if 1<=time_array[3]<=6:
                    CreateTime = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
                    Message = j[1]
                    if j[2] == 0 and j[3] == 1:
                        my_message.append(Message)
                    f.write(i+","+str(j[2])+","+CreateTime+","+Message+"\n")
    wordcloudAnalyse.Normal(my_message,filename = "WC_to_LateChat", maxwords = 30, title="")
    
def MostGroup():
    '''
    发信息最多的群聊
    '''
    chatrooms_group = getChat.GetChatrooms(typename=1)
    group_row_dict = {}
    for i in chatrooms_group:
        group_row_dict[i] = toMySQL.GetRowNum(i,db="mysql",Des=0)
    sorted_list = sorted(group_row_dict.items(), key=operator.itemgetter(1),reverse=True)
    print(sorted_list[0])
    message_list = []
    for row in getChat.GetData(sorted_list[0][0],["Message","Type"],Desname=0):
        if row[1]==1:
            message_list.append(row[0])
    wordcloudAnalyse.Normal(message_list,filename = "WC_to_MostGroup", maxwords = 50, title="")
    
def MostDay(filename = "mostday_to",Des = 0):
    '''
    发/收信息最多的一天
    '''
    chatrooms_group = getChat.GetChatrooms(typename=1)
    chatrooms_single = getChat.GetChatrooms(typename=2)
    chatrooms_all = chatrooms_group + chatrooms_single
    CreateTime_counter = {}
    for i in chatrooms_single:
        for j in getChat.GetData(i,["CreateTime"],Desname=Des):
            time_array = time.localtime(j[0])
            CreateTime = time.strftime("%Y-%m-%d", time_array)
            if CreateTime in CreateTime_counter:
                CreateTime_counter[CreateTime] += 1
            else:
                CreateTime_counter[CreateTime] = 1
    sorted_list = sorted(CreateTime_counter.items(), key=operator.itemgetter(1),reverse=True)
    
    format_time1 = sorted_list[0][0]+' 00:00:00'
    format_time2 = sorted_list[0][0]+' 23:59:59'
    time1 = int(time.mktime(time.strptime(format_time1, "%Y-%m-%d %H:%M:%S")))
    time2 = int(time.mktime(time.strptime(format_time2, "%Y-%m-%d %H:%M:%S")))
    chat_with = {}
    my_message = []

    with sqlInit.MysqlInit() as mysql_cur:
        for i in chatrooms_all:
            temp_list = []
            sql = "select Message,Des,Type from "+i+" where CreateTime>="+str(time1)+" and CreateTime<="+str(time2)
            mysql_cur.execute(sql)
            result = mysql_cur.fetchall()
            for row in result:
                if i != "Chat_b7ebbe67d8f64c77cda5415f4d749cc6" and row[1] == Des and row[2]==1:
                    temp_list.append(row[0])
                if row[1] == Des and row[2] == 1:
                    my_message.append(row[0])
            if len(temp_list)>0:
                chat_with[i] = temp_list

    with open("../../output/"+filename+".txt","w+",encoding="utf-8") as f:
        for key,value in chat_with.items():
            for i in value:
                f.write(key+","+i+"\n")

    # wordcloudAnalyse.Normal(my_message,filename = "WC_to_MostDay", maxwords = 10, title=sorted_list[0][0])

if __name__=='__main__':
    # BaseAnalyse()
    # MostEmoji()
    # TypeAnalyse()
    # RowAnalyse()
    # LateChat()
    # MostGroup()
    MostDay(filename="Mostday_from",Des=1)