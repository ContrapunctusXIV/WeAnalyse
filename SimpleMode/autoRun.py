import basicTool
import basicData
import timeAnalyse
import usageAnalyse
import wordcloudAnalyse

def AutoRun(outputdir = "./outputs"):
    print("正在获取聊天数据表...")
    chatrooms_group = basicTool.GetChatrooms(typename=1)
    chatrooms_single = basicTool.GetChatrooms(typename=2)
    chatrooms_all = chatrooms_group + chatrooms_single
    print("正在生成基本数据...")
    basicData.BaseData(chatrooms_group, chatrooms_single, filename=outputdir+"/基本数据")
    print("正在生成表情包数据...")
    basicData.MostEmoji(chatrooms_group, chatrooms_single, filename=outputdir+"/表情包数据")
    print("正在生成消息类型图...")
    basicData.TypeAnalyse(chatrooms_single, filename=outputdir+"/消息类型（仅好友）（饼图）")
    print("正在生成消息总量图...")
    basicData.RowAnalyse(chatrooms_single, filename=outputdir+"/消息总量（柱状图）")
    print("正在获取深夜消息...")
    basicData.TimeSlice(chatrooms_single,1,6,filename=outputdir+"/深夜消息（1-6点）")
    print("正在寻找产生消息最多的日期...")
    basicData.MostDay(chatrooms_group,chatrooms_single,filename=outputdir+"/消息最多的一天（接收）",Des=1)
    basicData.MostDay(chatrooms_group,chatrooms_single,filename=outputdir+"/消息最多的一天（发送）",Des=0)
    print("正在寻找未回复的消息...")
    usageAnalyse.Lonelydude(chatrooms_single,filename=outputdir+"/未回复的消息")
    print("正在生成使用情况日历图...")
    usageAnalyse.UsageAll(chatrooms_all,chartname="使用日历-发出（全部）",filename=outputdir+"/使用日历-发出（全部）（日历图）",Des=0)
    usageAnalyse.UsageAll(chatrooms_single, chartname="使用日历-发出（个人）",filename=outputdir+"/使用日历-发出（个人）（日历图）",Des=0)
    usageAnalyse.UsageAll(chatrooms_single, chartname="使用日历-接收（个人）",filename=outputdir+"/使用日历-接收（个人）（日历图）",Des=1)
    print("正在生成消息时频分布图...")
    timeAnalyse.TimeAll(chatrooms_single, chartname="时频分布-接收（个人）",filename=outputdir+"/时频分布-接收（个人）（柱状图）",Des=1)
    timeAnalyse.TimeAll(chatrooms_all, chartname="时频分布-发出（全部）",filename=outputdir+"/时频分布-发出（全部）（柱状图）",Des=0)
    print("正在生成消息总量走势图...")
    timeAnalyse.RowLine(chatrooms_single, filename=outputdir+"/总量走势（折线图）")
    print("正在生成词云...")
    wordcloudAnalyse.WordcloudAll(chatrooms_single,filename=outputdir+"/接收词频（个人）（词云图）",maxwords=100,Des=1)
    wordcloudAnalyse.WordcloudAll(chatrooms_group,filename=outputdir+"/发送词频（群组）（词云图）",maxwords=50,Des=0)
    wordcloudAnalyse.WordcloudAll(chatrooms_single,filename=outputdir+"/发送词频（个人）（词云图）",maxwords=100,Des=0)
    wordcloudAnalyse.WordcloudAll(chatrooms_all,filename=outputdir+"/发送词频（全部）（词云图）",maxwords=100,Des=0)
    print("已完成！")

if __name__=='__main__':
    AutoRun(outputdir = "./outputs")