# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-03-07 15:05:12
# @Last Modified by:   leonliang
# @Last Modified time: 2018-03-09 15:10:24
import time
import re
import json

data = {
    "BUSINESSNO" : "0001",
	"CENTERADDR" : "010101010101",
	"USERDEVICEADDR" : "020101010101",
	"APPDATABODY" : "0200120206101E12010160010000000400020101",
	"COMMAND" : "02"	
}

'''
----------------------------------------------------------------------------------
通用函数定义区域'''
def IntToHexStr(strInt,zeronumber=2):
	'''
	1,将十进制的数字转为二进制的数字并且保留去除标准十六进制表示中的"Ox"显示符号
	2,对于不满2位的数字在首位补0
	'''
	tempStr = ""
	tempIndexInt = 0
	tempStr = str(hex(strInt))
	tempIndexInt = tempStr.find("x")+1
	return (tempStr[tempIndexInt:]).zfill(zeronumber)

def ResortStr(strOrion,strSplit="",sort=1,subStrLen=2):
	'''
	字符串按照,subStrLen长度进行拆分
	分隔后的字符串按照进行排序,sort=1 为逆序,所有分隔字符组按照逆向进行排列,sort=0为正向排位
	同时用strSplit进行字符整体串联
	'''
	tempStr = ""
	retrunStr = ""
	tempStrLength = len(strOrion)
	tempStrModLength = tempStrLength%subStrLen
	if tempStrModLength>0 :
		tempStr = strOrion.zfill(tempStrModLength+tempStrLength)
	else :
		tempStr = strOrion

	rpattern = re.compile('.{'+str(subStrLen)+'}')
	b=re.findall(rpattern,tempStr) 
	if sort == 0:
		for i in range(len(b)):
			if i > 0  :
				retrunStr = retrunStr + strSplit + b[i]
			else :
				retrunStr = retrunStr + b[i]
	elif sort == 1:
		for i in range(len(b)):
			retrunStr = b[i] + strSplit + retrunStr
	return retrunStr

def GetHexStr(strHEX,sort=1):
	'''
	1,将十六进制的数字串转化为10进制的数字
	2,sort=1为原有的hex子串是逆向排位,低字节传输在前,高字节排序在后;sort=0为原有的hex子串为正向排位,高字节排序在前,低字节排序在后
	'''
	tempStr = ""
	returnStr = ""
	tempStrLength = len(strHEX)

	if tempStrLength>4 :
		print "数字长度超出定义范围,2字节以内"
	tempStr = ResortStr(strHEX,"",sort)
	returnStr = int(tempStr,16)

	'''if sort==1: 
		#tempStr = strHEX[2:]+strHEX[:2]
		tempStr = ResortStr(strHEX)
		returnStr = int(tempStr,16)
	elif sort==0:
		returnStr = int(strHEX,16)'''

	return (returnStr)

#testMsg = "40402E0000011201181339070101010101010202020202021400020200120206101E12010160010000000400020101D52323"
#print testMsg[24:36] 
'''
---------------------------------------------------------------------------------
数据准备区域'''

tempjson = json.loads(json.dumps(data))

'''通讯方式: 
控制命令为"01"(十进制),01(十六进制)---(监控中心->用户信息传输装置:监控中心--控制命令-->用户信息传输装置--确认-->监控中心);
信息上传为"05"(十进制),05(十六进制)---(用户信息传输装置->监控中心:用户信息传输装置--信息上传-->监控中心--接收确认-->用户信息传输装置);
信息查询为"10"(十进制),0A(十六进制)---(监控中心->用户信息传输装置:监控中心--信息查询请求-->用户信息传输装置--应答-->监控中心);
'''
COM_MOD_TYPE_STR = "01"

'''
业务流水号 2字节
默认通讯双发第一次建立网络连接时确定为0,业务发起方负责业务流水号的分配和回收保证业务续存期间业务流水号的唯一
在本次实现中:
	"控制命令"和"信息查询"的业务流水由"监控中心"负责管理;
	"信息上传"的业务流水由"用户信息传输装置"负责管理;
'''
BUSINESS_NO = tempjson.get("BUSINESSNO")									#Var变量

MASTER_PROTOCOL_VER = "01"                            	#协议版本主版本号

USER_PROTOCOL_Ver = "01"                             	#协议版本用户版本号

'''
#时间标签: 
秒 : 1位,0-59,本次案例为00[十六进制] / 00[十进制]
分 : 1位,0-59,本次案例为1E[十六进制] / 30[十进制]
时 : 1位,0-23,本次案例为12[十六进制] / 18[十进制]
日 : 1位,1-31,本次案例为05[十六进制] / 05[十进制]
月 : 1位,1-12,本次案例为03[十六进制] / 03[十进制]
年 : 1位,00-99,本次案例为12[十六进制] / 12[十进制](默认为20XX年)
'''

#SEND_DATE = "001E12050312"                                   `

localtime = time.localtime()
localyear =IntToHexStr(int(str(localtime[0])[-2:]))
localmonth = IntToHexStr(localtime[1])
localdate = IntToHexStr(localtime[2])
localhour = IntToHexStr(localtime[3])
localmin = IntToHexStr(localtime[4])
localsec = IntToHexStr(localtime[5])




#print "time.localtime() : %s" % time.localtime()
#print localyear+"/"+localmonth+"/"+localdate+" "+ localhour+":"+localmin+":"+localsec

'''
设备地址定义
源地址
目的地址
'''
CENTER_ADDR = tempjson.get("CENTERADDR") #"010101010101"								#Var变量
USERDEVICE_ADDR = tempjson.get("USERDEVICEADDR") #"020101010101"							#Var变量

#SOURCE_ADDR =  CENTER_ADDR                               	#源地址
#DEST_ADDR = USERDEVICE_ADDR                            	#目的地址

#应用数据单元
APPDATA_BODY = tempjson.get("APPDATABODY") #"0200120206101E12010160010000000400020101"	#Var变量

#应用数据单元长度, 1-1023
APPDATA_LENGTH = len(APPDATA_BODY)
APPDATA_LENGTH_HEX_STR = IntToHexStr(APPDATA_LENGTH,4)
#print str(APPDATA_LENGTH) +":"+ APPDATA_LENGTH_HEX_STR + ": " + str(GetHexStr(APPDATA_LENGTH_HEX_STR,1))
#print str(GetHexStr(APPDATA_LENGTH_HEX_STR,0))
APPDATA_LENGTH_HEX_STR_Resort =  ResortStr(APPDATA_LENGTH_HEX_STR)  #应用数据单元长度
#print   APPDATA_LENGTH_HEX_STR_Resort+":"+str(GetHexStr(APPDATA_LENGTH_HEX_STR_Resort))

'''
命令字节
00--预留
01--控制命令
02--发送数据
03--确认
04--请求
05--应答
06--否认
07-127---预留
128-255---用户自行定义
'''
COMMAND = tempjson.get("COMMAND") #"02"												#Var变量

print BUSINESS_NO+":"+COMMAND

'''
----------------------------------------------------------------------------------
应用函数区域'''
def CreateMsgGB(strMsg,strComModType,strBNo,strMProtVer,StrUProtVer,strSendDate,strCenterAddr,strDeviceAddr,strAppDataLen,strCommand,strAppData):
	'''
	#VerificationFlag确认校验是否通过,如果所有校验规则通过后无问题,则VerificationFlag为true,VerificationCode数组中存在唯一字符串"200"

	VerificationCode定义内容
	"200" : 验证正确
	"301" : 启动符,信息1,2两位不是固定值64(十进制),40(十六进制)
	"305" : 结束符,信息最末两位不是固定值35(十进制),23(十六进制)

	"501" : 发送标记时间与当前系统事件相距10秒以上,请确认应用时钟同步状态或者确认数据是否重发(国家标准超时时间不宜大于10秒)
	"601" : 平台该标识信息已经接受3次以上,请确认应用时钟同步状态或者确认相关应用响应确认服务是否正常(国家标准超时重发不宜大于3次)
	'''
	VerificationFlag = true
	VerificationCode = []
	#确认通讯模式
	ComModTypeStr = strComModType
	#启动符'@@' 2字节,数据包的第一、二字节,为固定值64,64(十进制)--40,40(十六进制)
	BeginStr = "4040"
	#结束符'##' 2字节,数据包的最后两个字节,为固定值35,35(十进制)--23,23(十六进制)
	EndStr = "2323"
	#业务流水号 2字节
	BNo = strBNo
	MasterProtocolVer = strMProtVer                            		#协议版本主版本号
	UserProtocolVer = StrUProtVer                             		#协议版本用户版本号
	SendDate = strSendDate                                    		#时间标签

	upperActions = ["02","04"]										#上行方向,从用户信息传输装置到监控中心的数据传输方向
	downActions =  ["01","03","04","05"]								#下行方向,从监控中心到用户信息传输装饰的数据传输方向
	if strCommand in downActions:
		strOriginalAddr = strCenterAddr
		strDestinationAddr = strDeviceAddr
	elif strCommand in upperActions:
		strOriginalAddr = strDeviceAddr
		strDestinationAddr = strCenterAddr

	OriginalAddr = strOriginalAddr                                	#源地址
	DestinationAddr = strDestinationAddr                            #目的地址



	AppDataLength = strAppDataLen									#应用数据单元长度, 第25,26字节低字节传输在前,总长度不超过1024
	AppDataLengthInt = GetHexStr(AppDataLength)						#应用数据单元长度-整型*2(一个字=2字节)

	Command = strCommand											#命令字节
	AppData = strAppData 											#应用数据单元

def VerfiyMsgGB(strMsg):
	pass