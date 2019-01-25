import operator
import numpy as np
import sqlInit
import toMySQL
import getChat
import time
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime
from pyecharts import Bar, Line, Grid

def RowAnalyse():
    '''
    统计聊天条数分布
    '''
    chatrooms_all = []
    chatrooms = []
    RowNum = {}
    with sqlInit.SqliteInit() as sqlite_cur:
        find_chatrooms = "select name from sqlite_master where type='table'"
        result = sqlite_cur.execute(find_chatrooms)
        for row in result:
            if row[0].find("Chat_")!=-1:
                chatrooms_all.append(row[0])
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
        # is_xaxis_show=0
    )
    bar_bottom = Bar("条数统计-对数坐标", title_top="60%",title_pos="10%")
    bar_bottom.add(
        "",
        x_axis,
        y_axis,
        yaxis_name="条数",
        yaxis_type='log',
        is_xaxislabel_align=True
        # is_xaxis_show=0
    )
    grid = Grid(width=1920, height=1080)
    grid.add(bar_top, grid_bottom="60%")
    grid.add(bar_bottom, grid_top="60%")
    grid.render(path="../../output/row_analyse.html")
    grid.render(path="../../output/row_analyse.pdf")

def TopAnimation():
    chatrooms = getChat.GetChatrooms(typename=1)
    chatrooms.append(getChat.GetChatrooms(typename=2))
    for i in chatrooms:
        getChat.GetData(i,["Type","Message"],0)
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
    
RowLine()