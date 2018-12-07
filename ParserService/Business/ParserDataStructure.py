# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-03-26 15:16:42
# @Last Modified by:   leonliang
# @Last Modified time: 2018-03-28 10:37:51
import time
import re
import json
import toolkits


#启动符'@@' 2字节,数据包的第一、二字节,为固定值64,64(十进制)--40,40(十六进制)
PackageBeginStr = "4040"
#结束符'##' 2字节,数据包的最后两个字节,为固定值35,35(十进制)--23,23(十六进制)
PackageEndStr = "2323"

'''通讯方式: 
控制命令为"01"(十进制),01(十六进制)---(监控中心->用户信息传输装置:监控中心--控制命令-->用户信息传输装置--确认-->监控中心);
信息上传为"05"(十进制),05(十六进制)---(用户信息传输装置->监控中心:用户信息传输装置--信息上传-->监控中心--接收确认-->用户信息传输装置);
信息查询为"10"(十进制),0A(十六进制)---(监控中心->用户信息传输装置:监控中心--信息查询请求-->用户信息传输装置--应答-->监控中心);
'''
CommandsTypes = ["01","05","10"]	

#VerificationFlag确认校验是否通过,如果所有校验规则通过后无问题,则VerificationFlag为true,VerificationCode数组中存在唯一字符串"200"



'''传输包数据定义区域 Region Begin'''
#传输包结构定义,数据定义方式Json,具体定义为"起始位置|结束位置"2字节,数据包的第一、二字节,为固定值64,64(十进制)--40,40(十六进制)
DictAPPDataStruct ={
    #"ID" : "7.8",
	"BeginStr" : "0|2",						#启动符'@@' 2字节,数据包的第一、二字节,为固定值64H,64H(十进制)--40,40(十六进制)
    "BNoLowbit" : "2|3",					#业务流水号低字节 1字节,低字节
	"BNoHighbit" : "3|4",					#业务流水号高字节 1字节,高字节
	"BNoOrigion" : "2|4",					#业务流水号原始值 2字节,低字节先传高字节后传 
	#"BNoOrigion" : "2|4",	#业务流水号 2字节,BNo = BNoHighbit+BNoLowbit
    "MasterProtocolVer" : "4|5", 			#协议版本主版本号 1字节
	"UserProtocolVer" : "5|6", 				#协议版本用户版本号 1字节
	"ProtocolVer" : "4|6",					#协议版本 1字节
    "SendDate" : "6|12",  					#时间标签6个字节,低字节先传,即秒,分,时,月,日,年(年为两位,如2018标识为18)
	"SendTimeSec" : "6|7", 					#发送秒 1个字节
	"SendTimeMin" : "7|8", 					#发送分 1个字节
	"SendTimeHour" : "8|9", 				#发送小时 1个字节
	"SendTimedate" : "9|10", 				#发送日 1个字节
	"SendTimeMonth" : "10|11", 				#发送月 1个字节
    "SendTimeYear" : "11|12", 				#发送年 1个字节
    #上行方向,从用户信息传输装置到监控中心的数据传输方向,需要区分 
    #下行方向,从监控中心到用户信息传输装饰的数据传输方向,需要区分
	"OriginalAddr" : "12|18",    			#源地址 6个字节 
	"DestinationAddr" : "18|24",   			#目的地址 6个字节
    "AppDataLengthlowbit" : "24|25", 		#应用数据单元长度低字节  1字节
    "AppDataLengthHighbit" : "25|26",  		#应用数据单元长度高字节 1字节
    "AppDataLength" : "24|26",  		#应用数据单元长度2字节, 低字节在前,高字节在后,需要翻转字节后在转换
    "AppData" : "27|-3",      #应用数据 共AppDataLength长度个字节
    "Command" : "26|27",                    #命令字节 1字节

    "Checksum" : "-3|-2" ,                 	#校验和 1位 使用各位和校验和求反方式, 倒数第三位
    "EndStr" : "-2|"						#结束符'##' 2字节,数据包的倒数第一、二字节,为固定值35H,35H(十进制)--23,23(十六进制)
}

#用于定义低字节优先传送的字段集合
ReverseKeyDifeTags=["AppDataLength","BNoOrigion"]
#用于定义需要转换为时间的字段集合
TimeConvertTag = ["SendDate"]

'''传输包数据定义区域 Region End'''





