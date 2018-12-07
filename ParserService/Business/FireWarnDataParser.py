# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-06-26 19:16:42
# @Last Modified by:   leonliang
# @Last Modified time: 2018-06-30 07:51:35
import time
import re
import json
#from toolkits import *
import FWWebAPI.Business.ParserDataStructure as ParserDataStructure
import FWWebAPI.Business.ParserDictionary as ParserDictionary
import FWWebAPI.Business.Config as GlobalVar
import FWWebAPI.Business.toolkits as toolkits

#通讯包解析-输出应用数据单元内容
class CommDataParser: #数据通讯包解析
    def __init__(self,FwDataBody = "4040002323",CenterInstAdd = "0201"):
        #对于阿里的短信网关，不可以修改
        self.__FwDataBody = FwDataBody #用于解析需要传入的数据内容
        self.__AppData = []
        self.CenterInstBNo = 0 #用于记录监控中心服务实例向客户端发送业务的流水号情况
        self.CenterInstAdd = "" #用于记录监控中心服务实例地址
        
        self.ClientInstBNo = 0 #用于记录客户设备实例向监控中心服务发送业务的流水号情况
        self.ClientrInstAdd = "" #用于记录记录客户设备实例地址
    
    def getNextCenterInstBNo(self,CurrentCenterInstBNo):
        '''
        用于获得记录监控中心服务实例定义的操作流水号
        '''
        self.CenterInstBNo = (CenterInstBNo+1)/(256*256)
        return  self.CenterInstBNo

    def getNextCenterInstBNo(self,CurrentCenterInstBNo,isRetry=False):
        return self.ClientInstBNo

    def AddAppData(self, psAppdata=""):
        #当一条指令里面命令内容多于条时返回集合
        self.__AppData.extend(psAppdata)
        return plAppdata
        
    def set_checksum(self,strOrion,subStrLen=2,intStartPostion=2,intEndPostion=-3) :
        '''
        最后版本20170708---用于和西科大数据交换验证
        返回根据有效数据传输内容(非头标志位\非校验值位\非结尾标志位数据)进行计算的CheckSum校验值
        1,将十六进制的数字串转化为10进制的数字
        2,sort=1为原有的hex子串是逆向排位,低字节传输在前,高字节排序在后;sort=0为原有的hex子串为正向排位,高字节排序在前,低字节排序在后
        '''
        tempStr = strOrion[intStartPostion*subStrLen:intEndPostion*subStrLen]
        checksum = 0 

        tempStrLength = len(tempStr)
        tempStrModLength = tempStrLength%subStrLen
        if tempStrModLength>0 :
            tempStr = tempStr.zfill(tempStrModLength+tempStrLength)
        else :
            tempStr = tempStr

        rpattern = re.compile('.{'+str(subStrLen)+'}')
        b=re.findall(rpattern,tempStr) 
        for i in range(len(b)):
            checksum = checksum+int(b[i],16)
        #checksum &= 0xFF # 强制截断
        #checksum = checksum%16
        checksum = checksum%256
        #checksum
        return toolkits.IntToHexStr(checksum)
        
    

    def get_chechsumresult(self,strOrion,strChecksumBit,intStartPostion=2,intEndPostion=-3,subStrLen=2) :
        '''
        最后版本20170708---用于和西科大数据交换验证
        根据具有效数据传输内容(非头标志位\非校验值位\非结尾标志位数据)返回CheckSum校验值，用于比较传入数据的校验位是否一致,如果一致则返回结果True
        1,将十六进制的数字串转化为10进制的数字
        2,sort=1为原有的hex子串是逆向排位,低字节传输在前,高字节排序在后;sort=0为原有的hex子串为正向排位,高字节排序在前,低字节排序在后
        '''
        tempStr = strOrion[intStartPostion*subStrLen:intEndPostion*subStrLen]
        intChecksumBit = int(strChecksumBit,16)
        checksum = 0 
        lbReturnVal = False
        tempStrLength = len(tempStr)
        tempStrModLength = tempStrLength%subStrLen
        if tempStrModLength>0 :
            tempStr = tempStr.zfill(tempStrModLength+tempStrLength)
        else :
            tempStr = tempStr
        rpattern = re.compile('.{'+str(subStrLen)+'}')
        b=re.findall(rpattern,tempStr) 
        for i in range(len(b)):
            checksum = checksum+int(b[i],16)
        #checksum = checksum - intChecksumBit
        #checksum &= 0xFF # 强制截断
        checksum = checksum%256

        if intChecksumBit == checksum :
            lbReturnVal = True
        return lbReturnVal

    def SetRegarChecksumValue(self,strOrion):
        '''
        获得常规意义上的校验值,即校验值和每位字节数字相加之和能够被256整除(舍弃二进制高八位后,剩余第八位第二进制字节的值内容 对应 的校验值,一般为被传输值每位值之和+校验值%16或者%256余0)
        1,将十六进制的数字串转化为10进制的数字
        '''
        tempStr = ""
        returnStr = ""
        subStrLen = 2
        tempStrLength = len(strOrion)
        tempStrModLength = tempStrLength%subStrLen
        if tempStrModLength>0 :
            tempStr = strOrion.zfill(tempStrModLength+tempStrLength)
        else :
            tempStr = strOrion

        rpattern = re.compile('.{'+str(subStrLen)+'}')
        b=re.findall(rpattern,tempStr) 
        result = 0 
        for i in range(len(b)):
            result=result+int(b[i],16)
        result = 256-result % 256
        return toolkits.IntToHexStr(result)

    def GetRegarChecksumResult(self,strOrion,strChecksumBit):
        '''
        获得常规意义上的校验值,即校验值和每位字节数字相加之和能够被256整除(舍弃二进制高八位后,剩余第八位第二进制字节的值内容 对应 的校验值,一般为被传输值每位值之和+校验值%16或者%256余0),如果校验值和传输数据值可以匹配则返回True
        1,将十六进制的数字串转化为10进制的数字
        '''
        tempStr = ""
        returnStr = ""
        subStrLen = 2
        tempStrLength = len(strOrion)
        intChecksumBit = int(strChecksumBit,16)
        tempStrModLength = tempStrLength%subStrLen
        if tempStrModLength>0 :
            tempStr = strOrion.zfill(tempStrModLength+tempStrLength)
        else :
            tempStr = strOrion

        rpattern = re.compile('.{'+str(subStrLen)+'}')
        b=re.findall(rpattern,tempStr) 
        result = 0 
        for i in range(len(b)):
            result=result+int(b[i],16)
        result = (intChecksumBit+result) % 256
        if result==0 :
            lbReturnVal = True
        return lbReturnVal

    def ParserTimeStr(self,strOriTime,strSplit="-",sort=1,subStrLen=2): #将解析出来的时间串,转译成可读的时间格式
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
            if sort ==0 :
                n = i
                if i == 0 :
                    returnStr = returnStr +  str(int(b[n],16)).zfill(subStrLen)
                elif i>0 and i<3 :
                    returnStr =  str(int(b[n],16)).zfill(subStrLen) + ":" +returnStr
                elif i==3 :
                    returnStr = returnStr + " " + str(int(b[n],16)).zfill(subStrLen)
                elif i==4 :
                    returnStr = returnStr + strSplit + str(int(b[n],16)).zfill(subStrLen)
                elif i==5 :
                    returnStr = returnStr + strSplit + "20"+str(int(b[n],16)).zfill(subStrLen)
            else :
                n = len(b)-i-1


                if i == 0 :
                    returnStr = returnStr + "20" + str(int(b[n],16)).zfill(subStrLen)
                elif i>0 and i<3 :
                    returnStr = returnStr + strSplit + str(int(b[n],16)).zfill(subStrLen)
                elif i==3 :
                    returnStr = returnStr + " " + str(int(b[n],16)).zfill(subStrLen)
                elif i>3 :
                    returnStr = returnStr + ":" + str(int(b[n],16)).zfill(subStrLen)
        return returnStr

    def GetCurrentTimeStr(self,sort=1):
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
        returnStr = ""
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

    def getCommunicationAddr(self,strCommand,strCenterAddr,strDeviceAddr):   #strCommand:命令类型 ;strCenterAddr:监控中心地址;strDeviceAddr:设备地址
        upperActions = ["02","04"]                                      #上行方向,从用户信息传输装置到监控中心的数据传输方向
        downActions =  ["01","03","04","05"]                                #下行方向,从监控中心到用户信息传输装饰的数据传输方向
        if strCommand in downActions:
            strOriginalAddr = strCenterAddr
            strDestinationAddr = strDeviceAddr
        elif strCommand in upperActions:
            strOriginalAddr = strDeviceAddr
            strDestinationAddr = strCenterAddr
        
        OriginalAddr = strOriginalAddr                                  #源地址
        DestinationAddr = strDestinationAddr                            #目的地址
        returnArr=[strOriginalAddr,strDestinationAddr] #源地址
        
        return returnArr


    #对于定义中有"command:" 指令方式的定义,直接执行获得结果内容.
    def getTextDefExcutedResult(self,strOrionStr,strCommandFlag = "command:" ): 
        '''
        对于定义中有"command:" 指令方式的定义,直接执行获得结果内容.
        '''
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

    def getPackageValueByDef(self,strOrionStr,strDefine,TimeConvertTag = ["SendDate"],isChangeToHex=False,strSplit = "|" ,StepLen=2):
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
            if toolkits.IsNumber(b[i]) :
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
            print(u"根据定义,提取元素值发生异常,请检查溢出问题！")
            tempStr = strDefine
        
        if len(tempStr)>0:
            retrunStr = tempStr
        #print(retrunStr,startPosition,endPosition) 
        return retrunStr

    def ParserGBMsgByDictDef(self,strOrionStr,DictDefine={  #默认校验用Dict
                                                        "BeginStr" : "0|2",  #启动符'@@' 2字节,数据包的第一、二字节,为固定值64H,64H(十进制)--40,40(十六进制)
                                                        "AppDataLengthlowbit" : "24|25",        #应用数据单元长度低字节  1字节
                                                        "AppDataLengthHighbit" : "25|26",       #应用数据单元长度高字节 1字节
                                                        "AppDataLength" : "24|26", #command:int(AppDataLengthHighbit+AppDataLengthlowbit,16)",       #应用数据单元长度高字节 1字节
                                                        "AppData" : "27|-4",      #应用数据 共AppDataLength长度个字节
                                                        "Command" : "26|27",                    #命令字节 1字节
                                                        "Checksum" : "-3|-2" ,                  #校验和 1位 使用各位和校验和求反方式, 倒数第三位
                                                        "EndStr" : "-2|"                        #结束符'##' 2字节,数据包的倒数第一、二字节,为固定值35H,35H(十进制)--23,23(十六进制)
                                                    },ReverseKeyDifeTags=["AppDataLength","BNoOrigion"],TimeConvertTag = ["SendDate"],isChangeToInt=False):
        ParserGBMsgBody = {}
        GBMsgStr = strOrionStr

        Dict_string=json.dumps(DictDefine)

        defDict= json.loads(Dict_string)
        for Key in defDict:
            #print(Key+" : "+defDict[Key])
            if Key in ReverseKeyDifeTags :
                ParserGBMsgBody[Key] =  toolkits.ResortStr(self.getPackageValueByDef(GBMsgStr,defDict[Key]))
            else :
                ParserGBMsgBody[Key] =  self.getPackageValueByDef(GBMsgStr,defDict[Key])
            
            if Key in TimeConvertTag :
                ParserGBMsgBody[Key] = self.ParserTimeStr(ParserGBMsgBody[Key])
            elif isChangeToInt :
                if not Key in ["AppData"] :
                    ParserGBMsgBody[Key] = toolkits.HexToIntStr(ParserGBMsgBody[Key],0)
                
            print Key+":"+ParserGBMsgBody[Key]
            
        return ParserGBMsgBody

    def VerifyData(self,strOrionStr,DictDefine={  #默认校验用Dict
                                                        "BeginStr" : "0|2",  #启动符'@@' 2字节,数据包的第一、二字节,为固定值64H,64H(十进制)--40,40(十六进制)
                                                        "Checksum" : "-3|-2" ,                  #校验和 1位 使用各位和校验和求反方式, 倒数第三位
                                                        "AppDataLength" : "24|26",  		#应用数据单元长度2字节, 低字节在前,高字节在后,需要翻转字节后在转换
                                                        "AppData" : "27|-3",      #应用数据 共AppDataLength长度个字节
                                                        "EndStr" : "-2|"                        #结束符'##' 2字节,数据包的倒数第一、二字节,为固定值35H,35H(十进制)--23,23(十六进制)
                                                    },VerifiedKeyDifeTags=["BeginStr","Checksum","EndStr"]):
        lbReturnflag = False
        ParserGBMsgBody ={}
        GBMsgStr = strOrionStr

        Dict_string=json.dumps(DictDefine)

        defDict= json.loads(Dict_string)
        for Key in defDict:
            #print(Key+" : "+defDict[Key])
            ParserGBMsgBody[Key] =  self.getPackageValueByDef(GBMsgStr,defDict[Key])
            print Key+":"+ParserGBMsgBody[Key]

        #ParserGBMsgBody["AppDataLength"] =  toolkits.ResortStr(ParserGBMsgBody["AppDataLength"]) 
        print "get AppDataLength from Appdata as :"+str(len(ParserGBMsgBody["AppData"])/2)
        print "get AppDataLength from revsers-AppDataLength as :"+toolkits.HexToIntStr(ParserGBMsgBody["AppDataLength"],1)
        if (len(ParserGBMsgBody["AppData"])/2) == int(toolkits.HexToIntStr(ParserGBMsgBody["AppDataLength"],1) ):
            if FireWaringDP.get_chechsumresult(strOrionStr,ParserGBMsgBody["Checksum"]) :
                if ParserGBMsgBody["BeginStr"] == "4040" and ParserGBMsgBody["EndStr"] == "2323":
                    lbReturnflag = True
            
        return lbReturnflag

#测试验证
'''
DataParserInst = DataParser()
currentTimestr =  DataParserInst.GetCurrentTimeStr()
print "1:"+ currentTimestr
currentTimestr2 = DataParserInst.GetCurrentTimeStr(1)
print "2:"+currentTimestr2
currentTimestr3 = ResortStr(currentTimestr2)
print "3:"+ currentTimestr3
'''

if __name__ == '__main__':
    #teststr = "40406E01010122090D1A03120100000000000000000000013000020201010B280101012308000000000000000000000000000000000000000000000000000000000000000007010D1A0312ED2323"
    teststr ="40402E000100041F0C0706120101010101010202020202020C00020101010B020024220C0706121E2323"
    #teststr ="404070010101040B0D1A03120100000000000000000000010C00020401010B1000080D0D1A0312CE2323"
    lsDictAPPDataStruct = ParserDataStructure.DictAPPDataStruct
    
    FireWaringDP = CommDataParser(teststr)
    print teststr
    if FireWaringDP.VerifyData(teststr) :
        print "data is vaild"
        FireWaringDPResultDict = FireWaringDP.ParserGBMsgByDictDef(teststr,lsDictAPPDataStruct,ParserDataStructure.ReverseKeyDifeTags,ParserDataStructure.TimeConvertTag)
    else :
        print "data is invaild"

    
    #FireWaringDP.ClientInstBNo = FireWaringDPResultDict["BNoOrigion"]
    #FireWaringDP.ClientrInstAdd = FireWaringDPResultDict["OriginalAddr"]
    #FireWaringDP.CenterInstAdd = FireWaringDPResultDict["DestinationAddr"]

    '''
    print len(FireWaringDPResultDict["AppData"])/2
    print "AppDataLength:"+str(toolkits.HexToIntStr(FireWaringDPResultDict["AppDataLength"],0))
    print "BNoOrigion:"+ str(FireWaringDPResultDict["BNoOrigion"])
    print "BNoOrigionInt:"+ str(toolkits.HexToIntStr(FireWaringDPResultDict["BNoOrigion"],0))
    print "BNoOrigionRevInt:"+ str(toolkits.HexToIntStr(FireWaringDPResultDict["BNoOrigion"],1))
    print "Checksum:"+ FireWaringDPResultDict["Checksum"]
    #print FireWaringDP.GetChecksumValue(teststr)
    print "FireWaringDP.SetRegarChecksumValue(teststr[2*2:-3*2])"+ FireWaringDP.SetRegarChecksumValue(teststr[2*2:-3*2])
    print "FireWaringDP.set_checksum(teststr)" + FireWaringDP.set_checksum(teststr)
    if FireWaringDP.get_chechsumresult(teststr,FireWaringDPResultDict["Checksum"]) :
        print "Checksum is "+FireWaringDPResultDict["Checksum"]
    else :
        print "Checksum is not "+FireWaringDPResultDict["Checksum"]

    if FireWaringDP.GetRegarChecksumResult(teststr[2*2:-3*2],FireWaringDP.SetRegarChecksumValue(teststr[2*2:-3*2])) :
        print "GetRegarChecksumResult is "+FireWaringDP.SetRegarChecksumValue(teststr[2*2:-3*2])
    else :
        print "GetRegarChecksumResult is not "+FireWaringDP.SetRegarChecksumValue(teststr[2*2:-3*2])
    '''
    #print FireWaringDP.GetChecksumValue(FireWaringDPResultDict["AppData"])
    #print FireWaringDP.GetChecksumValue(teststr[2*2:-3*2])
    #print FireWaringDP.get_chechsumdata(teststr)
    #print FireWaringDP.str_checksum(teststr,FireWaringDPResultDict["Checksum"])
    #print FireWaringDP.str_checksum(teststr,"0")
    #print FireWaringDP.str_checksum(teststr,FireWaringDP.get_chechsumdata(teststr))
    
    #lsDictAPPDataStruct = ParserDataStructure.DictAPPDataStruct
    #FireWaringDPResultDict = FireWaringDP.ParserGBMsgByDictDef(teststr,lsDictAPPDataStruct,ParserDataStructure.ReverseKeyDifeTags,ParserDataStructure.TimeConvertTag,True)
   

