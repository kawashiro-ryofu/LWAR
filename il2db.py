'''

Leancloud Waline Audit Robot
(C) Copyright 2022 非科学の河童, All Rights Reserved.
Follow GPL 2.0 License.

il2db.py
上传黑白名单至数据库

'''
import leancloud
import Shikieiki
import os
from Shikieiki import log

__LEAN_APP_ID__ = Shikieiki.config['LeanAppId']
__LEAN_APP_KEY__ = Shikieiki.config['LeanAppKey']

I = 0
E = 1
W = 2

#=========================================================
# 初始化leancloud
leancloud.init(__LEAN_APP_ID__, __LEAN_APP_KEY__)

# 用于查重并上传的函数
# r -> leancloud.query.Query对象（提前添加好查询条件）
# d -> leancloud.Object.extend
def setprop(r, d):
    if(len(r.find())):
        pass
    else:
        d.set('mail', a)
        d.save()

# To-Do 改多线程
# 读入上传白名单地址
try:
    c = leancloud.Object.extend('Whitelist')
    whitelist = Shikieiki.WhiteEmailADDRs

    count = 0
    total = len(whitelist)
    for a in whitelist:
        sleep(0.5)
        count += 1
        a = a.replace('\n', '')
        a = a.replace(' ','')
        if(a == ""):
            log("跳过\t\t("+str(count)+"/"+str(total)+")",W)
        else:
            r = c.query
            r.equal_to('mail',a)
            setprop(r, c())
            log("上传白名单\t("+str(count)+"/"+str(total)+")")

    # 读入上传黑名单地址
    c = leancloud.Object.extend('Blacklist')
    blacklist = Shikieiki.BlackEmailADDRs
    count = 0
    total = len(blacklist)
    for a in blacklist:
        sleep(0.5)
        count += 1
        a = a.replace('\n', '')
        a = a.replace(' ','')
        if(a == ""):
            log("跳过\t\t("+str(count)+"/"+str(total)+")",W)
        else:
            r = c.query
            r.equal_to('mail',a)
            setprop(r, c())
            log("上传黑名单\t("+str(count)+"/"+str(total)+")")

except Exception as e:
    log(str(e),E)
    os._exit(-1)
finally:
    del(count)
    del(total)
