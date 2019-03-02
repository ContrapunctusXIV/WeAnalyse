import json
import re
import getChat
import sqlInit
import numpy as np
from pyecharts import Geo, configure
from pyecharts.datasets.coordinates import search_coordinates_by_keyword
from pyecharts_snapshot.main import make_a_snapshot
import jieba
import operator

def GeoAll(chartname="",filename="geo_ana_all",typename=0,Des=2):
    '''
    chartname：str，图表名
    filename：str，文件名，存储在output文件夹下
    typename：int，0：全部，1：群组，2：个人，3：公众号
    Des：0：发出，1：接收，2：全部
    '''
    message_list = []
    counter0 = 0
    chatrooms = getChat.GetChatrooms(typename=1)
    chatrooms.extend(getChat.GetChatrooms(typename=2))
    for chatroom in chatrooms:
        for row in getChat.GetData(chatroom=chatroom,columns=["Message","Type"],Desname=Des):
            if row[1] == 1:
                message_list.append(row[0])
                counter0 += 1
    print("数据量：",counter0)
    joined_message = ",".join(message_list)
    cutted_message = []
    for i in jieba.lcut(joined_message):
        if len(i)>1:
            cutted_message.append(i)

    name_id_dict = {}
    sql = "select id,name from Geodata"
    with sqlInit.MysqlInit() as mysql_cur:
        mysql_cur.execute(sql)
        result = mysql_cur.fetchall()
        for row in result:
            name_id_dict[row[1]] = row[0]

    word_counter_dict = {}
    counter1 = 0
    for word in cutted_message:
        if word in name_id_dict.keys():
            counter1 += 1
            if not word in word_counter_dict:
                word_counter_dict[word] = 1
            else:
                word_counter_dict[word] += 1
    sorted_list = sorted(word_counter_dict.items(), reverse=True, key=operator.itemgetter(1))
    return sorted_list


def GeoSingle(chatroom="",chartname="",filename="geo_ana_single",Des=2):
    '''
    chatroom：str，聊天记录名
    chartname：str，图表名
    filename：str，文件名，存储在output文件夹下
    typename：int，0：全部，1：群组，2：个人，3：公众号
    Des：0：发出，1：接收，2：全部
    '''
    message_list = []
    counter0 = 0
    for row in getChat.GetData(chatroom=chatroom,columns=["Message","Type"],Desname=Des):
        if row[1] == 1:
            message_list.append(row[0])
            counter0 += 1
    print("数据量：",counter0)
    joined_message = ",".join(message_list)
    cutted_message = []
    for i in jieba.lcut(joined_message):
        if len(i)>1:
            cutted_message.append(i)

    name_id_dict = {}
    sql = "select id,name from Geodata"
    with sqlInit.MysqlInit() as mysql_cur:
        mysql_cur.execute(sql)
        result = mysql_cur.fetchall()
        for row in result:
            name_id_dict[row[1]] = row[0]
    word_counter_dict = {}
    counter1 = 0
    for word in cutted_message:
        if word in name_id_dict.keys():
            counter1 += 1
            if not word in word_counter_dict.keys():
                word_counter_dict[word] = 1
            else:
                word_counter_dict[word] += 1
    sorted_list = sorted(word_counter_dict.items(), reverse=True, key=operator.itemgetter(1))
    return sorted_list

def GeoMap(filename = "geo_ana"):
    f = open("geo.txt","r",encoding="utf-8")
    params = f.readline()
    f.close()
    place_list = re.findall("[(](.*?)[)]",params)
    name_counter_dict = {}
    for i in place_list:
        name_counter_dict[i.split(",")[0].strip('"').strip("'")] = int(i.split(",")[1].strip("'"))
    tempered_name_counter_dict = {}
    for key,value in name_counter_dict.items():
        if len(key)>2 and (key[-1] == "市" or key[-1] == "省"):
            if key[:-1] in tempered_name_counter_dict.keys():
                tempered_name_counter_dict[key[:-1]] = tempered_name_counter_dict[key[:-1]] + value
            else:
                tempered_name_counter_dict[key[:-1]] = value
        elif key in ['上合','南山区','翻身','科技园','桃园','光明','大学城','八卦岭','龙华','西乡','华侨城','梧桐山','大冲','沙井','红树湾']:
            if "深圳" in tempered_name_counter_dict.keys():
                tempered_name_counter_dict["深圳"] = tempered_name_counter_dict["深圳"] + value
            else:
                tempered_name_counter_dict["深圳"] = value
        elif key in ['中关村']:
            if "北京" in tempered_name_counter_dict.keys():
                tempered_name_counter_dict["北京"] = tempered_name_counter_dict["北京"] + value
            else:
                tempered_name_counter_dict["北京"] = value
        elif key in ['虹桥']:
            if "上海" in tempered_name_counter_dict.keys():
                tempered_name_counter_dict["上海"] = tempered_name_counter_dict["上海"] + value
            else:
                tempered_name_counter_dict["上海"] = value
        else:
            tempered_name_counter_dict[key] = value

    name_code_dict = {}
    code_name_dict = {}
    code_counter_dict = {}
    simplified_code_counter_dict = {}
    simplified_name_counter_dict = {}
    final_data = []
    sql = "select code,name from Geodata"
    with sqlInit.MysqlInit() as mysql_cur:
        mysql_cur.execute(sql)
        result = mysql_cur.fetchall()
        for row in result:
            name_code_dict[row[1]] = row[0]
            code_name_dict[row[0]] = row[1]
    for key,value in tempered_name_counter_dict.items():
        code_counter_dict[name_code_dict[key]] = value
    for key,value in code_counter_dict.items():
        if len(str(key))<=4:
            simplified_code_counter_dict[key] = value
        else:
            if int(str(key)[:4]) in simplified_code_counter_dict.keys():
                simplified_code_counter_dict[int(str(key)[:4])] = simplified_code_counter_dict[int(str(key)[:4])] + value
            else:
                simplified_code_counter_dict[int(str(key)[:4])] = value
    for key,value in simplified_code_counter_dict.items():
        with sqlInit.GeoSqlInit() as sqlite_cur:
            if len(str(key))==2:
                sql1 = "select name from province where code="+str(key)
                fetchResult1 = sqlite_cur.execute(sql1)
                for row in fetchResult1:
                    simplified_name_counter_dict[row[0]] = value
                    if "自治区" in row[0]:
                        final_data.append((row[0].strip("自治区"),value))
                    else:
                        final_data.append((row[0][:-1],value))
            elif len(str(key))==4:
                sql2 = "select name from city where code="+str(key)
                fetchResult2 = sqlite_cur.execute(sql2)
                for row in fetchResult2:
                    if row[0] == "市辖区":
                        sql3 = "select name from province where code="+str(key)[:2]
                        fetchResult3 = sqlite_cur.execute(sql3)
                        for row2 in fetchResult3:
                            simplified_name_counter_dict[row2[0]] = value
                            final_data.append((row2[0],value))
                    elif row[0] == "襄阳市":
                        simplified_name_counter_dict[row[0][:-1]] = value
                        final_data.append((row[0][:-1],value))
                    else:
                        simplified_name_counter_dict[row[0]] = value
                        final_data.append((row[0],value))
    data = final_data
    geo = Geo(
        "",
        "",
        title_color="#fff",
        title_pos="center",
        width=1200,
        height=600,
        background_color="#404a59",
    )
    attr, value = geo.cast(data)
    geo.add(
        "",
        attr,
        value,
        visual_range=[0, 200],
        visual_text_color="#fff",
        symbol_size=15,
        type="heatmap",
        is_visualmap=True,
        maptype='china',
        coordinate_region='中国'
    )
    geo.render(path="./output/"+filename+".html")
    geo.render(path="./output/"+filename+".pdf")
    print("已生成图")

GeoMap()
# GeoSingle(chatroom="chat_d54c228cca88e616bea79addf871522b")
# geo_result = geo_all(typename=2)
# geo_json = {}
# for i in geo_result:
#     geo_json[i[0]] = [i[1]]
# with open("geo.json", 'w+',encoding="utf-8") as f:
#     json.dump(geo_json, f, ensure_ascii=False)
