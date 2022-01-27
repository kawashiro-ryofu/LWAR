'''

Leancloud Waline Audit Robot
(C) Copyright 2022 非科学の河童, All Rights Reserved.
Follow GPL 2.0 License.

Shiklieiki.py
筛选出Waline评论E-mail地址

'''
import leancloud
import datetime
import pytz
import yaml
import os
import sys


#=========================================================
#  读取配置

f = open(os.path.join(sys.path[0], 'config.lwar.yml'), 'r', encoding='utf-8')
ymlc = f.read()
f.close()
config = yaml.load(ymlc, Loader=yaml.FullLoader)

__LEAN_APP_ID__ = config['LeanAppId']
__LEAN_APP_KEY__ = config['LeanAppKey']

#=========================================================

# 初始化Leancloud
leancloud.init(__LEAN_APP_ID__, __LEAN_APP_KEY__)

#=========================================================
# 遍历评论列表
c = leancloud.Object.extend('Comment')
d = c.query


# 每次请求返回100条，mRecentTime是上次请求返回的最后一个object的发布时间，凭借此再次请求
mRecentTime = datetime.datetime(2020, 8, 29).replace(tzinfo=pytz.timezone('UTC')) 

# 遍历leancloud.query.Query.find()生成列表
# l -> leancloud.query.Query.find()函数返回的列表
# args -> （列表）键名列表
def genlist(l, *args):
    
    keylist = args[0]
    global mRecentTime
    l2rt:list = []
    for a in l:
        mRecentTime = a.get('createdAt').replace(tzinfo=pytz.timezone('UTC'))
        if(len(keylist) > 1):
            objl:dict = {}
            for b in range(len(keylist)):
                objl[keylist[b]] = a.get(str(keylist[b]))
            if(not objl in l2rt):
                l2rt.append(objl)
        else:
            l2rt.append(a.get(keylist[0]))
    return l2rt


# Leancloud限制每次返回100条数据，此函数分批次获取全部数据
# f -> leancloud.query.Query对象
# args -> （列表）键名
def getpage(f, *args):
    PageC = f.count() // 100
    if(f.count()%100 != 0 and f.count()%100 < 100):
        PageC+=1
    outList:list = []
    for a in range(PageC):
        f.greater_than('createdAt', mRecentTime)
        t = genlist(f.find(), args[0])
        outList += t
    return outList
  
# 筛选
t = getpage(d, ["mail", "status"])


WhiteEmailADDRs:list = []
BlackEmailADDRs:list = []
for a in t:
    a["mail"].replace(" ","")
    if(a["mail"] != "\n"):
        if(a["status"] == "approved" and a["mail"] not in WhiteEmailADDRs):
            WhiteEmailADDRs.append(a["mail"])
        elif(a["status"] == "spam" and a["mail"] not in BlackEmailADDRs):
            BlackEmailADDRs.append(a["mail"])
        else:
            pass

