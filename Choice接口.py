# -*- coding: utf-8 -*-
"""
@author: QiWu
"""

from EmQuantAPI import *
# 该接口需在本地下载配置文件EmQuantAPI，并在Choice购买相应权益在本地激活
# 本人电脑上正好有一个没到期的账号可以使用，但没有购买的各位可能无法使用，本文档仅作参考

# 登录Choice量化接口
loginResult = c.start()
if(loginResult.ErrorCode != 0):
    print("login in fail")
    exit()

# 获取截面数据（获取股票，指数，基金，期货等各个证券品种或组合的基本资料，财务，估值等截面数据）
# 以获取20190827的东方财富的总股本为例
data_css = c.css("300059.SZ","TOTALSHARE","enddate=20190827",Ispandas=1, RowIndex=2)

# 获取序列数据（获取股票，指数，基金，期货等各个证券品种或组合的序列数据）
# 以获取20160701-20160706的东方财富、青松建化的总股本为例
data_csd = c.csd("300059.SZ,600425.SH","TOTALSHARE","20160701","20160706",Ispandas=1, RowIndex=2)

# 获取宏观EDB数据
# 以获取代码为EMM00087117的数据为例
data_edb = c.edb("EMM00087117","IsPublishDate=1,RowIndex=1,Ispandas=1")

# 获取板块数据
# 以获取20221117的上证50板块的收盘价、日主力资金流入为例
data_cses = c.cses("B_007090","CLOSELSWAVG,INFLOWSUM","TradeDate=2022-11-17,IsHistory=0")

# 条件选股
# 以从20221117的全部A股中，筛选出市净率(PB)<=30,利润总额>0的股票，输出PB最小的前100行
data_cps = c.cps("B_001071","PB,PB,2022-11-17,8;INCOMESTATEMENT_55,INCOMESTATEMENT_55,2021-12-31,1",
                 "[PB] <= 30 and [INCOMESTATEMENT_55] > 0 ","top=min([PB],100),sectordate=2022-11-17")

# 其他功能：获取专题报表、资讯函数、资讯订阅等，对于量化策略和交易不常用，故不列出使用方式

# 以上为利用该接口调取各种数据的示例函数，由demo.py总结和命令生成网页调取
# 由于该量化接口调取数据的数据流量有限，故本人调取数据后都存入本地，之后从本地调取使用
# 该文档仅作为展示数据获取过程
