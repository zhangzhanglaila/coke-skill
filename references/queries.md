# 检索词表

`plan.py` 会用「主体词 × 场景词 × 平台」笛卡尔积生成任务。这里列出词根，采集时可自由扩展。

## 主体词（必须全覆盖，含空耳与黑话）

```
coke老师
coke老师 语录
Ccoke
蒋帅
小猫老弟
小猫老师
小猫牢底        (空耳变体)
抖一颜
痞牛
痞帮宇宙
痞帅
阿玛特拉斯 / 阿玛忒拉斯 / 阿玛特拉斯
汗流浃背了吧老弟
我嘞个骚刚 / 我嘞个大刚
喜欢吗老弟
我痞吗 / 痞吗 / 大痞天下
火影手游 主播 coke
```

## 场景词（拼在主体词后）

```
语录
语录合集
经典语录
口头禅
名场面
名梗
台词
金句
直播 切片
直播 说
连麦
PK
综艺 OK了老铁们
采访
回应
怼黑粉
搞笑 片段
表情包 出处
梗 什么意思
梗 出处
```

## 反查型（用已知梗挖未知）

```
"<已入库的原句>" 完整版
"<已入库的原句>" 下一句
"<已入库的原句>" 出处
"<已入库的原句>" 什么梗
coke 还有哪些梗
coke 梗 大全 2024
coke 梗 大全 2025
```

## 平台限定

```
site:douyin.com coke老师
site:bilibili.com coke老师 语录
site:weibo.com coke老师 语录
site:zhihu.com coke老师
site:tieba.baidu.com coke
site:xiaohongshu.com coke 语录
site:jikipedia.com coke
site:gengbaike.cn coke
```

## 高危混淆（采集时要排除）

- Coca-Cola 可口可乐相关英文结果（"coke quotes" 会命中可乐名言）
- 同名音乐人/品牌/其他 coke 账号
- 禁毒相关的 "coke" 英文含义

判定：中文语境 + 出现「火影」「老弟」「痞」「抖音」任一，才可能是目标。
