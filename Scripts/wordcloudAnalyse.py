import jieba
import matplotlib.pyplot as plt
import PIL.Image as Image
import getChat
import numpy as np
from pyecharts import WordCloud
from pyecharts_snapshot.main import make_a_snapshot

def WordcloudAll(filename = "wc_all", maxwords = 50, Des = 2, typename = 0, title=""):
    '''
    filename：str，文件名，存储在output文件夹下
    maxwords：int，最大词云量
    typename：int，0：全部，1：群组，2：个人，3：公众号
    Des：0：发出，1：接收，2：全部
    '''
    chatrooms = getChat.GetChatrooms(typename = typename)
    message_list = []
    for chatroom in chatrooms:
        for row in getChat.GetData(chatroom=chatroom,columns=["Message","Type"],Desname=Des):
            if row[1]==1:
                message_list.append(row[0])
    Normal(message_list,filename = filename, maxwords = maxwords, title="")

def WordCloudSingle(chatroom,filename = "wc_single",maxwords = 200,Des = 2,from_user="",title=""):
    '''
    filename：str，文件名，存储在output文件夹下
    maxwords：int，最大词云量
    Des：0：发送，1：接收，2：全部
    '''
    message_list = []
    for row in getChat.GetData(chatroom=chatroom,columns=["Message","Type","SentFrom"],Desname=Des):
        if row[1]==1:
            if from_user=="":
                counter2 += 1
                message_list.append(row[0])
            else:
                if row[2]==from_user:
                    counter2 += 1
                    message_list.append(row[0])
    Normal(message_list,filename = filename, maxwords = maxwords, title=title)

def Normal(params,filename = "wc_normal",maxwords = 200,title=""):
    '''
    filename：str，文件名，存储在output文件夹下
    maxwords：int，最大词云量
    Des：0：发送，1：接收，2：全部
    '''
    seperated_list = []
    counter = 0
    for row in params:
        counter += 1
        seperated_list.extend(jieba.cut(row))

    print("总条数："+str(counter))

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
    wordcloud.render("../../output/"+filename+".html")
    wordcloud.render("../../output/"+filename+".pdf")

# WordcloudAll(filename="WC_from_all",maxwords=100,Des=1,typename=2)
# WordcloudAll(filename="WC_to_all_group",maxwords=50,Des=0,typename=1)
# WordcloudAll(filename="WC_to_all_single",maxwords=100,Des=0,typename=2)
