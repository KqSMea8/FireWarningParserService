#!/usr/bin/env python
# -*- coding=utf-8 -*-
import happybase
import time
import random

con = happybase.Connection('47.97.9.12')

con.open()

#con.delete_table('article', disable = True)


# 上行消息格式：24字节（现在不传输电话号码，应该只有18个字节）
# 起始符(1)+事件类型(1)+电话号码(6)+收发器ID(4)+信息标识(1)+机号(1)+报警信息(8) +校验和(1)+结束符(1)
# 例子：0D 10 00000001 10 01 0000000000000000 22 FF
# 下行消息格式：24字节（现在不传输电话号码，应该只有18个字节）
# 起始符(1)+事件类型(1)+电话号码(6)+收发器ID(4)+信息标识(1)+设置信息(9)+校验和(1)+结束符(1)




if  b'FireMsg' not in con.tables():
    msg = con.create_table('FireMsg',{"message":{}})
else:
    msg = con.table('FireMsg')


Event = (0x10,0x20,0x30,0x31,0x32,0x40,0x41,0x42,0x43,0x44,0x50,0x60,0x61,0x62,0x65,0x66)
InfoFlag = (0x09,0x10,0x11,0x12,0x13,0x40,0x48,0x50,0x51,0x52,0x53,0x54,0x55,0x56,0x57,0x95,0x96,0x9C,0x9D)

#批量插入数据
bat = msg.batch()
for i in range(10000):
    timestamp = time.time() + i
    MsgType = 0x0d if i % 2 == 0 else 0xd0
    rowkey = "message" + str(timestamp * 1000000)
    data = {
            b"message:MsgType": str(MsgType),              #消息类型（上行、下行）
            b"message:Event": str(0x10),                #事件类型
            b"message:TelNum": str(random.randint(100000,999999)), #电话号码
            b"message:SerDesID": str(random.randint(1,10000)),     #收发器ID
            b"message:InfoFlag": str(InfoFlag[random.randint(0,len(InfoFlag)-1)]),             #信息标识
            b"message:MachineNo": str(random.randint(100,100000)),            #机号
            b"message:Warning": 'Warning No ' + str(random.randint(1,100000)),              #报警信息
        }
    bat.put(rowkey, data)
    if i > 0 and i % 1000 == 0:#1000条一批次
        bat.send()        
bat.send()

# count = 0
# for key, data in msg.scan():# filter="SingleColumnValueFilter('basic', 'ArticleTypeID', =, 'substring:1')"):
#     print(key, data)
#     count += 1

# print(count)
con.close()

print('Done')