#WeAnalyse

##生成自己的微信使用数据

##这个项目面向谁？

所有在用Windows电脑的iOS用户。因为微信在iOS中的数据库未被加密，所以可以被轻易获取。安卓就没这么好运了。

当然，如果自己有备用的iPhone或iPad，也可以从安卓机迁移过去（非常简单）。

总的流程大致可分为：

用iTunes备份数据->安装备份提取软件->从备份中提取微信数据库->运行分析程序->完成！

 

##下面进行详细说明

首先将手机连上电脑，然后打开iTunes，在顶端点击红圈内的位置进入设备管理界面。

![Image text](https://github.com/ContrapunctusXIV/WeAnalyse/tree/master/images/1.png)

然后点击红圈内的立即备份，随后顶端会显示备份进度。

![Image text](https://github.com/ContrapunctusXIV/WeAnalyse/tree/master/images/2.png)

**备份可能会很久。并且，由于备份只能存在C盘，所以需要确保C盘有20G以上的空间。**

 

在备份期间，我们可以进行其它工作。

首先，下载一个可以读取备份的软件，我用的是iTools，在这里下载：

https://pro.itools.cn/itools3

注意安装时请不要勾选这玩意：

![Image text](https://github.com/ContrapunctusXIV/WeAnalyse/tree/master/images/3.png)

准备工作到此为止，下面等待之前的备份完成即可。

 

完成备份后，打开iTools，点击工具箱->iTunes备份管理->双击打开备份，你应该能看到这个界面

![Image text](https://github.com/ContrapunctusXIV/WeAnalyse/tree/master/images/4.png)

复制这个路径到红线上方的空白处：

/var/mobile/Applications/com.tencent.xin/Documents

这里就是存储微信数据的位置。

我们需要关注的是红圈圈住的那几个文件夹，具体名字与你看到的应该不一样，但格式都是一长串字母与数字的组合（实际上是你微信号的md5值）。

![Image text](https://github.com/ContrapunctusXIV/WeAnalyse/tree/master/images/5.png)

如果你的手机上登陆过多个微信账号，那么这种文件夹也有多个。我们需要的是这几个文件夹下 “DB”文件夹中的MM.sqlite和WCDB_Contact.sqlite两个文件。

![Image text](https://github.com/ContrapunctusXIV/WeAnalyse/tree/master/images/6.png)

由于我的另外两个账号都是临时登录的，聊天记录很少，所以根据文件大小很容易看出哪个是我的账号的数据。如果你无法通过这种方法分辨，那还是全部都提取出来吧。

 

提取的方法是选择这两个文件然后点击左上方的导出，然后选择目标文件夹即可。

![Image text](https://github.com/ContrapunctusXIV/WeAnalyse/tree/master/images/7.png)

提取整个WeAnalyse-master文件夹。

在这个文件夹里新建一个data文件夹，把刚才导出的微信数据放进去。

![Image text](https://github.com/ContrapunctusXIV/WeAnalyse/tree/master/images/8.png)

![Image text](https://github.com/ContrapunctusXIV/WeAnalyse/tree/master/images/9.png)

最后一步：

双击run.bat文件，它会自动接下来所有的工作。

程序运行结束后，可以在outputs文件夹中找到生成的文件。

 

注：如果报错，可能是Visual C++版本过低（14以上），请在这里下载并安装。

<https://download.visualstudio.microsoft.com/download/pr/e9e1e87c-5bba-49fa-8bad-e00f0527f9bc/8e641901c2257dda7f0d3fd26541e07a/vc_redist.x86.exe>

 

