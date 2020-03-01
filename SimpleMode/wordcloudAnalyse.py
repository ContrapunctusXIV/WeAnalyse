import jieba
import matplotlib.pyplot as plt
import PIL.Image as Image
import basicTool
import numpy as np
from pyecharts import WordCloud
# from pyecharts_snapshot.main import make_a_snapshot

def WordcloudAll(chatrooms,filename="wc_all", maxwords=50, Des=2, skip_useless=0,start_time="1970-01-01", end_time="",title=""):
    '''
    filename：str，文件名，存储在output文件夹下
    maxwords：int，最大词云量
    Des：0：发出，1：接收，2：全部
    '''
    message_list = []
    for chatroom in chatrooms:
        for row in basicTool.GetData(chatroom=chatroom,columns=["Message","Type"],Des=Des,start_time=start_time, end_time=end_time):
            if row[1]==1:
                message_list.append(row[0])

    Normal(message_list,filename = filename, maxwords = maxwords,skip_useless=skip_useless,title="")

def WordCloudSingle(chatroom,filename="wc_single",maxwords=200,Des=2,from_user="",start_time="1970-01-01", end_time="",title=""):
    '''
    filename：str，文件名
    from_user：str，用户名
    maxwords：int，最大词云量
    Des：0：发送，1：接收，2：全部
    '''
    message_list = []
    for row in basicTool.GetData(chatroom=chatroom,columns=["Message","Type","SentFrom"],Des=Des,start_time=start_time, end_time=end_time):
        if row[1]==1:
            if from_user=="":
                message_list.append(row[0])
            else:
                if row[2]==from_user:
                    message_list.append(row[0])
    Normal(message_list,filename = filename, maxwords = maxwords, title=title)

def Normal(params,filename = "wc_normal",maxwords = 200,title="",skip_useless=0):
    '''
    filename：str，文件名
    maxwords：int，最大词云量
    Des：0：发送，1：接收，2：全部
    skip_useless：0：不跳过无意义词，1：跳过无意义词
    '''
    useless_word = ["就是","可以","不是","一个","这个","没有","什么","还是","现在","自己","你们","怎么","觉得","知道","我们","这么","问题","感觉","时候","那个","应该","可能","真的","所以","一下","这种","喜欢","不会","还有","然后","他们","不能","其实","但是","因为","一样","这样","如果","已经","出来","不要","不过","为什么","很多","那么","东西","今天","大家","看看","有点","需要","直接","多少","开始","起来","这些","而且","好像","只是","地方","是不是","以后","看到","不错","不行","只有","那种","天天","肯定","比较","为啥","几个","以前","别人","之前","要是","只能","这是","不到","不如","反正","一点","群里","估计","人家","主要","建议","有人","...","的话","不好","一直","不了","一起","时间","一般","一次","发现","为了","一定","不用","差不多","不想","记得","两个","最近","意思","以为","发展","里面","当然","或者","哪个","最后","一年","谢谢","认识","https","各位","比如","支持","只要","那些","其他","有没有","有个","com","一天","本来","除了","毕竟","每天","水平","结果","基本","事情","真是","哪里","特别","正常","准备","关系","当年","视频","小时","虽然","我要","咱们","本人","还要","了解","不然","办法","一些"]
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
    if skip_useless==0:
        for i in sorted_word:
            temp_word = id_word_dict[i[0]]
            if len(temp_word)>1 and temp_word.isdigit() == False:
                sorted_list.append([temp_word,i[1]])
    else:
        for i in sorted_word:
            temp_word = id_word_dict[i[0]]
            if len(temp_word)>1 and temp_word.isdigit() == False:
                if temp_word not in useless_word: #跳过无意义词
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
    print(basicTool.GetWXID("Chat_73fa81f0353984fbd79d780a7d65c983"))
    WordCloudSingle("Chat_73fa81f0353984fbd79d780a7d65c983",filename="001",maxwords=50,Des=2,from_user="andenverchenxiaoyi")
