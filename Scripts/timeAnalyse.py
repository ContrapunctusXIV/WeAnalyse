import getChat
import time
import datetime
import numpy as np
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
        rawtime = datetime.datetime.fromtimestamp(row[1])
        hours = rawtime.hour
        minutes = rawtime.minute
        weeks = rawtime.weekday()
        output_data = (row[0],weeks,hours,minutes)
        time_list.append(output_data)
    print("总条数："+str(counter))

    time_tree = np.zeros((7,24,12))
    for i in time_list:
        time_tree[i[1],i[2],int(i[3]/5)] = time_tree[i[1],i[2],int(i[3]/5)] + 1

    days = []
    week_title = ["星期日","星期一","星期二","星期三","星期四","星期五","星期六"]
    for i in week_title:
        for j in range(24):
            for k in range(12):
                days.append(i+" "+str(j)+":"+str(k*5).zfill(2))
    days_v1 = []
    for i in range(7):
        for j in range(24):
            for k in range(12):
                days_v1.append(time_tree[i,j,k])
    bar = Bar(chartname)
    bar.add(
        "",
        days,
        days_v1,
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
    pass
if __name__=='__main__':
    # TimeAll(chartname="时频分布-接收（不包括群聊）",filename="time_ana_from_all",typename=2,Des=1)
    # TimeAll(chartname="时频分布-发出",filename="time_ana_to_all",typename=0,Des=0)
    # chatroom = "Chat_67183be064c8c3ef11df9bb7a53014c8"
    # TimeSingle(chatroom,chartname=getChat.GetWXIDlocal(chatroom),filename="time_ana_temp",Des=1)
    pass