# qmt-knowledge-skill 安全加固 diff

**基线 commit**: `4dbdc8036baa43fdfa39784b632dd25382a5e68f`

**改动**: P0-1 账号占位符 (15 处) + P0-2 quickTrade=2 fence 邻接标记 (19 处)

**范围**: 仅改知识文档示例，未改任何交易函数签名或 quickTrade 参数值

```diff
diff --git "a/src/knowledge__01-\345\205\245\351\227\250__\345\277\253\351\200\237\345\274\200\345\247\213.md" "b/src/knowledge__01-\345\205\245\351\227\250__\345\277\253\351\200\237\345\274\200\345\247\213.md"
index e4d59d3..f4be5f2 100644
--- "a/src/knowledge__01-\345\205\245\351\227\250__\345\277\253\351\200\237\345\274\200\345\247\213.md"
+++ "b/src/knowledge__01-\345\205\245\351\227\250__\345\277\253\351\200\237\345\274\200\345\247\213.md"
@@ -189,6 +189,7 @@ def handlebar(C):
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 
diff --git "a/src/knowledge__02-API__\344\272\244\346\230\223\345\207\275\346\225\260.md" "b/src/knowledge__02-API__\344\272\244\346\230\223\345\207\275\346\225\260.md"
index a9c77d2..807c05d 100644
--- "a/src/knowledge__02-API__\344\272\244\346\230\223\345\207\275\346\225\260.md"
+++ "b/src/knowledge__02-API__\344\272\244\346\230\223\345\207\275\346\225\260.md"
@@ -32,7 +32,7 @@ passorder(
 passorder(
     2 #opType 操作号
     , 1101 #orderType 组合方式
-    , '1000044' #accountid 资金账号
+    , '<ACCOUNT_ID>' #accountid 资金账号（已脱敏）
     , 'cu2403.SF' #orderCode 品种代码
     , 14 #prType 报价类型
     , 0.0 #price 价格
@@ -232,7 +232,7 @@ userparam = {
     "MaxOrderCount": 20,
     "SuperPriceType": 1,
     "SuperPriceValue": 1.12}
-accid = '918800000818'  #资金账号
+accid = '<ACCOUNT_ID>'  #资金账号（已脱敏）
 algo_passorder(23,1101,accid,'000001.SZ',5,15,1000,'',1,'strReMark',userparam,ContextInfo)
 #表示修改算法交易的最大委托次数为20,单笔下单基准类型为按价格类型超价,单笔超价1.12元,其他参数同函数交易参数中设置
 ```
@@ -292,6 +292,7 @@ smart_algo_passorder(opType,orderType,accountid,orderCode,prType,price,volume,st
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 
@@ -369,6 +370,7 @@ get_smart_algo_param(algoList)
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 
@@ -464,7 +466,7 @@ python返回值
 
 
 def init(ContextInfo):
-    ContextInfo.accid = '6000000248'
+    ContextInfo.accid = '<ACCOUNT_ID>'
 
 def handlebar(ContextInfo):
     if ContextInfo.is_last_bar():
@@ -514,7 +516,7 @@ python
 '''
 
 def init(ContextInfo):
-    ContextInfo.accid = '6000000248'
+    ContextInfo.accid = '<ACCOUNT_ID>'
 
 def handlebar(ContextInfo):
     # 获取当前客户端所有的任务
@@ -564,7 +566,7 @@ python
 '''
 
 def init(ContextInfo):
-    ContextInfo.accid = '6000000248'    
+    ContextInfo.accid = '<ACCOUNT_ID>'    
 
 def handlebar(ContextInfo):
     
@@ -615,7 +617,7 @@ python
 '''
 
 def init(ContextInfo):
-    ContextInfo.accid = '6000000248'    
+    ContextInfo.accid = '<ACCOUNT_ID>'    
 def handlebar(ContextInfo):
     if ContextInfo.is_last_bar():
         # 获取当前客户端所有的任务
@@ -652,6 +654,7 @@ print( get_basket('basket1') )
 
 **示例：**
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 table=[
     {'stock':'600000.SH','weight':0.11,'quantity':100,'optType':23},
@@ -842,7 +845,7 @@ def init(ContextInfo):
 
 ```
 def init(ContextInfo):
-    ContextInfo.accid="10000001"# 返回新股新债信息
+    ContextInfo.accid="<ACCOUNT_ID>"# 返回新股新债信息
     purchase_limit=get_new_purchase_limit(ContextInfo.accid)
 ```
 
@@ -878,7 +881,7 @@ python返回值
 
 ```
 def init(ContextInfo):
-    ContextInfo.accid = '6000000248'
+    ContextInfo.accid = '<ACCOUNT_ID>'
 
 def handlebar(ContextInfo):
     orderid = get_last_order_id(ContextInfo.accid, 'stock', 'order')
@@ -940,7 +943,7 @@ String，委托号，如果没找到返回 '-1'。
 
 ```
 def init(ContextInfo):
-    ContextInfo.accid = '6000000248'
+    ContextInfo.accid = '<ACCOUNT_ID>'
 
 def handlebar(ContextInfo):
     orderid = get_last_order_id(ContextInfo.accid, 'stock', 'order')
@@ -978,7 +981,7 @@ def show_data(data):
     return tdata
 
 def handlebar(ContextInfo): 
-    obj = get_assure_contract('6000000248')
+    obj = get_assure_contract('<ACCOUNT_ID>')
     for i in obj[:3]:
 		print(show_data(i))
 
@@ -993,7 +996,7 @@ def handlebar(ContextInfo):
 'm_eFinStatus': 48, # 融资状态
 'm_eSloStatus': 48, # 融券状态
 'm_nPlatformID': 10064,  # 平台号
-'m_strAccountID': '95000857',  # 资金账号
+'m_strAccountID': '<MASKED>',  # 资金账号
 'm_strBrokerID': '003', # 经纪公司编号
 'm_strBrokerName': '光大证券信用',  # 证券公司
 'm_strExchangeID': 'SH', # 交易所
@@ -1090,7 +1093,7 @@ python返回值
 import time
 
 def init(ContextInfo):
-	ContextInfo.accid='200133'
+	ContextInfo.accid='<ACCOUNT_ID>'
 	
 def handlebar(ContextInfo):
 	if ContextInfo.is_last_bar():
@@ -1173,7 +1176,7 @@ def init(ContextInfo):
     """初始化：设置账号、初始化全局变量、注册定时器"""
     
     # 设置两融账号（必须先在QMT客户端登录该账号）
-    ContextInfo.accid = '200133'
+    ContextInfo.accid = '<ACCOUNT_ID>'
     
     # 记录上次查询时间戳，用于控制查询间隔（>=180秒）
     g.last_query_time = 0
@@ -1454,7 +1457,7 @@ list(\[ CStkUnclosedCompacts, ... \]) 负债列表，CStkUnclosedCompacts属性
 **示例：**
 
 ```
-get_unclosed_compacts('6000000248', 'CREDIT')
+get_unclosed_compacts('<ACCOUNT_ID>', 'CREDIT')
 ```
 
 ### get\_closed\_compacts-获取已了结负债合约明细
@@ -1510,7 +1513,7 @@ list(\[ CStkUnclosedCompacts, ... \]) 负债列表，CStkUnclosedCompacts属性
 **示例：**
 
 ```
-get_closed_compacts('6000000248', 'CREDIT')
+get_closed_compacts('<ACCOUNT_ID>', 'CREDIT')
 ```
 
 ## 其他交易函数（仅回测可用）
@@ -1561,13 +1564,13 @@ get_closed_compacts('6000000248', 'CREDIT')
 ```
 def handlebar(ContextInfo):
     # 按最新价下 1 手买入
-    order_lots('000002.SZ', 1, ContextInfo, '600000248')
+    order_lots('000002.SZ', 1, ContextInfo, '<ACCOUNT_ID>')
 
     # 用对手价下 1 手卖出
-    order_lots('000002.SZ', -1, 'COMPETE', ContextInfo, '600000248')
+    order_lots('000002.SZ', -1, 'COMPETE', ContextInfo, '<ACCOUNT_ID>')
 
     # 用指定价 37.5 下 2 手卖出
-    order_lots('000002.SZ', -2, 'fix', 37.5, ContextInfo, '600000248')
+    order_lots('000002.SZ', -2, 'fix', 37.5, ContextInfo, '<ACCOUNT_ID>')
 ```
 
 ### order\_value-指定价值交易
diff --git "a/src/knowledge__02-API__\346\210\220\344\272\244\345\233\236\346\212\245\345\256\236\346\227\266\344\270\273\346\216\250\345\207\275\346\225\260.md" "b/src/knowledge__02-API__\346\210\220\344\272\244\345\233\236\346\212\245\345\256\236\346\227\266\344\270\273\346\216\250\345\207\275\346\225\260.md"
index 81bc115..289e568 100644
--- "a/src/knowledge__02-API__\346\210\220\344\272\244\345\233\236\346\212\245\345\256\236\346\227\266\344\270\273\346\216\250\345\207\275\346\225\260.md"
+++ "b/src/knowledge__02-API__\346\210\220\344\272\244\345\233\236\346\212\245\345\256\236\346\227\266\344\270\273\346\216\250\345\207\275\346\225\260.md"
@@ -33,6 +33,7 @@
 
 示例返回值
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 def show_data(data):
@@ -89,6 +90,7 @@ def account_callback(ContextInfo, accountInfo):
 
 示例返回值
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 def show_data(data):
@@ -117,10 +119,10 @@ def task_callback(ContextInfo, taskInfo):
 ```
 
 ```
-{'m_3rdPartyTradeParam': '', 'm_cancelTime': 2147483647, 'm_dFixPrice': 9.82, 'm_eOperationType': 18, 'm_eOrderType': 0, 'm_ePriceType': 5, 'm_eStatus': 3, 'm_endTime': 2147483647, 'm_nBusinessNum': 0, 'm_nGroupId': 11, 'm_nNum': 100, 'm_nTaskId': '11', 'm_script': '', 'm_startTime': 1708420476, 'm_stockCode': '000001.SZ', 'm_strAccountID': '2000567', 'm_strMsg': '9.8200全部委托! 报价行情已8076秒未更新!', 'm_strRemark': '投资备注'}
-{'m_3rdPartyTradeParam': '', 'm_cancelTime': 2147483647, 'm_dFixPrice': 9.82, 'm_eOperationType': 18, 'm_eOrderType': 0, 'm_ePriceType': 5, 'm_eStatus': 3, 'm_endTime': 2147483647, 'm_nBusinessNum': 100, 'm_nGroupId': 11, 'm_nNum': 100, 'm_nTaskId': '11', 'm_script': '', 'm_startTime': 1708420476, 'm_stockCode': '000001.SZ', 'm_strAccountID': '2000567', 'm_strMsg': '9.8200全部委托! 报价行情已8076秒未更新!', 'm_strRemark': '投资备注'}
-{'m_3rdPartyTradeParam': '', 'm_cancelTime': 2147483647, 'm_dFixPrice': 9.82, 'm_eOperationType': 18, 'm_eOrderType': 0, 'm_ePriceType': 5, 'm_eStatus': 7, 'm_endTime': 1708420476, 'm_nBusinessNum': 100, 'm_nGroupId': 11, 'm_nNum': 100, 'm_nTaskId': '11', 'm_script': '', 'm_startTime': 1708420476, 'm_stockCode': '000001.SZ', 'm_strAccountID': '2000567', 'm_strMsg': '任务完成', 'm_strRemark': '投资备注'}
-{'m_3rdPartyTradeParam': '', 'm_cancelTime': 2147483647, 'm_dFixPrice': 9.82, 'm_eOperationType': 18, 'm_eOrderType': 0, 'm_ePriceType': 5, 'm_eStatus': 7, 'm_endTime': 1708420476, 'm_nBusinessNum': 100, 'm_nGroupId': 11, 'm_nNum': 100, 'm_nTaskId': '11', 'm_script': '', 'm_startTime': 1708420476, 'm_stockCode': '000001.SZ', 'm_strAccountID': '2000567', 'm_strMsg': '任务完成', 'm_strRemark': '投资备注'}
+{'m_3rdPartyTradeParam': '', 'm_cancelTime': 2147483647, 'm_dFixPrice': 9.82, 'm_eOperationType': 18, 'm_eOrderType': 0, 'm_ePriceType': 5, 'm_eStatus': 3, 'm_endTime': 2147483647, 'm_nBusinessNum': 0, 'm_nGroupId': 11, 'm_nNum': 100, 'm_nTaskId': '11', 'm_script': '', 'm_startTime': 1708420476, 'm_stockCode': '000001.SZ', 'm_strAccountID': '<MASKED>', 'm_strMsg': '9.8200全部委托! 报价行情已8076秒未更新!', 'm_strRemark': '投资备注'}
+{'m_3rdPartyTradeParam': '', 'm_cancelTime': 2147483647, 'm_dFixPrice': 9.82, 'm_eOperationType': 18, 'm_eOrderType': 0, 'm_ePriceType': 5, 'm_eStatus': 3, 'm_endTime': 2147483647, 'm_nBusinessNum': 100, 'm_nGroupId': 11, 'm_nNum': 100, 'm_nTaskId': '11', 'm_script': '', 'm_startTime': 1708420476, 'm_stockCode': '000001.SZ', 'm_strAccountID': '<MASKED>', 'm_strMsg': '9.8200全部委托! 报价行情已8076秒未更新!', 'm_strRemark': '投资备注'}
+{'m_3rdPartyTradeParam': '', 'm_cancelTime': 2147483647, 'm_dFixPrice': 9.82, 'm_eOperationType': 18, 'm_eOrderType': 0, 'm_ePriceType': 5, 'm_eStatus': 7, 'm_endTime': 1708420476, 'm_nBusinessNum': 100, 'm_nGroupId': 11, 'm_nNum': 100, 'm_nTaskId': '11', 'm_script': '', 'm_startTime': 1708420476, 'm_stockCode': '000001.SZ', 'm_strAccountID': '<MASKED>', 'm_strMsg': '任务完成', 'm_strRemark': '投资备注'}
+{'m_3rdPartyTradeParam': '', 'm_cancelTime': 2147483647, 'm_dFixPrice': 9.82, 'm_eOperationType': 18, 'm_eOrderType': 0, 'm_ePriceType': 5, 'm_eStatus': 7, 'm_endTime': 1708420476, 'm_nBusinessNum': 100, 'm_nGroupId': 11, 'm_nNum': 100, 'm_nTaskId': '11', 'm_script': '', 'm_startTime': 1708420476, 'm_stockCode': '000001.SZ', 'm_strAccountID': '<MASKED>', 'm_strMsg': '任务完成', 'm_strRemark': '投资备注'}
 
 ```
 
@@ -146,6 +148,7 @@ def task_callback(ContextInfo, taskInfo):
 
 示例返回值
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 def show_data(data):
@@ -199,6 +202,7 @@ def order_callback(ContextInfo, orderInfo):
 
 示例返回值
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 def show_data(data):
@@ -252,6 +256,7 @@ def deal_callback(ContextInfo, dealInfo):
 
 示例返回值
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 def show_data(data):
@@ -307,6 +312,7 @@ def position_callback(ContextInfo, positionInfo):
 
 示例返回值
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 def show_data(data):
diff --git "a/src/knowledge__02-API__\347\263\273\347\273\237\345\207\275\346\225\260.md" "b/src/knowledge__02-API__\347\263\273\347\273\237\345\207\275\346\225\260.md"
index 19a81c4..5bdc773 100644
--- "a/src/knowledge__02-API__\347\263\273\347\273\237\345\207\275\346\225\260.md"
+++ "b/src/knowledge__02-API__\347\263\273\347\273\237\345\207\275\346\225\260.md"
@@ -87,6 +87,7 @@ def handlebar(ContextInfo):
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 
diff --git "a/src/knowledge__04-\347\244\272\344\276\213\344\270\216FAQ__\345\256\214\346\225\264\347\244\272\344\276\213.md" "b/src/knowledge__04-\347\244\272\344\276\213\344\270\216FAQ__\345\256\214\346\225\264\347\244\272\344\276\213.md"
index 3b0a51d..bd110c0 100644
--- "a/src/knowledge__04-\347\244\272\344\276\213\344\270\216FAQ__\345\256\214\346\225\264\347\244\272\344\276\213.md"
+++ "b/src/knowledge__04-\347\244\272\344\276\213\344\270\216FAQ__\345\256\214\346\225\264\347\244\272\344\276\213.md"
@@ -14,7 +14,7 @@ python
 #coding:gbk
 def init(C):
 	
-	r = get_assure_contract('123456789')
+	r = get_assure_contract('<ACCOUNT_ID>')
 	if len(r) == 0:
 		print('未取到担保明细')
 	else:
@@ -665,6 +665,7 @@ def handlebar(ContextInfo):
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 def init(C):
@@ -717,6 +718,7 @@ def handlebar(ContextInfo):
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 
@@ -791,6 +793,7 @@ python返回值
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 c = 0
@@ -850,6 +853,7 @@ def handlebar(ContextInfo):
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 
 #coding:gbk
@@ -912,6 +916,7 @@ def handlebar(C):
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 import time
@@ -947,6 +952,7 @@ def handlebar(C):
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 # encoding:gbk
 
@@ -1044,6 +1050,7 @@ def query_info(C):
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #coding:gbk
 
@@ -1060,6 +1067,7 @@ def after_init(C):
 
 python
 
+> 🚫 **quickTrade=2 高风险示例** — 历史 Bar 也会触发委托，请先在模拟环境验证
 ```
 #encoding:gbk
 
@@ -1235,7 +1243,7 @@ python
 #coding:gbk
 def init(C):
 	
-	r = get_assure_contract('123456789')
+	r = get_assure_contract('<ACCOUNT_ID>')
 	if len(r) == 0:
 		print('未取到担保明细')
 	else:

```
