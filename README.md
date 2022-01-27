# Leancloud Waline Audit Robot(**LWAR**)

适用于使用Leancloud作为数据库的Waline评论系统的自动审核脚本。

## 须知

1. 这个项目仍在开发，测试或使用请提前备份好数据；
2. 遵循GPL 2.0协议分发，这意味着使用本程序造成的损失自行承担；
3. 使用Valine-Admin后台会出现无权限写入的问题。

## 要求

一台能运行Python3的服务器（也可以是闲置的手机电脑，不需要内网穿透，只需要能运行Python3，支持pip）

## 安装

### 0. 

安装好Python3，把这个项目克隆/下载下来。

在Leancloud控制台提前创建`Blacklist`和`Whitelist`两个Class。

### 1. 安装依赖

在储存库根目录执行：

```bash
pip install -r requirements.txt
```

### 2. 编辑配置文件

更改`config.lwar.yml`，将`LeanAppId`和`LeanAppKey`的值分别改为Leancloud应用的`AppID`和`AppKey`。

### 3. 执行`auditRobot.py`进行测试

现阶段不在控制台输出任何字符串就算程序正常。

之后会加入日志。

### 4. 将`auditRobot.py`设为开机启动

## To-Do

 - 解决`WhiteEmailADDRs`和`BlackEmailADDRs`的空格问题
 - 加入日志功能
 - 定期重启
 - 加入正则表达式
