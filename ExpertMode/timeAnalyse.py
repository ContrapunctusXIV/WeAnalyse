import getChat
import time
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
import toMySQL
from pyecharts import Bar, configure
from pyecharts_snapshot.main import make_a_snapshot

def TimeAll(chartname="",filename="time_ana_all",typename=0,Des=2):
    '''
    chartname：str，图表名
    filename：str，文件名，存储在output文件夹下
    typename：int，0：全部，1：群组，2：个人，3：公众号
    Des：0：发出，1：接收，2：全部
    '''
    chatrooms = getChat.GetChatrooms(typename)
    message_list = []

    for chatroom in chatrooms:
        for row in getChat.GetData(chatroom=chatroom,columns=["id","CreateTime"],Desname=Des):
            message_list.append(row)
    Normal(message_list,chartname=chartname,filename=filename)

def TimeSingle(chatroom,chartname="",filename="time_ana_single",Des=2):
    '''
    chatroom：str，聊天对象
    chartname：str，图表名
    filename：str，文件名，存储在output文件夹下
    Des：0：发出，1：接收，2：全部
    '''
    message_list = []
    for row in getChat.GetData(chatroom=chatroom,columns=["id","CreateTime"],Desname=Des):
        message_list.append(row)
    Normal(message_list,chartname=chartname,filename=filename)
    
def Normal(params,chartname="",filename="time_ana"):
    '''
    params：list，内嵌元组的列表，格式为：[(id,CreateTime)]
    chartname：str，图表名
    filename：str，文件名，存储在output文件夹下
    '''
    time_list = []
    counter = 0
    for row in params:
        counter += 1
        rawtime = datetime.fromtimestamp(row[1])
        hours = rawtime.hour
        minutes = rawtime.minute
        weeks = rawtime.weekday()
        output_data = (row[0],weeks,hours,minutes)
        time_list.append(output_data)
    print("总条数："+str(counter))

    time_tree_5min = np.zeros((7,24,12))
    time_tree_10min = np.zeros((7,24,6))
    time_tree_30min = np.zeros((7,24,2))
    for i in time_list:
        time_tree_5min[i[1],i[2],int(i[3]/5)] = time_tree_5min[i[1],i[2],int(i[3]/5)] + 1
        # time_tree_10min[i[1],i[2],int(i[3]/10)] = time_tree_10min[i[1],i[2],int(i[3]/10)] + 1
        # time_tree_30min[i[1],i[2],int(i[3]/30)] = time_tree_30min[i[1],i[2],int(i[3]/30)] + 1

    days_5min = []
    days_10min = []
    days_30min = []
    range_5min = []
    range_10min = []
    range_30min = []
    week_title = ["星期日","星期一","星期二","星期三","星期四","星期五","星期六"]
    for i in week_title:
        for j in range(24):
            for k in range(12):
                days_5min.append(i+" "+str(j)+":"+str(k*5).zfill(2))
    # for i in week_title:
    #     for j in range(24):
    #         for k in range(6):
    #             days_10min.append(i+" "+str(j)+":"+str(k*10).zfill(2))
    # for i in week_title:
    #     for j in range(24):
    #         for k in range(2):
    #             days_30min.append(i+" "+str(j)+":"+str(k*30).zfill(2))
    
    for i in range(7):
        for j in range(24):
            for k in range(12):
                range_5min.append(time_tree_5min[i,j,k])
    # for i in range(7):
    #     for j in range(24):
    #         for k in range(6):
    #             range_10min.append(time_tree_10min[i,j,k])
    # for i in range(7):
    #     for j in range(24):
    #         for k in range(2):
    #             range_30min.append(time_tree_30min[i,j,k])

    bar = Bar(chartname)

    # bar.add(
    #     "30分钟",
    #     days_30min,
    #     range_30min,
    #     yaxis_name="条数",
    #     is_datazoom_show=True,
    #     datazoom_type="slider",
    #     datazoom_range=[0,100],
    #     is_datazoom_extra_show=True,
    #     datazoom_extra_type="slider",
    #     datazoom_extra_range=[0,100],
    #     is_toolbox_show=False,
    #     is_xaxislabel_align=True
    # )
    # bar.add(
    #     "10分钟",
    #     days_10min,
    #     range_10min,
    #     yaxis_name="条数",
    #     is_datazoom_show=True,
    #     datazoom_type="slider",
    #     datazoom_range=[0,100],
    #     is_datazoom_extra_show=True,
    #     datazoom_extra_type="slider",
    #     datazoom_extra_range=[0,100],
    #     is_toolbox_show=False,
    #     is_xaxislabel_align=True
    # )
    bar.add(
        "",
        days_5min,
        range_5min,
        yaxis_name="条数",
        is_datazoom_show=True,
        datazoom_type="slider",
        datazoom_range=[0,100],
        is_datazoom_extra_show=True,
        datazoom_extra_type="slider",
        datazoom_extra_range=[0,100],
        is_toolbox_show=False,
        is_xaxislabel_align=True
    )

    bar.render(path="../../output/"+filename+".html")
    bar.render(path="../../output/"+filename+".pdf")

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

if __name__=='__main__':
    # TimeAll(chartname="时频分布-接收（不包括群聊）",filename="time_ana_from_all",typename=2,Des=1)
    # TimeAll(chartname="时频分布-发出",filename="time_ana_to_all",typename=0,Des=0)
    # chatroom = "Chat_67183be064c8c3ef11df9bb7a53014c8"
    # TimeSingle(chatroom,chartname=getChat.GetWXID(chatroom),filename="time_ana_temp",Des=1)
    RowLine()