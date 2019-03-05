import time
import os
from datetime import datetime
from matplotlib.font_manager import FontProperties
from matplotlib import rcParams
import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
import basicTool
import operator
from pyecharts import Bar, configure
# from pyecharts_snapshot.main import make_a_snapshot

def TimeAll(chatrooms,chartname="",filename="time_ana_all",Des=2):
    '''
    chartname：str，图表名
    filename：str，文件名，存储在outputs文件夹下
    Des：0：发出，1：接收，2：全部
    '''
    message_list = []

    for chatroom in chatrooms:
        for row in basicTool.GetData(chatroom=chatroom,columns=["id","CreateTime","Des"]):
            if row[2] == Des:
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
    for row in basicTool.GetData(chatroom=chatroom,columns=["id","CreateTime","Des"]):
        if row[2] == Des:
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

    time_tree_5min = np.zeros((7,24,12))
    # time_tree_10min = np.zeros((7,24,6))
    # time_tree_30min = np.zeros((7,24,2))
    for i in time_list:
        time_tree_5min[i[1],i[2],int(i[3]/5)] = time_tree_5min[i[1],i[2],int(i[3]/5)] + 1
        # time_tree_10min[i[1],i[2],int(i[3]/10)] = time_tree_10min[i[1],i[2],int(i[3]/10)] + 1
        # time_tree_30min[i[1],i[2],int(i[3]/30)] = time_tree_30min[i[1],i[2],int(i[3]/30)] + 1

    days_5min = []
    # days_10min = []
    # days_30min = []
    range_5min = []
    # range_10min = []
    # range_30min = []
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

    bar.render(path=filename+".html")
    # bar.render(path=filename+".pdf")

def RowLine(chatrooms,filename):
    '''
    统计聊天条数走势
    '''
    chatrooms_temp = []
    for chatroom in chatrooms:
        chatrooms_temp.append((chatroom,basicTool.GetRowNum(chatroom)))
    chatrooms_sorted = sorted(chatrooms_temp, key=operator.itemgetter(1),reverse=True)
    if len(chatrooms_sorted) >= 10:
        chatrooms_inuse = [i[0] for i in chatrooms_sorted[:10]]
    else:
        chatrooms_inuse = [i[0] for i in chatrooms_sorted]
    id_time_dict = {}
    for i in range(len(chatrooms_inuse)):
        temp_arr = np.array(basicTool.GetData(chatrooms_inuse[i],["id","CreateTime"]),dtype="int")
        id_time_dict[chatrooms_inuse[i]] = np.append(temp_arr[temp_arr[:,0] % 20 == 1],[temp_arr[-1,:]],axis=0)

    f = plt.figure(figsize=(16, 9))
    plt.grid(True)
    # font0 = FontProperties(fname='./Symbola.ttf')

    # prop = FontProperties(fname="./Symbola.ttf")
    font = {'family' : 'DengXian'}
    plt.rc('font', **font)
    ax=plt.gca()
    for key,value in id_time_dict.items():
        dateframe_x = [datetime.fromtimestamp(i) for i in value[:,1]]
        x = md.date2num(dateframe_x)
        y = value[:,0]
        # ax=plt.gca()
        xfmt = md.DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(xfmt)
        # plt.plot(x,y)
        plt.plot(x,y,label=basicTool.GetName(key))
        # plt.xlabel(basicTool.GetName(key),fontname='symbola')
        plt.legend(loc='upper left')

    plt.show()
    f.savefig(filename+".pdf", bbox_inches='tight')

if __name__=='__main__':
    # chatrooms_group = basicTool.GetChatrooms(typename=1)
    chatrooms_single = basicTool.GetChatrooms(typename=2)
    # chatrooms_all = chatrooms_group + chatrooms_single
    # TimeAll(chatrooms_single, chartname="时频分布-接收（个人）",filename="时频分布-接收（个人）（柱状图）",Des=1)
    # TimeAll(chatrooms_all, chartname="时频分布-发出（全部）",filename="时频分布-发出（全部）（柱状图）",Des=0)
    RowLine(chatrooms_single,filename="总量走势（折线图）")