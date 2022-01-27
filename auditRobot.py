'''

Leancloud Waline Audit Robot
(C) Copyright 2022 非科学の河童, All Rights Reserved.
Follow GPL 2.0 License.

auditRobot.py
自动审核

'''
import il2db
import leancloud
import datetime
import pytz
import threading
import queue


#=========================================================
#  自行设置
__LEAN_APP_ID__ = il2db.Shikieiki.config["LeanAppId"]
__LEAN_APP_KEY__ = il2db.Shikieiki.config["LeanAppKey"]

#=========================================================

# 初始化leancloud
leancloud.init(__LEAN_APP_ID__, __LEAN_APP_KEY__)

#=========================================================
# 获取当前黑白名单
bl = leancloud.Object.extend('Blacklist')
wl = leancloud.Object.extend('Whitelist')
blq = bl.query
wlq = wl.query

# 查询等待审核的评论
c = leancloud.Object.extend('Comment')
d = c.query
d.equal_to('status', 'waiting')


# Leancloud每次请求返回100条数据，mRecentTime是上次请求返回的最后一个object的发布时间，凭借此再次请求
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
        


# 根据ObjectId获取单个对象的对应数据
# ObjectId -> 对象的ObjectId
# args -> （数组）键名
def getSingleByObjectId(ObjectId, *args):
    m = d.get(ObjectId)
    out:dict = {}
    for a in args:
        out[a] = m.get(a)
    return out

# 更新对象的单一键值
# ObjectId -> 对象的ObjectId
# key -> （单一）键名
# value -> 设置键值
def updateObjSingleKey(objectId, key, value):
    m = d.get(objectId)
    m.set(key, value)
    m.save()
    print(objectId, key, value)


# 多线程getpage
# 好像也没有多大用的样子
# 当作历史遗留问题吧（笑）
class gpwt(threading.Thread):
    keylist:list = []
    output:list = []
    f:leancloud.query.Query = None
    def __init__(self, ID, name, f, *args):
        threading.Thread.__init__(self)
        #self.threadID = threadID
        self.name = name
        self.keylist = list(args)
        self.f = f
        
    def run(self):
        self.output = getpage(self.f, self.keylist)



#=========================================================
# 获取邮箱黑名单、白名单与等待审核评论队列



# 创建线程

t3 = gpwt(3,  'GetQueueOfComments2BeAudit', d, "objectId", "mail", "comment")

# 阻塞

t3.start()
t3.join()

# 得到白名单、黑名单和待审核评论队列
WhiteEmailADDRs:list = il2db.Shikieiki.WhiteEmailADDRs
BlackEmailADDRs:list = il2db.Shikieiki.BlackEmailADDRs
_2BeAuditComments:queue = queue.Queue()

for a in t3.output:
    _2BeAuditComments.put(a)

#=========================================================
# 自动审核

CommentsObjectId:dict = {
    "approved": queue.Queue(), 
    "waiting": queue.Queue(), 
    "spam": queue.Queue()
}

while(not _2BeAuditComments.empty()):
    C2audit = _2BeAuditComments.get_nowait()
    if(C2audit['mail'] in BlackEmailADDRs):
        CommentsObjectId["spam"].put(C2audit['objectId'])
    elif(C2audit['mail'] in WhiteEmailADDRs):
        CommentsObjectId["approved"].put(C2audit['objectId'])
    else:
        CommentsObjectId["waiting"].put(C2audit['objectId'])

#=========================================================
# 自动执行

status = ["approved", "waiting", "spam"]
for q in status:
    while(not CommentsObjectId[q].empty()):
        updateObjSingleKey(CommentsObjectId[q].get_nowait(), "status", q)

