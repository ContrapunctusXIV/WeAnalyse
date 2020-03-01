import operator
import re
import numpy as np
import basicTool
import wordcloudAnalyse
import time
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime
from pyecharts import Bar, Line, Grid, Pie

def BaseData(chatrooms_group, chatrooms_single,filename="basic_ana", start_time="1970-01-02", end_time=""):
    '''
    好友总数
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
    counter5 = 0
    counter6 = 0
    chatrooms_all = chatrooms_group + chatrooms_single
    message_length_to = []
    message_length_from = []
    for chatroom in chatrooms_single:
        result = basicTool.getAvgLen(chatroom,Des=0,start_time=start_time,end_time=end_time)
        if result[0]!=None:
            message_length_to.append(float(result[0]))

        result = basicTool.getAvgLen(chatroom,Des=1,start_time=start_time,end_time=end_time)
        if result[0]!=None:
            message_length_from.append(float(result[0]))

    for chatroom in chatrooms_all:
        counter1 += basicTool.GetRowNum(chatroom,Des=0,start_time=start_time,end_time=end_time)
        counter3 += basicTool.GetRowNum(chatroom,Des=1,start_time=start_time,end_time=end_time)
    for chatroom in chatrooms_single:
        counter2 += basicTool.GetRowNum(chatroom,Des=0,start_time=start_time,end_time=end_time)
        counter4 += basicTool.GetRowNum(chatroom,Des=1,start_time=start_time,end_time=end_time)
    for chatroom in chatrooms_group:
        counter5 += basicTool.GetRowNum(chatroom,Des=0,start_time=start_time,end_time=end_time)
        counter6 += basicTool.GetRowNum(chatroom,Des=1,start_time=start_time,end_time=end_time)
    recall_to_sum = {"撤回消息": 0}
    recall_from_sum = {"撤回消息": 0}
    for chatroom in chatrooms_single:
        for i in basicTool.GetData(chatroom,columns=["Message","Des"],start_time=start_time,end_time=end_time,Type=2):
            if i[0] == "撤回消息":
                if i[1] == 0:
                    recall_to_sum["撤回消息"] += 1
                else:
                    recall_from_sum["撤回消息"] += 1
    with open(filename+".txt","w+",encoding="utf-8") as f:
        f.write("好友总数："+str(len(chatrooms_single))+"个\n")
        f.write("群聊总数："+str(len(chatrooms_group))+"个\n")
        f.write("总共发出："+str(counter1)+"条\n")
        f.write("总共发出（好友）："+str(counter2)+"条\n")
        f.write("总共发出（群聊）："+str(counter5)+"条\n")
        f.write("总共接收："+str(counter3)+"条\n")
        f.write("总共接收（好友）："+str(counter4)+"条\n")
        f.write("总共接收（群聊）："+str(counter6)+"条\n")
        f.write("平均发出消息长度为（好友）："+"%.2f"%np.mean(message_length_to)+"个字\n")
        f.write("平均接收消息长度为（好友）："+"%.2f"%np.mean(message_length_from)+"个字\n")
        f.write("我总共撤回（好友）："+str(recall_to_sum["撤回消息"])+"次\n")
        f.write("总共被撤回（好友）："+str(recall_from_sum["撤回消息"])+"次\n")
    

def MostEmoji(chatrooms_group, chatrooms_single, filename="emoji_ranking", start_time="1970-01-02", end_time=""):
    chatrooms_all = chatrooms_group + chatrooms_single
    pattern = re.compile(' md5="(.*?)"')
    emoji_dict_to = {}
    emoji_dict_from = {}

    #选择时间段
    start_time_stamp =  int(time.mktime(time.strptime(start_time, "%Y-%m-%d")))
    if end_time=="":
        end_time_stamp = int(time.time())
    else:
        end_time_stamp = int(time.mktime(time.strptime(end_time, "%Y-%m-%d")))
    
    for chatroom in chatrooms_all:
        sql = "SELECT Message,CreateTime as num FROM "+chatroom+" WHERE Type=47 and Des=0 and CreateTime>=? and CreateTime<=?"
        Name = basicTool.GetName(chatroom)
        with basicTool.SqliteInit() as sqlite_cur:
            sqlite_cur.execute(sql,(str(start_time_stamp),str(end_time_stamp)))
            result = sqlite_cur.fetchall()
            for row in result:
                emoji_md5 = pattern.findall(row[0])[0]
                if len(emoji_md5)>0:
                    if emoji_md5 in emoji_dict_to.keys():
                        emoji_dict_to[emoji_md5][0] += 1
                    else:
                        emoji_dict_to[emoji_md5] = [1,Name,row[1]]
                    if (Name != "") and (emoji_dict_to[emoji_md5][1] == ""):
                        emoji_dict_to[emoji_md5][1] = Name
                        emoji_dict_to[emoji_md5][2] = row[1]

    sorted_list_to = sorted(emoji_dict_to.items(), key=lambda x: x[1][0],reverse=True)
    
    for chatroom in chatrooms_single:
        sql = "SELECT Message,CreateTime as num FROM "+chatroom+" WHERE Type=47 and Des=1 and CreateTime>=? and CreateTime<=?"
        Name = basicTool.GetName(chatroom)
        with basicTool.SqliteInit() as sqlite_cur:
            sqlite_cur.execute(sql,(str(start_time_stamp),str(end_time_stamp)))
            result = sqlite_cur.fetchall()
            for row in result:
                emoji_md5 = pattern.findall(row[0])[0]
                if len(emoji_md5)>0:
                    if emoji_md5 in emoji_dict_from.keys():
                        emoji_dict_from[emoji_md5][0] += 1
                    else:
                        emoji_dict_from[emoji_md5] = [1,Name,row[1]]
                    if (Name != "") and (emoji_dict_from[emoji_md5][1] == ""):
                        emoji_dict_from[emoji_md5][1] = Name
                        emoji_dict_from[emoji_md5][2] = row[1]
    sorted_list_from = sorted(emoji_dict_from.items(), key=lambda x: x[1][0],reverse=True)
    with open(filename+".txt","w+",encoding="utf-8") as f:
        f.write("发出最多的表情包："+sorted_list_to[0][0]+"\n")
        f.write("共"+str(sorted_list_to[0][1][0])+"次"+"\n")
        f.write("聊天记录定位：微信名："+sorted_list_to[0][1][1]+"，时间："+str(datetime.fromtimestamp(sorted_list_to[0][1][2]))+"\n\n")

        f.write("接收最多的表情包："+sorted_list_from[0][0]+"\n")
        f.write("共"+str(sorted_list_from[0][1][0])+"次"+"\n")
        f.write("聊天记录定位：微信名："+sorted_list_from[0][1][1]+"，时间："+str(datetime.fromtimestamp(sorted_list_from[0][1][2]))+"\n")
    

def TypeAnalyse(chatrooms_single, filename="Type_ana", start_time="1970-01-02", end_time=""):
    single_type_counter_to = {1:0, 3:0, 34:0, 42:0, 43:0, 47:0, 48:0, 49:0, 50:0, 10000:0}
    single_type_counter_from = {1:0, 3:0, 34:0, 42:0, 43:0, 47:0, 48:0, 49:0, 50:0, 10000:0}
    for i in chatrooms_single:
        for j in basicTool.GetData(i,["Type","Des"],start_time=start_time,end_time=end_time,Type=2):
            if j[1] == 0:
                if j[0] in single_type_counter_to.keys():
                    single_type_counter_to[j[0]] += 1
                else:
                    single_type_counter_to[j[0]] = 1
            else:
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
    pie.render(path=filename+".html")
    # pie.render(path=filename+".pdf")

def RowAnalyse(chatrooms_single,filename="Row_ana", start_time="1970-01-02", end_time=""):
    '''
    统计聊天条数分布
    个人
    '''
    chatrooms = chatrooms_single
    RowNum = {}
    for chatroom in chatrooms:
        RowNum[chatroom]=basicTool.GetRowNum(chatroom,start_time=start_time,end_time=end_time)
    # sorted_list = sorted(RowNum.items(), key=operator.itemgetter(1),reverse=True)
    # f = open("../../rows.txt","w+",encoding="utf-8")
    # for i in sorted_list:
    #     f.write(i[0]+","+str(basicTool.GetWXID(i[0]))+","+str(i[1])+"\n")
    # f.close()
    sorted_list = sorted(RowNum.items(), key=operator.itemgetter(1),reverse=True)
    
    #x_axis = list(range(len(sorted_list))) #不显示姓名时用这个
    x_axis = [str(i+1)+","+basicTool.GetName(sorted_list[i][0]) for i in range(len(sorted_list))]
    y_axis = [i[1] for i in sorted_list]
    bar_top = Bar("条数统计",title_pos="10%")
    def label_formatter(params):
        return params.split(",")[0]
    bar_top.add(
        "",
        x_axis,
        y_axis,
        # xaxis_interval=0,
        # xaxis_rotate = 30,
        xaxis_formatter = label_formatter,
        yaxis_name="条数",
        is_xaxislabel_align=True,
        is_datazoom_show=True,
        datazoom_range=[0,100]
    )

    # bar_bottom = Bar("条数统计-对数坐标", title_top="55%",title_pos="10%")
    # bar_bottom.add(
    #     "",
    #     x_axis,
    #     y_axis,
    #     # xaxis_interval=0,
    #     # xaxis_rotate = 30,
    #     xaxis_formatter = label_formatter,
    #     yaxis_name="条数",
    #     yaxis_type='log',
    #     is_xaxislabel_align=True
    # )
    # grid = Grid(width=1920, height=1080)
    # grid.add(bar_top, grid_bottom="60%")
    # grid.add(bar_bottom, grid_top="60%")
    bar_top.render(path=filename+".html")
    # grid.render(path=filename+".pdf")

def TimeSlice(chatrooms_single,start=1,end=6,filename="Time_slice", start_time="1970-01-02", end_time=""):
    '''
    返回一定时间段的所有聊天内容
    start：开始时间
    end：截止时间
    '''
    # 发出
    my_message = []
    with open(filename+".txt","w+",encoding="utf-8") as f:
        for i in chatrooms_single:
            for j in basicTool.GetData(i,["CreateTime","Message","Des","Type"],start_time=start_time,end_time=end_time,Type=2):
                time_array = time.localtime(j[0])
                if start<=time_array[3]<=end:
                    CreateTime = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
                    Message = j[1]
                    if j[2] == 0 and j[3] == 1:
                        my_message.append(Message)
                    f.write(basicTool.GetName(i)+","+str(j[2])+","+CreateTime+","+Message+"\n")
    
def MostDay(chatrooms_group,chatrooms_single,filename = "mostday_to",Des = 0, start_time="1970-01-02", end_time=""):
    '''
    发/收信息最多的一天
    '''
    chatrooms_all = chatrooms_group + chatrooms_single
    CreateTime_counter = {}
    for i in chatrooms_single:
        for j in basicTool.GetData(i,["CreateTime","Des"],start_time=start_time,end_time=end_time,Type=2):
            if j[1] == Des:
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

    with basicTool.SqliteInit() as sqlite_cur:
        for i in chatrooms_all:
            temp_list = []
            sql = "select Message,Des,Type from "+i+" where CreateTime>="+str(time1)+" and CreateTime<="+str(time2)
            sqlite_cur.execute(sql)
            result = sqlite_cur.fetchall()
            for row in result:
                if i != "Chat_b7ebbe67d8f64c77cda5415f4d749cc6" and row[1] == Des and row[2]==1:
                    temp_list.append(row[0])
                if row[1] == Des and row[2] == 1:
                    my_message.append(row[0])
            if len(temp_list)>0:
                chat_with[i] = temp_list

    with open(filename+".txt","w+",encoding="utf-8") as f:
        f.write(sorted_list[0][0]+"\n")
        for key,value in chat_with.items():
            for i in value:
                f.write(basicTool.GetName(key)+","+i+"\n")

if __name__=='__main__':
    chatrooms_group = basicTool.GetChatrooms(typename=1)
    chatrooms_single = basicTool.GetChatrooms(typename=2)
    BaseData(chatrooms_group, chatrooms_single)
    MostEmoji(chatrooms_group, chatrooms_single)
    TypeAnalyse(chatrooms_single)
    RowAnalyse(chatrooms_single)
    TimeSlice(chatrooms_single,1,6)
    MostDay(chatrooms_group,chatrooms_single,filename="消息最多的一天（接收）",Des=1)
    MostDay(chatrooms_group,chatrooms_single,filename="消息最多的一天（发送）",Des=0)