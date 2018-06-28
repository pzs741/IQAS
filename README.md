# IQAS智能问答系统
IQAS是小猪快跑实验室参加第七届中国软件杯大学生软件设计大赛--A组赛题作品。
# 前台
前台使用Andriod开发，实现QA对话界面，该界面可以基于用户提问，自动连接后台、并从知识库寻找答案，并呈现给用户，前台问题可以是由主题、关键词、短语构成。

| 发布日期 | 版本号 | 下载地址 |密码|
| --- | --- | --- | --- |
|2018.6.4|text604|https://pan.baidu.com/s/1axdgTTnmdbyuVSLffEyV1A | qbi6 |

# 后台
后台由Django开发，MVP模式，可以从文档中提取尽可能多且质量高的问答对，问题可以是由主题、关键词、短语构成，答案可以直接一个段落活语句组成。
1）文档：格式html，数量大概是5w左右，所有文档类型都是用户指南、常见问题、产品手册

2）知识库QA对格式：

    Q: 弹性云服务器的价格怎么计算的？

    A: 我们有按需、包年/包月两种计费方式，您可以根据您的实际情况选择不同的计费方式。

    Q: ……

    A: ……

3）知识库管理：实现基本QA对删除、增加、查询等操作功能



| 发布日期 | 版本号 | 项目名称 |下载地址|
| --- | --- | --- | --- |
|2018.6.13| 0.1.1| 基于Web文档密度和标签的问答对抽取及挖掘算法| https://github.com/pzs741/EMDT |
|2018.6.18| 0.2.4| 基于深度学习和模板的问句生成算法| https://github.com/pzs741/QGDT |
|2018.6.18| 1.0.0| 智能问答后台管理系统| https://github.com/pzs741/IQAS |



# 文档
文档说明，包括系统设计文档、知识库构建核心规则或算法设计文档等。

| 发布日期 | 类别 | 下载地址 |密码|
| --- | --- | --- | --- |
|2018.6.12|系统设计文档|https://pan.baidu.com/s/1t52ad1E7CoOibA_yxYlqKA | 29g2 |

# 阿里云部署
前、后台采用服务器端+移动端模式，服务器端可为Web服务器，移动端为APP（Android）。

| 公网地址 | 域名 | 帐号 |密码|
| --- | --- | --- | --- |
|39.105.124.151|piggrush.cn| test | test123456 |

# github托管
```
#进入项目根目录
cd ~/project/IQAS
#初始化目录
git init 
#初始化仓库
git add . 
#本地工作区和暂存区的版本进行比较，查看当前的状态，把所有文件加入到了暂存区中，但是还没有提交到本地历史区
git status 
#把本地暂存区中的文件提交到本地历史区，只有在本地历史区中的内容才能提交到github，所有的文件都只是在本地
git commit -m 'write comment here'
#添加项目源
git remote add origin https://github.com/pzs741/IQAS.git
#把github上的文件拉下来，注意在每次提交之前要首先进行pull，防止冲突
git pull origin master
#向github提交，执行完成后，github上的repository就有和你本地一样的代码文件了
git push -u origin master 
```

# 作者
> Z.S. Peng/[Ex_treme](https://pzs741.github.io/)
