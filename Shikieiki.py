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
import time
import requests
import threading
from random import random

__version__ = 202201281751
__SaveLog__ = os.path.join(sys.path[0] ,'log')
__Config__ = 'config.lwar.yml'
#=========================================================
# 日志函数
I = 0
W = 1
E = 2
def log(info: str, stat: int = 0):
    sign = ["[i]", "<!>", "(x)"]

    consOutMark = ["\033[;32m", "\033[;33m", "\033[;31m"]
    print("[" + time.strftime("%Y-%m-%d %H:%M:%S")+"]"+ consOutMark[stat] + sign[stat] + info + '\033[;0m')
    try:
        open(
            os.path.join(
                __SaveLog__, 
                "LOG-" + time.strftime("%Y-%m-%d") + ".log"
            ),
            "a+").write(
                "[" + time.strftime("%Y-%m-%d %H:%M:%S")+"]" + sign[stat] + info + "\n"
            )
    except:
        print("无法记录日志！请检查日志保存路径及其写入权限。")
        sys.exit(-1)

#=========================================================
#  读取配置
__version__ = str(__version__)
__LEAN_APP_ID__:str = None
__LEAN_APP_KEY__:str = None
try:
    f = open(os.path.join(sys.path[0], __Config__), 'r', encoding='utf-8')
    ymlc = f.read()
    config = yaml.load(ymlc, Loader=yaml.FullLoader)
except Exception as e:
    log(str(e))
else:
    try:
        __LEAN_APP_ID__ = config['LeanAppId']
        __LEAN_APP_KEY__ = config['LeanAppKey']
    except KeyError:
        log("非法的配置文件！", E)
        os._exit(-1)
finally:
    f.close()
    try:
        if(not os.path.isdir(__SaveLog__)):
            os.mkdir(__SaveLog__)
    except PermissionError:
        log("无写入权限！", E) 
        os._exit(-1)
    except Exception as e:
        log(str(e)) 
        os._exit(-1)
    else:
        log('LWAR alpha v.'+__version__)
        log('(C) 2022 非科学の河童, All Rights Reserved')
        log('遵循GPLv2许可证分发')
        log('''
                        ####################
                        # 此程序不含担保！ #
                        ####################''', W)

#=========================================================
# 初始化Leancloud
leancloud.init(__LEAN_APP_ID__, __LEAN_APP_KEY__)


#=========================================================
# 遍历评论列表
try:
    c = leancloud.Object.extend('Comment')
    d = c.query
    # 每次请求返回100条，mRecentTime是上次请求返回的最后一个object的发布时间，凭借此再次请求
    mRecentTime = datetime.datetime(2020, 8, 29).replace(tzinfo=pytz.timezone('UTC')) 
except Exception as e:
    log(str(e), E) 
    os._exit(-1)


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

try:
    # 筛选
    t = getpage(d, ["objectId", "mail", "status"])
except ConnectionError as e:
    log("无法与"+ e.request.__dict__['url'] +"建立连接！", E)
    log("请检查配置文件", W)
    os._exit(-1)
except Exception as e:
    log(str(e), E)
    os._exit(-1)
else:
    try:
        log("整理已评论邮箱：开始")
        WhiteEmailADDRs:list = []
        BlackEmailADDRs:list = []
        for a in t:
            a["mail"].replace(" ","")
            if(a["mail"] != "\n"):
                if(a["status"] == "approved" and a["mail"] not in WhiteEmailADDRs):
                    log("objectId:\t"+a['objectId']+';\tmail:\t'+a["mail"]+'\t\t.加入白名单')
                    WhiteEmailADDRs.append(a["mail"])
                elif(a["status"] == "spam" and a["mail"] not in BlackEmailADDRs):
                    log("objectId:\t"+a['objectId']+';\tmail:\t'+a["mail"]+'.\t\t加入黑名单')
                    BlackEmailADDRs.append(a["mail"])
                else:
                    #log("objectId:\t"+a['objectId']+'\t;mail:\t'+a["mail"]+'\t\t.跳过', W)
                    pass
        log("整理已评论邮箱：完成")
    except Exception as e:
        log(str(e), E)
        os._exit(-1)

