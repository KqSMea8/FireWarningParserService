# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-03-26 15:16:42
# @Last Modified by:   leonliang
# @Last Modified time: 2018-03-28 11:23:10
import time
import re
import json
import toolkits

'''通用函数定义区域 Region Begin'''
def str_checksum(strOrion,strChecksumBit,subStrLen=2,intStartPostion=2,intEndPostion=-3,StepLen=2) :
	tempStr = strOrion[intStartPostion*StepLen:intEndPostion*StepLen]
	intChecksumBit = int(strChecksumBit,16)
	checksum = 0 

	tempStrLength = len(tempStr)
	tempStrModLength = tempStrLength%subStrLen
	if tempStrModLength>0 :
		tempStr = strOrion.zfill(tempStrModLength+tempStrLength)
	else :
		tempStr = strOrion

	rpattern = re.compile('.{'+str(subStrLen)+'}')
	b=re.findall(rpattern,tempStr) 
	for i in range(len(b)):
		if i > 0  :
			intChecksumAll = intChecksumAll+int(b[0],16)
	checksum = checksum + int(ChecksumBit,16)
	#checksum &= 0xFF # 强制截断

	checksum = checksum%16
	return checksum


def get_chechsumdata(strOrion,intStartPostion=2,intEndPostion=-3,subStrLen=2) :
	tempStr = strOrion[intStartPostion*StepLen:intEndPostion*StepLen]
	intChecksumBit = int(strChecksumBit,16)
	checksum = 0 

	tempStrLength = len(tempStr)
	tempStrModLength = tempStrLength%subStrLen
	if tempStrModLength>0 :
		tempStr = strOrion.zfill(tempStrModLength+tempStrLength)
	else :
		tempStr = strOrion

	rpattern = re.compile('.{'+str(subStrLen)+'}')
	b=re.findall(rpattern,tempStr) 
	for i in range(len(b)):
		if i > 0  :
			checksum = hex(checksum)+int(b[0],16)
	checksum = checksum + intChecksumBit
	#checksum &= 0xFF # 强制截断

	checksum = 16-checksum%16
	return IntToHex(Strchecksum)



def ParserTimeStr(strOriTime,strSplit="-",sort=1,subStrLen=2): #将解析出来的时间串,转译成可读的时间格式
	'''
	字符串按照,subStrLen长度进行拆分
	分隔后的字符串按照进行排序,sort=1 为逆序,所有分隔字符组按照逆向进行排列,sort=0为正向排位
	同时用strSplit进行字符整体串联
	'''
	tempStr = ""
	returnStr = ""
	tempStrLength = len(strOriTime)
	tempStrModLength = tempStrLength%subStrLen
	if tempStrModLength>0 :
		tempStr = strOriTime.zfill(tempStrModLength+tempStrLength)
	else :
		tempStr = strOriTime
	rpattern = re.compile('.{'+str(subStrLen)+'}')
	b=re.findall(rpattern,tempStr) 


	for i in range(len(b)):
		if sort == 0:
			n = i
		else :
			n = len(b)-i-1

		if i == 0 :
			returnStr = returnStr + "20" + str(int(b[n],16))
		elif i>0 and i<3 :
			returnStr = returnStr + strSplit + str(int(b[n],16))
		elif i==3 :
			returnStr = returnStr + " " + str(int(b[n],16))
		elif i>3 :
			returnStr = returnStr + ":" + str(int(b[n],16))


	return returnStr

def GetCurrentTimeStr(sort=1):
    '''#时间标签: 返回当前子串
    秒 : 1位,0-59,本次案例为00[十六进制] / 00[十进制]
    分 : 1位,0-59,本次案例为1E[十六进制] / 30[十进制]
    时 : 1位,0-23,本次案例为12[十六进制] / 18[十进制]
    日 : 1位,1-31,本次案例为05[十六进制] / 05[十进制]
    月 : 1位,1-12,本次案例为03[十六进制] / 03[十进制]
    年 : 1位,00-99,本次案例为12[十六进制] / 12[十进制](默认为20XX年)
    sort参数:返回字符串按照进行排序,sort=1(默认值) 为逆序,所有分隔字符组按照逆向进行排列,sort=0为正向排位
    '''

    #SEND_DATE = "001E12050312"                                   `

    localtime = time.localtime()
    localyear =IntToHexStr(int(str(localtime[0])[-2:]))
    localmonth = IntToHexStr(localtime[1])
    localdate = IntToHexStr(localtime[2])
    localhour = IntToHexStr(localtime[3])
    localmin = IntToHexStr(localtime[4])
    localsec = IntToHexStr(localtime[5])

    if sort==1:
    	returnStr = localsec+localmin+localhour+localdate+localmonth+localyear
    elif sort == 0:
    	returnStr = localyear+localmonth+localdate+localhour+localmin+localsec
    return (returnStr)

def getCommunicationAddr(strCommand,strCenterAddr,strDeviceAddr):   #strCommand:命令类型 ;strCenterAddr:监控中心地址;strDeviceAddr:设备地址
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
	returnArr=[strOriginalAddr,strDestinationAddr] #源地址
	
	return returnArr


#对于定义中有"command:" 指令方式的定义,直接执行获得结果内容.
def getTextDefExcutedResult(strOrionStr,strCommandFlag = "command:" ): 
	tempExecStr = ""
	rpatter = re.compile(r'command:')
	b=re.sub(rpatter,tempExecStr,"") 
	print(b)
	try:
		#empExecStr = str(eval(b[0]))
		print(b[0])
	except Exception, e:
		raise e.message
		tempExecStr = strOrionStr
	
	return tempExecStr

def getPackageValueByDef(strOrionStr,strDefine,strSplit = "|" ,StepLen=2):
	tempStr = ""
	retrunStr = ""
	tempStrLength = len(strOrionStr)
	startPosition = ""
	startPosition = ""

	#rpattern = re.compile("[,|;*]")
	rpattern = re.compile("["+strSplit+"]")
	b=re.split(rpattern,strDefine) 
	


	#print str(tempStrLength)
	#print(b)
	if len(b)>2:
		tempStr="请检查变量解析定义设置是否有误,例如是否有过多的设置参数或者设置值是否可以转化为整型"
	
	for i in range(len(b)):
		if b[i].isdigit() :
			try:     
				f =int(b[i]) 
			except ValueError:     
				print("输入的不是数字！")
				tempStr=strDefine

	try:

		if len(b[0])>0 :
			startPosition = int(b[0])*StepLen
		if len(b[1])>0 :
			endPosition = int(b[1])*StepLen


		if len(b[0]) == 0 :
			retrunStr = strOrionStr[:endPosition]
			tempStr = ""
		elif len(b[1]) == 0 :
			retrunStr = strOrionStr[startPosition:]
			tempStr = ""
		else :
		    retrunStr = strOrionStr[startPosition:endPosition]

	except ValueError:     
		print("根据定义,提取元素值发生异常,请检查溢出问题！")
		tempStr = strDefine

	if len(tempStr)>0:
		retrunStr = tempStr
	#print(retrunStr,startPosition,endPosition)	
	return retrunStr

def ParserGBMsgByJsonDef(strOrionStr,jsonDefine={	#默认校验用json
													"BeginStr" : "0|2",  #启动符'@@' 2字节,数据包的第一、二字节,为固定值64H,64H(十进制)--40,40(十六进制)
												    "AppDataLengthlowbit" : "24|25", 		#应用数据单元长度低字节  1字节
												    "AppDataLengthHighbit" : "25|26",  		#应用数据单元长度高字节 1字节
												    "AppDataLength" : "command:int(AppDataLengthHighbit+AppDataLengthlowbit,16)",  		#应用数据单元长度高字节 1字节
												    "AppData" : "27|command:27+AppDataLength",      #应用数据 共AppDataLength长度个字节
												    "Command" : "26|27",                    #命令字节 1字节
												    "Checksum" : "-3|-2" ,                 	#校验和 1位 使用各位和校验和求反方式, 倒数第三位
												    "EndStr" : "-2|"						#结束符'##' 2字节,数据包的倒数第一、二字节,为固定值35H,35H(十进制)--23,23(十六进制)
												}):
	ParserGBMsgBody = {}
	GBMsgStr = strOrionStr

	json_string=json.dumps(jsonDefine)

	defDict= json.loads(json_string)
	for Key in defDict:
		#print(Key+" : "+defDict[Key])
		ParserGBMsgBody[Key] =  getPackageValueByDef(GBMsgStr,defDict[Key])

	return ParserGBMsgBody



#temparr = getCommunicationAddr("02","OriginalAddr","strDeviceAddr")
#print(temparr)
'''通用函数定义区域 Region End'''





'''传输包数据定义区域 Region Begin'''

#启动符'@@' 2字节,数据包的第一、二字节,为固定值64,64(十进制)--40,40(十六进制)
PackageBeginStr = "4040"
#结束符'##' 2字节,数据包的最后两个字节,为固定值35,35(十进制)--23,23(十六进制)
PackageEndStr = "2323"

#上行方向,从用户信息传输装置到监控中心的数据传输方向
upperActions = ["02","04"]

#下行方向,从监控中心到用户信息传输装饰的数据传输方向										
downActions =  ["01","03","04","05"]	

'''通讯方式: 
控制命令为"01"(十进制),01(十六进制)---(监控中心->用户信息传输装置:监控中心--控制命令-->用户信息传输装置--确认-->监控中心);
信息上传为"05"(十进制),05(十六进制)---(用户信息传输装置->监控中心:用户信息传输装置--信息上传-->监控中心--接收确认-->用户信息传输装置);
信息查询为"10"(十进制),0A(十六进制)---(监控中心->用户信息传输装置:监控中心--信息查询请求-->用户信息传输装置--应答-->监控中心);
'''
CommandsTypes = ["01","05","10"]							

#VerificationFlag确认校验是否通过,如果所有校验规则通过后无问题,则VerificationFlag为true,VerificationCode数组中存在唯一字符串"200"
VerificationCode = {
	"200" : "发送包数据,已经通过校验位验证,验证正确",
	"500" : "发送包数据,未能通过校验位,可能是通讯中发生了意味[应对:1,重试;2,报错-提醒线路巡检]",

	"301" : "启动符,信息1,2两位不是固定值64(十进制),40(十六进制)",
	"305" : "结束符,信息最末两位不是固定值35(十进制),23(十六进制)",
	
	"501" : "发送标记时间与当前系统事件相距10秒以上,请确认应用时钟同步状态或者确认数据是否重发(国家标准超时时间不宜大于10秒)",
	"601" : "平台该标识信息已经接受3次以上,请确认应用时钟同步状态或者确认相关应用响应确认服务是否正常(国家标准超时重发不宜大于3次)"
}






#传输包结构定义,数据定义方式Json,具体定义为"起始位置|结束位置"2字节,数据包的第一、二字节,为固定值64,64(十进制)--40,40(十六进制)
APPDataStruct = {
	"BeginStr" : "0|2",						#启动符'@@' 2字节,数据包的第一、二字节,为固定值64H,64H(十进制)--40,40(十六进制)

	"BNoLowbit" : "2|3",					#业务流水号低字节 1字节,低字节
	"BNoHighbit" : "3|4",					#业务流水号高字节 1字节,高字节
	"BNoOrigion" : "2|4",					#业务流水号原始值 2字节,低字节先传高字节后传 
	"BNoOrigion" : "command:BNoHighbit+BNoLowbit",	#业务流水号 2字节,BNo = BNoHighbit+BNoLowbit

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
    "AppDataLength" : "command:int(AppDataLengthHighbit+AppDataLengthlowbit,16)",  		#应用数据单元长度高字节 1字节
    "AppData" : "27|command:27+AppDataLength",      #应用数据 共AppDataLength长度个字节
    "Command" : "26|27",                    #命令字节 1字节

    "Checksum" : "-3|-2" ,                 	#校验和 1位 使用各位和校验和求反方式, 倒数第三位
    "EndStr" : "-2|"						#结束符'##' 2字节,数据包的倒数第一、二字节,为固定值35H,35H(十进制)--23,23(十六进制)
}



'''传输包数据定义区域 Region End'''


'''应用数据定义区域 Region Begin'''
#应用数据结构定义,数据定义方式Json,具体定义为
CommandTypeStruct ={
	#命令字节
    "00":"预留" ,
    "01":"控制命令" ,
    "02":"发送数据" ,
    "03":"确认" ,
    "04":"请求" ,
    "05":"应答" ,
    "06":"否认" 
    #07-127---预留
	#128-255---用户自行定义
}



#数据类型标志含义,数据定义方式Json,具体定义见国标26875.3-2011的"表3"
JsonAppTypeFlag = {
	"1" :  "1, #上传建筑消防设施系统状态",
	"2" :  "2, #上传建筑消防设施部件运行状态",  
	"3" :  "3, #上传建筑消防设施部件模拟量值",
	"4" :  "4, #上传建筑消防设施操作信息",
	"5" :  "5, #上传建筑消防设施软件版本",
	"6" :  "6, #上传建筑消防设施系统配置情况",
	"7" :  "7, #上传建筑消防设施部件配置情况",
	"8" :  "8, #上传建筑消防设施系统时间",
	"21" :  "21, #上传用户信息传输装置运行状态",
	"24" :  "24, #上传用户信息传输装置操作信息",
	"25" :  "25, #上传用户信息传输装置软件版本",
	"26" :  "26, #上传用户信息传输装置配置情况",
	"28" :  "28, #上传用户信息传输装置系统时间",
	"61" :  "61, #读建筑消防设施系统状态",
	"62" :  "62, #读建筑消防设施部件运行状态",
	"63" :  "63, #读建筑消防设施部件模拟量值",
	"64" :  "64, #读建筑消防设施操作信息",
	"65" :  "65, #读建筑消防设施软件版本",
	"66" :  "66, #读建筑消防设施系统配置情况",
	"67" :  "67, #读建筑消防设施部件配置情况",
	"68" :  "68, #读建筑消防设施系统时间",
	"81" :  "82, #读用户信息传输装备运行状态",
	"84" :  "84, #读用户信息传输装置操作信息记录",
	"85" :  "85, #读用户信息传输装置软件版本",
	"86" :  "86, #读用户信息传输装置配置情况",
	"88" :  "88, #读用户信息传输装置系统时间",
	"89" :  "89, #初始化用户信息传输装置",
	"90" :  "90, #同步用户信息传输装置时钟",
	"91" :  "92, #查岗命令"
}



#系统类型定义表,数据定义方式Json,具体定义见国标26875.3-2011的表4
JsonAppSysType ={
	"0" : "通用",
	"1" : "火灾报警系统",
	#"2-9" : "预留",
	"10" : "消防联动控制器",
	"11" : "消火栓系统",
	"12" : "自动喷水灭火系统",
	"13" : "气体灭火系统",
	"14" : "水喷雾灭火系统(泵启动方式)",
	"15" : "水喷雾灭火系统(压力容器启动方式)",
	"16" : "泡沫灭火系统",
	"17" : "干粉灭火系统",
	"18" : "防烟排烟系统",
	"19" : "防火门急卷帘系统",
	"20" : "消防电梯",
	"21" : "消防应急广播",
	"22" : "消防应用照明和疏散指示系统",
	"23" : "消防电源",
	"24" : "消防电话" #,
	#"25-127" : "预留",
	#"128-255" : "用户自定义"
}

#建筑消防设施部件类型定义表,数据定义方式Json,具体定义见国标26875.3-2011的表5
JsonAppPartType ={
	"0" : "通用",
	"1" : "火灾报警控制器",
	#"2-9" : "预留",
	"10" : "可燃气体探测器",
	"11" : "点型可燃气体探测器",
	"12" : "独立式可燃气体探测器",
	"13" : "线型可燃气探测器",
	#"14" : "预留",
	#"15" : "预留",
	"16" : "电器火灾监控报警器",
	"17" : "剩余电流式电气火灾监控探测器",
	"18" : "测温式电气火灾监控探测器",
	#"19" : "预留",
	#"20" : "预留",
	"21" : "探测回路",
	"22" : "火灾显示盘",
	"23" : "手动火灾报警按钮",
	"24" : "消防栓按钮", 
	"25" : "火灾探测器",
	#"26-29" : "预留",
	"30" : "感温火灾探测器",
	"31" : "点型感温火灾探测器",
	"32" : "点型感温火灾探测器(S型)",
	"33" : "点型感温火灾探测器(R型)",
	"34" : "线型感温火灾探测器",
	"35" : "线型感温火灾探测器(S型)",
	"36" : "线型感温火灾探测器(R型)",
	"37" : "光纤感温火灾探测器",
	#"38" : "预留",
	#"39" : "预留",
	"40" : "感烟火灾探测器",
	"41" : "点型离子感烟火灾探测器",
	"42" : "点型光电感烟火灾探测器",
	"43" : "线型光束感烟火灾探测器",
	"44" : "吸气式感烟火灾探测器", 	
	#"45-49" : "预留",
	"50" : "复合式火灾探测器",
	"51" : "复合式感烟感温火灾探测器",
	"52" : "复合式感光感温火灾探浏器",
	"53" : "复合式感光感烟火灾探测器",
	#"54-59" : "预留",
	#"60" : "预留",
	"61" : "紫外火焰探测器",
	"62" : "红外火焰探测器",
	#"63-68" : "预留",
	"69" : "感光火灾探测器",
	#"70-73" : "预留",
	"74" : "气体探测器",
	#"75-77" : "预留",
	"78" : "图像摄像方式火灾探测器",
	"79" : "感声火灾探测器",
	#"80" : "预留",
	"81" : "气体灭火控制器",
	"82" : "消防电气控制装置",
	"83" : "消防控制室图形显示装置",
	"84" : "模块",
	"85" : "输入模块",
	"86" : "输出模块",
	"87" : "输入／输出模块",
	"88" : "中继模块",
	#"89-90" : "预留",
	"91" : "消防水泵",
	"92" : "消防水箱",
	#"93" : "预留",
	#"94" : "预留",
	"95" : "喷淋泵",
	"96" : "水流指示器",
	"97" : "信号阀",
	"98" : "报警阀",
	"99" : "压力开关",
	#"100" : "预留",
	"101" : "阀驱动装置",
	"102" : "防火门",
	"103" : "防火阀",
	"104" : "通风空调",
	"105" : "泡沫液泵",
	"106" : "管网电磁阀",
	#"107-110" : "预留",
	"111" : "防烟排烟风机",
	#"112" : "预留",
	"113" : "排烟防火阀",
	"114" : "常闭送风口",
	"115" : "排烟口",
	"116" : "电控挡烟垂壁",
	"117" : "防火卷帘控制器",
	"118" : "防火门监控器",
	#"119-120" : "预留",
	"121" : "警报装置" #,
	#"121-127" : "预留",
	#"128-255" : "用户自定义"

}

#应用数据单元结构定义,数据定义方式Json,具体定义为"起始位置|字节数"2字节
APPDataStruct = {
    #9.1标识符
    "AppTypeFlag" : "0|1",   #数据类型标志,1个字节,具体定义见国标26875.3-2011的表3即本定义 JsonAppTypeFlag 对象
    "InfoObjectsNum" : "1|2", #信息对象数目,1个字节

    #9.2信息对象
    "AppObjBodyLength" : [
	    4, #建筑消防设施系统状态信息, 4字节
	    2,
	    2

    ], #对应JsonAppTypeFlagIndex中各类传输类型的信息体字节位数
    #9.2.1信息体
    #9.2.1.1  建筑消防设施系统状态 信息
    "AppObjBodyDefine" : [
	    [
	    	{
		    	"AppSysType" : "2|3", #9.2.1.1.1 建筑消防设施系统类型标志, 1字节,定义如国标26875.3-2011的表4(即,JsonAppSysType中定义的相关内容)
		    	"AppSysAddr" : "3|4", #9.2.1.1.2 系统地址, 1字节,由消防设施设定
		    	"AppSysStatus" : "4|6", #9.2.1.1.3 系统状态,2字节,定义如国标26875.3-2011的图6,低字节传输在前
		    	"AppSysStatusLowBit" : "4|5", #9.2.1.1.3 系统状态,2字节,定义如国标26875.3-2011的图6,低字节
		    	"AppSysStatusHighBit" : "5|6" #9.2.1.1.3 系统状态,2字节,定义如国标26875.3-2011的图6,高字节

		    	'''
		    	AppSysStatusBin = HexToByteStr(AppSysStatusHighBit)+HexToByteStr(AppSysStatusLowBit)
		    	bit15 = AppSysStatusBin[0:1]    #0预留
		    	bit14 = AppSysStatusBin[1:2]    #0预留
	            bit13 = AppSysStatusBin[2:3]    #1复位          0正常
	            bit12 = AppSysStatusBin[3:4]    #1配置改变      0无配置改变
	            bit11 = AppSysStatusBin[4:5]    #1手动状态      0自动状态
	            bit10 = AppSysStatusBin[5:6]    #1总线故障      0总线正常
	            bit9 = AppSysStatusBin[6:7]     #1备电故障      0备电正常
	            bit8 = AppSysStatusBin[7:8]     #1主电故障      0主电正常
	            bit7 = AppSysStatusBin[8:9]     #1延时状态      0未延时
	            bit6 = AppSysStatusBin[9:10]    #1反馈          0无反馈
	            bit5 = AppSysStatusBin[10:11]   #1启动（开启）   0停止（关闭）
	            bit4 = AppSysStatusBin[11:12]   #1监管    0无监管
	            bit3 = AppSysStatusBin[12:13]   #1屏蔽    0无屏蔽
	            bit2 = AppSysStatusBin[13:14]   #1故障    0无故障
	            bit1 = AppSysStatusBin[14:15]   #1火警    0无火警
	            bit0 = AppSysStatusBin[15:16]   #1正常运行状态    0测试状态
		    	'''
		    }
	    ],#9.2.1.1 建筑消防设施系统状态 消息体定义 ,共4个字节
	    [
	    	{
	    		"AppSysType" : "2|3", 	#9.2.1.2.1 建筑消防设施系统类型标志, 1字节,定义如国标26875.3-2011的表4(即,JsonAppSysType中定义的相关内容)
		    	"AppSysAddr" : "3|4", 	#9.2.1.2.2 系统地址, 1字节,消防设施部件设定,暂时定位 系统标志+部件流水号的方式,从而从首位能够看出类型,问题:如果消防电话为例,类别为24 且可能超过10部,如何表示?
		    	"AppPartType" : "4|5", 	#9.2.1.2.3 建筑消防设施部件类型,1字节,定义见国标26875.3-2011的表5(即,JsonAppPartType中定义的相关内容)

		    	"AppPartAddr" : "5|9",  #9.2.1.2.4 建筑消防设施部件地址（4字节，低位字节在前，部件编号1字节、楼层号1字节、楼号1字节、楼群号1字节）
		    	"AppPartNo" : "5|6",    #9.2.1.2.4.1 部件编号
		    	"AddrRegionNo" : "6|7",  #9.2.1.2.4.2 小区编号/楼群号
            	"AddrBuilderNo" : "7|8", #9.2.1.2.4.3 楼号
            	"AddrFloorNo" : "8|9",   #9.2.1.2.4.4楼层号
            	"AppPartStatus" : "9|11", #9.2.1.2.3建筑消防设施部件状态数据（2个字节，定义如国标26875.3-2011的图7所示）,低字节的先传。
            	"AppPartStatusLowBit" : "9|10", #9.2.1.2.3建筑消防设施部件状态数据（2个字节，定义如国标26875.3-2011的图7所示）,低字节。
            	"AppPartStatusHighBit" : "10|11" #9.2.1.2.3建筑消防设施部件状态数据（2个字节，定义如国标26875.3-2011的图7所示）,低字节。

            	'''
				AppPartStatus = "0800"
				AppPartStatusBin = HexToByteStr(AppPartStatusLowBit)+HexToByteStr(AppPartStatusHighBit)
				#AppPartStatusBin = HexToByteStr(AppPartStatus[2:4])+HexToByteStr(AppPartStatus[0:2])
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
            	'''

  	    	}
	    ]#9.2.1.2 建筑消防设施部件状态（具体部件状态，共40个字节，定义如国标26875.3-2011的图7所示,其中31字节的部件说明暂时保留，设置为00H…...
    ]
    #9.2.2
    


	
}


'''应用数据定义区域 Region End'''


if IsNumber(12) :
	print("isnum")