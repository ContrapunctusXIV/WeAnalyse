import operator
import time
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
import basicTool
from pyecharts import HeatMap, Grid
# from pyecharts_snapshot.main import make_a_snapshot

def UsageAll(chatrooms,chartname="",filename="usage_ana_all",Des=0,start_time="1970-01-02", end_time=""):
    '''
    chartname：str，图表名
    filename：str，文件名，存储在output文件夹下
    typename：int，0：全部，1：群组，2：个人，3：公众号
    Des：0：发出，1：接收，2：全部
    '''
    CreateTime_counter = {}
    for i in chatrooms:
        for j in basicTool.GetData(i,["CreateTime"],Des=Des,start_time=start_time, end_time=end_time):
            time_array = time.localtime(j[0])
            CreateTime = time.strftime("%Y-%m-%d", time_array)
            if CreateTime in CreateTime_counter:
                CreateTime_counter[CreateTime] += 1
            else:
                CreateTime_counter[CreateTime] = 1
    sorted_list = sorted(CreateTime_counter.items(), key=operator.itemgetter(0),reverse=False)
    Normal(sorted_list,chartname=chartname,filename=filename)

def UsageSingle(chatroom,chartname="",filename="usage_ana_single",Des=2,start_time="1970-01-02", end_time=""):
    '''
    chatroom：str，聊天对象
    chartname：str，图表名
    filename：str，文件名，存储在output文件夹下
    Des：0：发出，1：接收，2：全部
    '''
    CreateTime_counter = {}
    for i in basicTool.GetData(chatroom=chatroom,columns=["CreateTime"],Des=Des,start_time=start_time, end_time=end_time):
        time_array = time.localtime(i[0])
        CreateTime = time.strftime("%Y-%m-%d", time_array)
        if CreateTime in CreateTime_counter:
            CreateTime_counter[CreateTime] += 1
        else:
            CreateTime_counter[CreateTime] = 1
    sorted_list = sorted(CreateTime_counter.items(), key=operator.itemgetter(0),reverse=False)
    Normal(sorted_list,chartname=chartname,filename=filename)
    
def Normal(params,chartname="",filename="usage_ana"):
    '''
    params：list，内嵌元组或列表的列表，格式为：[("2019-2-8",32)]
    chartname：str，图表名
    filename：str，文件名，存储在output文件夹下
    '''
    day_counter = []
    for i in params:
        day_counter.append(i[1])
    heatmap = HeatMap(chartname, "", width=1500)

    heatmap.add(
        "",
        params,
        is_label_show=True,
        tooltip_formatter='{c}',
        is_calendar_heatmap=True,
        visual_text_color="#000",
        visual_range_text=["", ""],
        visual_range=[1, int(max(day_counter))],
        calendar_cell_size=["auto", 30],
        is_visualmap=True,
        # calendar_date_range="2015",
        calendar_date_range=[params[0][0], params[-1][0]],
        visual_orient="horizontal",
        visual_pos="center",
        visual_top="80%",
        is_piecewise=True,
    )

    heatmap.render(path=filename+".html")
    # heatmap.render(path=filename+".pdf")

def Lonelydude(chatrooms,filename="lonelydude",start_time="1970-01-02", end_time=""):
    '''
    用于获取发出但没有收到回复的消息和收到但没有回复对方的消息
    filename：str，文件名，存储在output文件夹下
    typename：int，0：全部，1：群组，2：个人，3：公众号
    '''
    CreateTime_counter_to = {}
    CreateTime_counter_from = {}
    for i in chatrooms:
        for j in basicTool.GetData(i,["CreateTime","Des"],start_time=start_time, end_time=end_time):
            time_array = time.localtime(j[0])
            CreateTime = time.strftime("%Y-%m-%d", time_array)
            if j[1] == 0:
                if CreateTime in CreateTime_counter_to:
                    CreateTime_counter_to[CreateTime] += 1
                else:
                    CreateTime_counter_to[CreateTime] = 1
            elif j[1] == 1:
                if CreateTime in CreateTime_counter_from:
                    CreateTime_counter_from[CreateTime] += 1
                else:
                    CreateTime_counter_from[CreateTime] = 1
    no_response = []
    no_reply = []
    no_response = [i for i in CreateTime_counter_to.keys() if i not in CreateTime_counter_from.keys()]
    no_reply = [i for i in CreateTime_counter_from.keys() if i not in CreateTime_counter_to.keys()]

    no_response_with = {}
    for i in no_response:
        format_time1 = i+' 00:00:00'
        format_time2 = i+' 23:59:59'
        time1 = int(time.mktime(time.strptime(format_time1, "%Y-%m-%d %H:%M:%S")))
        time2 = int(time.mktime(time.strptime(format_time2, "%Y-%m-%d %H:%M:%S")))
        with basicTool.SqliteInit() as mysql_cur:
            for j in chatrooms:
                temp_list = []
                sql = "select Message from "+j+" where CreateTime>="+str(time1)+" and CreateTime<="+str(time2)+" and Des=0"
                mysql_cur.execute(sql)
                result = mysql_cur.fetchall()
                for row in result:
                    temp_list.append(row[0])
                if len(temp_list)>0:
                    no_response_with[j] = temp_list

    no_reply_with = {}
    for i in no_reply:
        format_time1 = i+' 00:00:00'
        format_time2 = i+' 23:59:59'
        time1 = int(time.mktime(time.strptime(format_time1, "%Y-%m-%d %H:%M:%S")))
        time2 = int(time.mktime(time.strptime(format_time2, "%Y-%m-%d %H:%M:%S")))
        with basicTool.SqliteInit() as mysql_cur:
            for j in chatrooms:
                temp_list = []
                sql = "select Message from "+j+" where CreateTime>="+str(time1)+" and CreateTime<="+str(time2)+" and Des=1"
                mysql_cur.execute(sql)
                result = mysql_cur.fetchall()
                for row in result:
                    temp_list.append(row[0])
                if len(temp_list)>0:
                    no_reply_with[j] = temp_list

    with open(filename+".txt","w+",encoding="utf-8") as f:
        f.write("未收到回复："+",".join(no_response)+"\n")
        f.write("未回复对方："+",".join(no_reply)+"\n")
        f.write("未获得回复：\n")
        for key,value in no_response_with.items():
            for i in value:
                f.write(basicTool.GetName(key)+": "+i+"\n")
        f.write("\n未回复对方：\n")
        for key,value in no_reply_with.items():
            for i in value:
                f.write(basicTool.GetName(key)+": "+i+"\n")
if __name__=='__main__':
    # chatrooms_group = basicTool.GetChatrooms(typename=1)
    # chatrooms_single = basicTool.GetChatrooms(typename=2)
    # chatrooms_all = chatrooms_group + chatrooms_single
    # Lonelydude(chatrooms_single,filename="未回复的消息")
    # UsageAll(chatrooms_all,chartname="使用日历-发出（全部）",filename="使用日历-发出（全部）（日历图）",Des=0)
    # UsageAll(chatrooms_single, chartname="使用日历-发出（个人）",filename="使用日历-发出（个人）（日历图）",Des=0)
    # UsageAll(chatrooms_single, chartname="使用日历-接收（个人）",filename="使用日历-接收（个人）（日历图）",Des=1)
    UsageSingle("Chat_67183be064c8c3ef11df9bb7a53014c8", chartname="",filename="thedeadgroup_usage",Des=2)