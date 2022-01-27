'''

Leancloud Waline Audit Robot
(C) Copyright 2022 非科学の河童, All Rights Reserved.
Follow GPL 2.0 License.

il2db.py
上传黑白名单至数据库

'''
import leancloud
import Shikieiki
#=========================================================
#  自行设置
__LEAN_APP_ID__ = Shikieiki.config['LeanAppId']
__LEAN_APP_KEY__ = Shikieiki.config['LeanAppKey']

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

# 读入上传白名单地址
c = leancloud.Object.extend('Whitelist')
whitelist = Shikieiki.WhiteEmailADDRs

for a in whitelist:
    a = a.replace('\n', '')

    r = c.query
    r.equal_to('mail',a)

    setprop(r, c())

# 读入上传黑名单地址
c = leancloud.Object.extend('Blacklist')
blacklist = Shikieiki.BlackEmailADDRs


for a in blacklist:
    a = a.replace('\n', '')

    r = c.query
    r.equal_to('mail',a)

    setprop(r, c())