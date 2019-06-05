import jieba
import matplotlib.pyplot as plt
import PIL.Image as Image
import basicTool
import numpy as np
from pyecharts import WordCloud
# from pyecharts_snapshot.main import make_a_snapshot

def WordcloudAll(chatrooms,filename="wc_all", maxwords=50, Des=2, title=""):
    '''
    filename：str，文件名，存储在output文件夹下
    maxwords：int，最大词云量
    Des：0：发出，1：接收，2：全部
    '''
    message_list = []
    for chatroom in chatrooms:
        for row in basicTool.GetData(chatroom=chatroom,columns=["Message","Type","Des"]):
            if row[1]==1:
                if row[2]==Des:
                    message_list.append(row[0])
    Normal(message_list,filename = filename, maxwords = maxwords, title="")

def WordCloudSingle(chatroom,filename="wc_single",maxwords=200,Des=2,from_user="",title=""):
    '''
    filename：str，文件名
    maxwords：int，最大词云量
    Des：0：发送，1：接收，2：全部
    '''
    message_list = []
    for row in basicTool.GetData(chatroom=chatroom,columns=["Message","Type","SentFrom","Des"]):
        if row[1]==1:
            if Des==2:
                if from_user=="":
                    message_list.append(row[0])
                else:
                    if row[2]==from_user:
                        message_list.append(row[0])
            else:
                if row[3]==Des:
                    if from_user=="":
                        message_list.append(row[0])
                    else:
                        if row[2]==from_user:
                            message_list.append(row[0])
    Normal(message_list,filename = filename, maxwords = maxwords, title=title)

def Normal(params,filename = "wc_normal",maxwords = 200,title=""):
    '''
    filename：str，文件名
    maxwords：int，最大词云量
    Des：0：发送，1：接收，2：全部
    '''
    seperated_list = []
    counter = 0
    for row in params:
        counter += 1
        seperated_list.extend(jieba.cut(row))

    word_id_dict = dict.fromkeys(seperated_list, 0)
    id_counter_dict = dict.fromkeys(range(len(word_id_dict)), 0)
    counter0 = 0
    id_word_dict = {}
    for key,value in word_id_dict.items():
        word_id_dict[key] = counter0
        id_word_dict[counter0] = key
        counter0 += 1
    for i in seperated_list:
        id_counter_dict[word_id_dict[i]] += 1
    word_array = np.zeros((len(id_counter_dict),2),dtype="int")
    counter1 = 0
    for key,value in id_counter_dict.items():
        word_array[counter1,0] = key
        word_array[counter1,1] = value
        counter1 += 1
    sorted_word = word_array[np.argsort(-word_array[:,1])]
    sorted_list = []
    for i in sorted_word:
        temp_word = id_word_dict[i[0]]
        if len(temp_word)>1 and temp_word.isdigit() == False:
            sorted_list.append([temp_word,i[1]])
    name = []
    frequency = []
    if len(sorted_list)>=maxwords:
        maxwords_inuse = maxwords
    else:
        maxwords_inuse = len(sorted_list)
    for i in sorted_list[:maxwords_inuse]:
        name.append(i[0])
        frequency.append(i[1])
    wordcloud = WordCloud(title=title,width=1300, height=620,title_top="18%",title_pos="20%",title_text_size="30")
    wordcloud.add("",name, frequency, word_size_range=[20, 100])
    wordcloud.render(filename+".html")
    # wordcloud.render(filename+".pdf")

if __name__=='__main__':
    # chatrooms_group = basicTool.GetChatrooms(typename=1)
    # chatrooms_single = basicTool.GetChatrooms(typename=2)
    # chatrooms_all = chatrooms_group + chatrooms_single
    # WordcloudAll(chatrooms_single,filename="接收词频（个人）（词云图）",maxwords=100,Des=1)
    # WordcloudAll(chatrooms_group,filename="发送词频（群组）（词云图）",maxwords=50,Des=0)
    # WordcloudAll(chatrooms_single,filename="发送词频（个人）（词云图）",maxwords=100,Des=0)
    # WordcloudAll(chatrooms_all,filename="发送词频（全部）（词云图）",maxwords=100,Des=0)
    # WordcloudAll(chatrooms_group,filename="发送词频（群组）（词云图）",maxwords=50,Des=0)
    print(basicTool.GetWXID("Chat_67183be064c8c3ef11df9bb7a53014c8"))
    WordCloudSingle("Chat_67183be064c8c3ef11df9bb7a53014c8",filename="thedeadgroup",maxwords=200,Des=2)
