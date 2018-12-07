#!/usr/bin/env python
# -*- coding=utf-8 -*-

import happybase


def ParserGB(strMsg):
    #低字节放在前面的
    #4040 2E00 0001 120118133907 010101010101 020202020202 1400 02 0200120206101E12010160010000000400020101 D5 2323
    if strMsg[:4] == "4040" and strMsg[-4:] == "2323":
        
        #con = happybase.Connection('localhost')
        con = happybase.Connection('47.97.9.12')
        con.open()

        #con.delete_table('FireMsgGB',disable=True)

        if  b'FireMsgGB' not in con.tables():
            msg = con.create_table('FireMsgGB',{"message":{}})
        else:
            msg = con.table('FireMsgGB')

        #BNo = strMsg[4:8]                                           #业务流水号
        BNo = strMsg[6:8]+strMsg[4:6]                                           #业务流水号(20180312版本,两个字节,低字节先传送)
        MasterProtocolVer = strMsg[8:10]                            #协议版本主版本号
        UserProtocolVer = strMsg[10:12]                             #协议版本用户版本号
        SendDate = strMsg[12:24]                                    #时间标签
        OriginalAddr = strMsg[24:36]                                #源地址
        DestinationAddr = strMsg[36:48]                             #目的地址
        AppDataLength = int(strMsg[50:52] + strMsg[48:50],16) * 2   #应用数据单元长度(2个字节,低字节先传)
        Command = strMsg[52:54]                                     #命令字节
        AppDataEnd = 54+AppDataLength
        AppData = strMsg[54:AppDataEnd]                             #应用数据单元
        Checksum = strMsg[AppDataEnd:AppDataEnd+2]                  #校验和
        print(BNo,MasterProtocolVer,UserProtocolVer,SendDate,OriginalAddr,DestinationAddr,AppDataLength,Command,AppData,Checksum)
       
        #应用数据单元解析开始
        #0200 120206101E12 01 01 60 01000000 0400 020101
        AppTypeFlag = int(AppData[2:4] + AppData[:2])               #数据属性标志；类型标志定义
       
        if AppTypeFlag == 1:        #上传建筑消防设施系统状态
            AppStatusDate = AppData[4:16]                               #状态时间
            AppSysType = AppData[16:18]                                 #系统类型
            AppSysAddr = AppData[18:20]                                 #系统地址
            AppSysStatus = AppData[20:24]                               #系统状态

            AddrRegionNo = AppData[24:26]                               #小区编号
            AddrBuilderNo = AppData[26:28]                              #楼号
            AddrFloorNo = AppData[28:30]                                #层号

            AppSysStatusBin = ("0000000000000000" + bin(int(AppSysStatus))[2:])[-14:]

            bit13 = AppSysStatusBin[0:1]    #1复位          0正常
            bit12 = AppSysStatusBin[1:2]    #1配置改变      0无配置改变
            bit11 = AppSysStatusBin[2:3]    #1手动状态      0自动状态
            bit10 = AppSysStatusBin[3:4]    #1总线故障      0总线正常
            bit9 = AppSysStatusBin[4:5]     #1备电故障      0备电正常
            bit8 = AppSysStatusBin[5:6]     #1主电故障      0主电正常
            bit7 = AppSysStatusBin[6:7]     #1延时状态      0未延时
            bit6 = AppSysStatusBin[7:8]     #1反馈          0无反馈
            bit5 = AppSysStatusBin[8:9]     #1启动（开启）   0停止（关闭）
            bit4 = AppSysStatusBin[9:10]    #1监管    0无监管
            bit3 = AppSysStatusBin[10:11]   #1屏蔽    0无屏蔽
            bit2 = AppSysStatusBin[11:12]   #1故障    0无故障
            bit1 = AppSysStatusBin[12:13]   #1火警    0无火警
            bit0 = AppSysStatusBin[13:14]   #1正常运行状态    0测试状态

            data = {
                b"message:BNo": str(BNo),              
                b"message:MasterProtocolVer": str(MasterProtocolVer),               
                b"message:UserProtocolVer": str(UserProtocolVer), 
                b"message:SendDate": str(SendDate),      
                b"message:OriginalAddr": str(OriginalAddr),            
                b"message:DestinationAddr": str(DestinationAddr),            
                b"message:AppTypeFlag": str(AppTypeFlag),   
                b"message:AppStatusDate": str(AppStatusDate),
                b"message:AppSysType": str(AppSysType),
                b"message:AppSysAddr": str(AppSysAddr),                
                b"message:AddrRegionNo": str(AddrRegionNo),
                b"message:AddrBuilderNo": str(AddrBuilderNo),
                b"message:AddrFloorNo": str(AddrFloorNo),
                b"message:SysStatus_13": str(bit13),
                b"message:SysStatus_12": str(bit12),
                b"message:SysStatus_11": str(bit11),
                b"message:SysStatus_10": str(bit10),
                b"message:SysStatus_9": str(bit9),
                b"message:SysStatus_8": str(bit8),
                b"message:PartStatus_7": str(bit7),
                b"message:PartStatus_6": str(bit6),
                b"message:PartStatus_5": str(bit5),
                b"message:PartStatus_4": str(bit4),
                b"message:PartStatus_3": str(bit3),
                b"message:PartStatus_2": str(bit2),
                b"message:PartStatus_1": str(bit1),
                b"message:PartStatus_0": str(bit0),
            }

            bat = msg.batch()
            bat.put(BNo, data)
            bat.send()

        elif AppTypeFlag == 2:      #上传建筑消防设施部件运行状态            
            AppStatusDate = AppData[4:16]                               #状态时间
            AppSysType = AppData[16:18]                                 #系统类型
            AppSysAddr = AppData[18:20]                                 #系统地址
            AppPartType = AppData[20:22]                                #部件类型
            AppPartAddr = AppData[22:30]                                #部件地址
            AppPartStatus = AppData[30:34]                              #部件状态

            AddrRegionNo = AppData[34:36]                               #小区编号
            AddrBuilderNo = AppData[36:38]                              #楼号
            AddrFloorNo = AppData[38:40]                                #层号

            #010160分别为系统类型、系统地址、部件类型
            #01000000部件地址
            #0400部件状态
            #020101 小区编号，楼号，层号
            #系统类型参考GB里的表4，部件类型参考表5

            print(AppTypeFlag,AppStatusDate,AppSysType,AppSysAddr,AppPartType,AppPartAddr,AppPartStatus,AddrRegionNo,AddrBuilderNo,
            AddrFloorNo)

            AppPartStatusBin = ("000000000" + bin(int(AppPartStatus))[2:])[-9:]
            
            bit8 = AppPartStatusBin[0:1]    #1电源故障  0电源正常
            bit7 = AppPartStatusBin[1:2]    #1延时状态  0未延时
            bit6 = AppPartStatusBin[2:3]    #1反馈      0无反馈
            bit5 = AppPartStatusBin[3:4]    #1启动（开启）   0停止（关闭）
            bit4 = AppPartStatusBin[4:5]    #1监管    0无监管
            bit3 = AppPartStatusBin[5:6]    #1屏蔽    0无屏蔽
            bit2 = AppPartStatusBin[6:7]    #1故障    0无故障
            bit1 = AppPartStatusBin[7:8]    #1火警    0无火警
            bit0 = AppPartStatusBin[8:9]    #1正常运行状态    0测试状态
            print(AppPartStatusBin,bit8,bit7,bit6,bit5,bit4,bit3,bit2,bit1,bit0)


            data = {
                b"message:BNo": str(BNo),              
                b"message:MasterProtocolVer": str(MasterProtocolVer),               
                b"message:UserProtocolVer": str(UserProtocolVer), 
                b"message:SendDate": str(SendDate),      
                b"message:OriginalAddr": str(OriginalAddr),            
                b"message:DestinationAddr": str(DestinationAddr),            
                b"message:AppTypeFlag": str(AppTypeFlag),   
                b"message:AppStatusDate": str(AppStatusDate),
                b"message:AppSysType": str(AppSysType),
                b"message:AppSysAddr": str(AppSysAddr),
                b"message:AppPartType": str(AppPartType),
                b"message:AppPartAddr": str(AppPartAddr),                
                b"message:AddrRegionNo": str(AddrRegionNo),
                b"message:AddrBuilderNo": str(AddrBuilderNo),
                b"message:AddrFloorNo": str(AddrFloorNo),
                b"message:PartStatus_8": str(bit8),
                b"message:PartStatus_7": str(bit7),
                b"message:PartStatus_6": str(bit6),
                b"message:PartStatus_5": str(bit5),
                b"message:PartStatus_4": str(bit4),
                b"message:PartStatus_3": str(bit3),
                b"message:PartStatus_2": str(bit2),
                b"message:PartStatus_1": str(bit1),
                b"message:PartStatus_0": str(bit0),
            }

            bat = msg.batch()
            bat.put(BNo, data)
            bat.send()

        elif AppTypeFlag == 3:  #上传建筑消防设施部件模拟量值
            pass
        elif AppTypeFlag == 4:  #上传建筑消防设施操作信息
            AppStatusDate = AppData[4:16]                               #状态时间
            AppSysType = AppData[16:18]                                 #系统类型
            AppSysAddr = AppData[18:20]                                 #系统地址
            AppOperateFlag = AppData[20:22]                             #操作标志
            AppOperatorNo = AppData[22:24]                              #操作员编号

            AddrRegionNo = AppData[24:26]                               #小区编号
            AddrBuilderNo = AppData[26:28]                              #楼号
            AddrFloorNo = AppData[28:30]                                #层号

            AppOperateFlagBin = ("00000000" + bin(int(AppOperateFlag))[2:])[-8:]
            bit7 = AppOperateFlagBin[0:1]    #保留
            bit6 = AppOperateFlagBin[1:2]    #1测试        0无操作
            bit5 = AppPartStatusBin[2:3]     #1确认        0无操作
            bit4 = AppPartStatusBin[3:4]     #1自检        0无操作
            bit3 = AppPartStatusBin[4:5]     #1警情消除    0无操作
            bit2 = AppPartStatusBin[5:6]     #1手动报警    0无操作
            bit1 = AppPartStatusBin[6:7]     #1消音        0无操作
            bit0 = AppPartStatusBin[7:8]     #1复位        0无操作


            data = {
                b"message:BNo": str(BNo),              
                b"message:MasterProtocolVer": str(MasterProtocolVer),               
                b"message:UserProtocolVer": str(UserProtocolVer), 
                b"message:SendDate": str(SendDate),      
                b"message:OriginalAddr": str(OriginalAddr),            
                b"message:DestinationAddr": str(DestinationAddr),            
                b"message:AppTypeFlag": str(AppTypeFlag),   
                b"message:AppStatusDate": str(AppStatusDate),
                b"message:AppSysType": str(AppSysType),
                b"message:AppSysAddr": str(AppSysAddr),
                b"message:AppOperatorNo": str(AppOperatorNo),                         
                b"message:AddrRegionNo": str(AddrRegionNo),
                b"message:AddrBuilderNo": str(AddrBuilderNo),
                b"message:AddrFloorNo": str(AddrFloorNo),
                b"message:PartStatus_7": str(bit7),
                b"message:PartStatus_6": str(bit6),
                b"message:PartStatus_5": str(bit5),
                b"message:PartStatus_4": str(bit4),
                b"message:PartStatus_3": str(bit3),
                b"message:PartStatus_2": str(bit2),
                b"message:PartStatus_1": str(bit1),
                b"message:PartStatus_0": str(bit0),
            }

            bat = msg.batch()
            bat.put(BNo, data)
            bat.send()

        elif AppTypeFlag == 5:  #上传建筑消防设施软件版本
            AppStatusDate = AppData[4:16]                               #状态时间
            AppSysType = AppData[16:18]                                 #系统类型
            AppSysAddr = AppData[18:20]                                 #系统地址
            AppMasterVer = AppData[20:22]                               #主版本号
            AppSubVer = AppData[22:24]                                  #次版本号

            AddrRegionNo = AppData[24:26]                               #小区编号
            AddrBuilderNo = AppData[26:28]                              #楼号
            AddrFloorNo = AppData[28:30]                                #层号
            
            data = {
                b"message:BNo": str(BNo),              
                b"message:MasterProtocolVer": str(MasterProtocolVer),               
                b"message:UserProtocolVer": str(UserProtocolVer), 
                b"message:SendDate": str(SendDate),      
                b"message:OriginalAddr": str(OriginalAddr),            
                b"message:DestinationAddr": str(DestinationAddr),            
                b"message:AppTypeFlag": str(AppTypeFlag),   
                b"message:AppStatusDate": str(AppStatusDate),
                b"message:AppSysType": str(AppSysType),
                b"message:AppSysAddr": str(AppSysAddr),
                b"message:AppMasterVer": str(AppMasterVer),    
                b"message:AppSubVer": str(AppSubVer),                    
                b"message:AddrRegionNo": str(AddrRegionNo),
                b"message:AddrBuilderNo": str(AddrBuilderNo),
                b"message:AddrFloorNo": str(AddrFloorNo),
            }

            bat = msg.batch()
            bat.put(BNo, data)
            bat.send()
        elif AppTypeFlag == 6:  #上传建筑消防设施系统配置情况
            AppStatusDate = AppData[4:16]                               #状态时间
            AppSysType = AppData[16:18]                                 #系统类型
            AppSysAddr = AppData[18:20]                                 #系统地址
            AppSysDescLength = AppData[20:22]                           #系统说明长度

            posDesc = 22+AppSysDescLength
            AppSysDesc = AppData[22:posDesc]                            #系统配置说明

            AddrRegionNo = AppData[posDesc:posDesc+2]                   #小区编号
            AddrBuilderNo = AppData[posDesc+2:posDesc+4]                #楼号
            AddrFloorNo = AppData[posDesc +4:posDesc+6]                 #层号

            data = {
                b"message:BNo": str(BNo),              
                b"message:MasterProtocolVer": str(MasterProtocolVer),               
                b"message:UserProtocolVer": str(UserProtocolVer), 
                b"message:SendDate": str(SendDate),      
                b"message:OriginalAddr": str(OriginalAddr),            
                b"message:DestinationAddr": str(DestinationAddr),            
                b"message:AppTypeFlag": str(AppTypeFlag),   
                b"message:AppStatusDate": str(AppStatusDate),
                b"message:AppSysType": str(AppSysType),
                b"message:AppSysAddr": str(AppSysAddr),
                b"message:AppSysDesc": str(AppSysDesc),               
                b"message:AddrRegionNo": str(AddrRegionNo),
                b"message:AddrBuilderNo": str(AddrBuilderNo),
                b"message:AddrFloorNo": str(AddrFloorNo),
            }

            bat = msg.batch()
            bat.put(BNo, data)
            bat.send()

        elif AppTypeFlag == 7:  #上传建筑消防设施部件配置情况
            AppStatusDate = AppData[4:16]                               #状态时间
            AppSysType = AppData[16:18]                                 #系统类型
            AppSysAddr = AppData[18:20]                                 #系统地址
            AppPartType = AppData[20:22]                                #部件类型
            AppPartAddr = AppData[22:30]                                #部件地址
            AppPartDesc = AppData[30:92]                                #部件说明

            AddrRegionNo = AppData[92:94]                               #小区编号
            AddrBuilderNo = AppData[94:96]                              #楼号
            AddrFloorNo = AppData[96:98]                                #层号

            data = {
                b"message:BNo": str(BNo),              
                b"message:MasterProtocolVer": str(MasterProtocolVer),               
                b"message:UserProtocolVer": str(UserProtocolVer), 
                b"message:SendDate": str(SendDate),      
                b"message:OriginalAddr": str(OriginalAddr),            
                b"message:DestinationAddr": str(DestinationAddr),            
                b"message:AppTypeFlag": str(AppTypeFlag),   
                b"message:AppStatusDate": str(AppStatusDate),
                b"message:AppSysType": str(AppSysType),
                b"message:AppSysAddr": str(AppSysAddr),
                b"message:AppPartType": str(AppPartType),               
                b"message:AppPartAddr": str(AppPartAddr),               
                b"message:AppPartDesc": str(AppPartDesc),
                b"message:AddrRegionNo": str(AddrRegionNo),
                b"message:AddrBuilderNo": str(AddrBuilderNo),
                b"message:AddrFloorNo": str(AddrFloorNo),
            }

            bat = msg.batch()
            bat.put(BNo, data)
            bat.send()
            
        elif AppTypeFlag == 8:  #上传建筑消防设施系统时间
            pass
        elif AppTypeFlag == 21: #上传用户信息传输装置运行状态
            pass
        elif AppTypeFlag == 24: #上传用户信息传输装置操作信息
            pass
        elif AppTypeFlag == 25: #上传用户信息传输装置软件版本
            pass
        elif AppTypeFlag == 26: #上传用户信息传输装置配置情况
            pass
        elif AppTypeFlag == 28: #上传用户信息传输装置系统时间
            pass
        elif AppTypeFlag == 61: #读建筑消防设施系统状态
            pass
        elif AppTypeFlag == 62: #读建筑消防设施部件运行状态
            pass
        elif AppTypeFlag == 63: #读建筑消防设施部件模拟量值
            pass
        elif AppTypeFlag == 64: #读建筑消防设施操作信息
            pass
        elif AppTypeFlag == 65: #读建筑消防设施软件版本
            pass
        elif AppTypeFlag == 66: #读建筑消防设施系统配置情况
            pass
        elif AppTypeFlag == 67: #读建筑消防设施部件配置情况
            pass
        elif AppTypeFlag == 68: #读建筑消防设施系统时间
            pass
        elif AppTypeFlag == 81: #读用户信息传输装备运行状态
            pass
        elif AppTypeFlag == 84: #读用户信息传输装置操作信息记录
            pass
        elif AppTypeFlag == 85: #读用户信息传输装置软件版本
            pass
        elif AppTypeFlag == 86: #读用户信息传输装置配置情况
            pass
        elif AppTypeFlag == 88: #读用户信息传输装置系统时间
            pass
        elif AppTypeFlag == 89: #初始化用户信息传输装置
            pass
        elif AppTypeFlag == 90: #同步用户信息传输装置时钟
            pass
        elif AppTypeFlag == 91: #查岗命令
            pass
        
        con.close()
            
            
            
            
            
            
            
            
            
            
            
            
            
        
            
            
            
            
            
            
            
            
            
            
            
            
            
    else:
        print("非法消息！")

if __name__ == "__main__":
    ParserGB("40402E0000011201181339070101010101010202020202021400020200120206101E12010160010000000400020101D52323")
