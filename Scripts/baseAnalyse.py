import operator
import numpy as np
import sqlInit
import toMySQL
import getChat
import wordcloudAnalyse
import time
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime
from pyecharts import Bar, Line, Grid
def BaseAnalyse():
    '''
    总发出消息
    总接受消息（个人）
    '''
    chatrooms = toMySQL.GetAllChatrooms()
    counter1 = 0
    counter2 = 0
    for i in chatrooms:
        counter1 += toMySQL.GetRowNum(i,db="sqlite",Des=0)
    for i in chatrooms:
        counter2 += toMySQL.GetRowNum(i,db="sqlite",Des=1)
    print(counter1)
    print(counter2)
def RowAnalyse():
    '''
    统计聊天条数分布
    '''
    chatrooms_all = toMySQL.GetAllChatrooms()
    chatrooms = []
    RowNum = {}
    for chatroom in chatrooms_all:
        if toMySQL.ChatroomType(chatroom) == 2:
            chatrooms.append(chatroom)
    print("总聊天数："+str(len(chatrooms)))
    for chatroom in chatrooms:
        RowNum[chatroom]=toMySQL.GetRowNum(chatroom)
    sorted_list = sorted(RowNum.items(), key=operator.itemgetter(1),reverse=True)
    f = open("rows.txt","w+",encoding="utf-8")
    for i in sorted_list:
        f.write(i[0]+","+str(toMySQL.GetWXID(i[0]))+","+str(i[1])+"\n")
    f.close()
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
    bar_bottom = Bar("条数统计-对数坐标", title_top="60%",title_pos="10%")
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

def RowLine():
    '''
    统计聊天条数走势
    '''
    chatrooms = getChat.GetChatrooms(typename=2)
    chatrooms_inuse = []
    for chatroom in chatrooms:
        if toMySQL.GetRowNum(chatroom,"mysql")>=5000:
            chatrooms_inuse.append(chatroom)
    id_time_dict = {}
    for i in range(len(chatrooms_inuse)):
        temp_arr = np.array(getChat.GetData(chatrooms_inuse[i],["id","CreateTime"],2),dtype="int")
        id_time_dict[chatrooms_inuse[i]] = np.append(temp_arr[temp_arr[:,0] % 20 == 1],[temp_arr[-1,:]],axis=0)

    f = plt.figure(figsize=(16, 9))
    plt.grid(True)
    for key,value in id_time_dict.items():
        dateframe_x = [datetime.fromtimestamp(i) for i in value[:,1]]
        x = md.date2num(dateframe_x)
        y = value[:,0]
        ax=plt.gca()
        xfmt = md.DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(xfmt)
        plt.plot(x,y,label=key)
        plt.legend(loc='upper left')
    f.savefig("../../output/RowLine.pdf", bbox_inches='tight')
    plt.show()

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
    
def MostDay():
    '''
    发信息最多的一天
    '''
    # 发出
    chatrooms_group = getChat.GetChatrooms(typename=1)
    chatrooms_single = getChat.GetChatrooms(typename=2)
    chatrooms_all = chatrooms_group + chatrooms_single
    CreateTime_counter = {}
    for i in chatrooms_all:
        for j in getChat.GetData(i,["CreateTime"],Desname=0):
            time_array = time.localtime(j[0])
            CreateTime = time.strftime("%Y-%m-%d", time_array)
            if CreateTime in CreateTime_counter:
                CreateTime_counter[CreateTime] += 1
            else:
                CreateTime_counter[CreateTime] = 1
    sorted_list = sorted(CreateTime_counter.items(), key=operator.itemgetter(1),reverse=True)
    print(sorted_list[0])
    
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
                if i != "Chat_b7ebbe67d8f64c77cda5415f4d749cc6":
                    temp_list.append(row[0])
                if row[1] == 0 and row[2] == 1:
                    my_message.append(row[0])
            if len(temp_list)>0:
                chat_with[i] = temp_list

    with open("../../output/mostday.txt","w+",encoding="utf-8") as f:
        for key,value in chat_with.items():
            for i in value:
                f.write(key+","+i+"\n")
    wordcloudAnalyse.Normal(my_message,filename = "WC_to_MostDay", maxwords = 10, title=sorted_list[0][0])
    

if __name__=='__main__':
    # MostDay()
    # MostGroup()
    # LateChat()
    # RowLine()
    BaseAnalyse()