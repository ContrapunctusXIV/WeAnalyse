import jieba
import matplotlib.pyplot as plt
import PIL.Image as Image
import basicTool
import numpy as np
from pyecharts import Bar,Grid
# from pyecharts_snapshot.main import make_a_snapshot

def GroupRankingAll(chatrooms,filename="group_ranking_all", num = 10 ,Des=2, title=""):
    '''
    统计群里发言最多的人
    chatrooms：list，聊天记录表
    filename：str，文件名，存储在output文件夹下
    Des：0：发出，1：接收，2：全部
    '''
    message_list = []
    for chatroom in chatrooms:
        for row in basicTool.GetData(chatroom=chatroom,columns=["SentFrom","Message"]):
            if row[0]!="system":
                message_list.append(row)
    Normal(message_list, filename = filename, num = num, title=title)

def GroupRankingSingle(chatroom,filename="group_ranking_single", num = 10, Des=2, title=""):
    '''
    统计群里发言最多的人
    chatrooms：list，聊天记录表
    filename：str，文件名，存储在output文件夹下
    Des：0：发出，1：接收，2：全部
    '''
    message_list = []
    for row in basicTool.GetData(chatroom=chatroom,columns=["SentFrom","Message"]):
        if row[0]!="system":
            message_list.append(row)
    Normal(message_list, filename = filename, num = num, title=title)

def Normal(params, filename = "group_ranking", num = 10, title=""):
    '''
    '''
    # getNamed_list = [[basicTool.GetName(i[0]),i[1]] for i in params]
    id_counter_dict = dict.fromkeys([i[0] for i in params], 0)
    for i in params:
        id_counter_dict[i[0]] += 1
    name_counter_dict = {}
    for key,value in id_counter_dict.items():
        name = basicTool.GetName(key)
        if not name in name_counter_dict.keys():
            name_counter_dict[name] = value
        else:
            name_counter_dict[name] += value
    name_counter_sorted_list = sorted(name_counter_dict.items(), key=lambda x: x[1],reverse=True)
    x_list = [i[0] for i in name_counter_sorted_list]
    y_list = [i[1] for i in name_counter_sorted_list]
    grid=Grid()
    bar = Bar(title=title,title_pos="40%")
    if len(x_list)<num:
        bar.add("", x_list, y_list, is_convert=True)
    else:
        bar.add("", x_list[:num], 
        y_list[:num],
        is_label_show=True,
        xaxis_interval=0,
        is_xaxislabel_align=True,
        xaxis_rotate=30,
        is_xaxis_show=True,
        is_yaxis_show=True,
        # is_datazoom_show=True,
        is_splitline_show=False)
    grid.add(bar,grid_bottom="30%")
    grid.render(path=filename+".html")

if __name__=='__main__':
    GroupRankingSingle("Chat_67183be064c8c3ef11df9bb7a53014c8",filename="thedeadgroup_userranking_v", num = 25, Des=2, title="")
    # chatrooms_group = basicTool.GetChatrooms(typename=1)
    # GroupRankingAll(chatrooms_group,filename="group_ranking_single", num = 25, Des=2, title="")
    # chatrooms_temp = []
    # for chatroom in chatrooms_group:
    #     chatrooms_temp.append((chatroom,basicTool.GetRowNum(chatroom)))
    # chatrooms_top_group = sorted(chatrooms_temp, key=lambda x: x[1],reverse=True)[:3]
    # counter = 0
    # for i in chatrooms_top_group:
    #     counter += 1
    #     groupname = basicTool.GetName(i[0])
    #     GroupRankingSingle(i[0],filename=str(counter)+".排名前三群聊中的发出消息排名（柱状图）", num = 25, Des=2, title=groupname)
