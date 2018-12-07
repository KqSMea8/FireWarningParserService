# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-03-27 22:42:42
# @Last Modified by:   leonliang
# @Last Modified time: 2018-06-30 07:53:43
import types
import re
import time
import os
import MySQLdb
import shutil
import uuid
import socket
import smtplib #mail
import zipfile   #zipfiles
import sys #字符串加密
import Config as GlobalVar
#import Image as image
from Crypto.Cipher import AES #字符串加密解密
from binascii import b2a_hex, a2b_hex #字符串加密解密
from email.mime.text import MIMEText #mail
from email.header import Header #mail
from email.mime.multipart import MIMEMultipart #mail

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest #sms
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest #sms

#from FWWebAPI.aliyunsdkcore.client import AcsClient #sms
#from FWWebAPI.aliyunsdkcore.profile import region_provider  #sms
#from FWWebAPI.aliyunsdkcore.http import method_type as MT  #sms
#from FWWebAPI.aliyunsdkcore.http import format_type as FT  #sms


#------------checksum 相关算法 begin--------
def GetChecksumValue(strOrion):
    '''
    最终使用版本20180616
    1,将十六进制的数字串转化为10进制的数字
    2,sort=1为原有的hex子串是逆向排位,低字节传输在前,高字节排序在后;sort=0为原有的hex子串为正向排位,高字节排序在前,低字节排序在后
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
    

    result = result % 16
    return IntToHexStr(result)

#------------checksum 相关算法 end--------

#----------------验证所有表单提交的数据------begin 
 
  
#判断是否为整数 15  
def IsNumber(varObj):  
  
    return type(varObj) is types.IntType  
  
#判断是否为字符串 string  
def IsString(varObj):  
  
    return type(varObj) is types.StringType  
  
#判断是否为浮点数 1.324  
def IsFloat(varObj):  
    
    return type(varObj) is types.FloatType  
  
#判断是否为字典 {'a1':'1','a2':'2'}  
def IsDict(varObj):  
  
    return type(varObj) is types.DictType  
  
#判断是否为tuple [1,2,3]  
def IsTuple(varObj):  
  
    return type(varObj) is types.TupleType  
  
#判断是否为List [1,3,4]  
def IsList(varObj):  
  
    return type(varObj) is types.ListType  
  
#判断是否为布尔值 True  
def IsBoolean(varObj):  
  
    return type(varObj) is types.BooleanType  
  
#判断是否为货币型 1.32  
def IsCurrency(varObj):  
  
    #数字是否为整数或浮点数  
    if IsFloat(varObj) and IsNumber(varObj):  
        #数字不能为负数  
        if varObj >0:  
            return isNumber(currencyObj)  
            return False  
    return True  
  
#判断某个变量是否为空 x  
def IsEmpty(varObj):  
  
    if len(varObj) == 0:  
        return True  
    return False  
  
#判断变量是否为None None  
def IsNone(varObj):  
  
    return type(varObj) is types.NoneType# == "None" or varObj == "none":  
  
#判断是否为日期格式,并且是否符合日历规则 2010-01-31  
def IsDate(varObj):  
  
    if len(varObj) == 10:  
        rule = '(([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)$/'  
        match = re.match( rule , varObj )  
        if match:  
            return True  
        return False  
    return False  
  
#判断是否为邮件地址  
def IsEmail(varObj):  
  
    rule = '[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$'  
    match = re.match( rule , varObj )  
  
    if match:  
        return True  
    return False  
  
#判断是否为中文字符串  
def IsChineseCharString(varObj):  
  
    for x in varObj:  
        if (x >= u"\u4e00" and x<=u"\u9fa5") or (x >= u'\u0041' and x<=u'\u005a') or (x >= u'\u0061' and x<=u'\u007a'):  
           continue  
        else:  
           return False  
    return True  
  
  
#判断是否为中文字符  
def IsChineseChar(varObj):  
  
    if varObj[0] > chr(127):  
       return True  
    return False  
  
#判断帐号是否合法 字母开头，允许4-16字节，允许字母数字下划线  
def IsLegalAccounts(varObj):  
  
    rule = '[a-zA-Z][a-zA-Z0-9_]{3,15}$'  
    match = re.match( rule , varObj )  
  
    if match:  
        return True  
    return False  
  
#匹配IP地址  
def IsIpAddr(varObj):  
  
    rule = '\d+\.\d+\.\d+\.\d+'  
    match = re.match( rule , varObj )  
  
    if match:  
        return True  
    return False  
#----------------验证所有表单提交的数据------end 


#---------------数据子串处理------begin
def HexToByteStr(strHex,zeronumber=8):
    '''
    1,将十六进制的数字转为二进制的Byte数字并且保留去除标准二进制进制表示中的"0b"显示符号
    2,对于不满8位的数字在首位补0
    '''
    empStr = ""
    tempIndexInt = 0
    tempStr = bin(int(strHex,16))
    tempIndexInt = tempStr.find("0b")+2
    return (tempStr[tempIndexInt:]).zfill(zeronumber)

def IntToHexStr(strInt,zeronumber=2):
    '''
    1,将十进制的数字转为十六进制的数字并且保留去除标准十六进制表示中的"Ox"显示符号
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
    returnStr = ""
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
                returnStr = returnStr + strSplit + b[i]
            else :
                returnStr = returnStr + b[i]
    elif sort == 1:
        for i in range(len(b)):
            returnStr = b[i] + strSplit + returnStr
    return returnStr

def HexToIntStr(strHEX,sort=1):
    '''
    1,将十六进制的数字串转化为10进制的数字
    2,sort=1为原有的hex子串是逆向排位,低字节传输在前,高字节排序在后;sort=0为原有的hex子串为正向排位,高字节排序在前,低字节排序在后
    '''
    try :
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
    except:
        returnStr = strHEX
    finally:
        return str(returnStr)
#---------------数据子串处理------End

#--------------时间戳处理--begin
def TimeStrToTimetamp(lsTimes):
    timeArray = time.strptime(lsTimes,"%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return timestamp

def TimetampToTimeStr(liTimestamp):
    timeArray = time.localtime(liTimestamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime   # 2013--10--10 23:40:00

def getNowToTimestamp():
    now = int(time.time())
    return now
    '''timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime'''
#时间戳转换----------End

#获得服务器信息--Begin
def getMacAddress(): #获得mac地址
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
    return ":".join([mac[e:e+2] for e in range(0,11,2)])

#获取本机电脑名
def getServerName(): #获得服务器名称
    returnservername =  socket.getfqdn(socket.gethostname())
    return returnservername

#获取本机ip
def getServerIP(servername='this'): #获得指定服务器ip
    if servername == 'this':
        servername = getServerName()    
    try :
        returnserverip = socket.gethostbyname(servername) 
    except :
        returnserverip = 'Unknown Server IP or Servername is wrong'
    return  returnserverip
#获得服务器信息--End

#文件操作---Begin
def createFolder(DestPath):
    if os.path.isdir(DestPath):
        return 'The target folder has existed!'
    try :
        os.makedirs(DestPath)
        return True
    except Exception,e:
        print "The folder is failure to create, the detial information: " + str(e)
        return False

def getArchivedFolderPath(RootPath,timestamp,interval=5 ) :
    timeArray = time.localtime(timestamp)
    lsyear = time.strftime("%Y", timeArray)
    lsMon = time.strftime("%m", timeArray)
    lsDay = time.strftime("%d", timeArray)
    lsHour = time.strftime("%H", timeArray)
    lsMin = time.strftime("%M", timeArray)
    tempMin  = int(lsMin) / interval
    if tempMin == 0 :
        tempMin = int(lsMin)
    else :
        tempMin = tempMin * interval
    #return RootPath +lsyear+ '\\'+lsMon+ '\\'+lsDay+ '\\'+lsHour+ '\\'+str(tempMin).zfill(2)
    return RootPath +lsyear+ os.sep+lsMon+ os.sep+lsDay+ os.sep+lsHour+ os.sep+str(tempMin).zfill(2) #使用os.sep替代 '\\'用于适合windows和linux 系统

def getFailureFolderPath(FailureFilePath = 'D:\work\DataStore\Firewarning\Failure') :
    return FailureFilePath

def openFile(filename,strsplit="  ") :
    '''
    打开文件并进行内容读取，通过strsplit分隔号，将文件内容进行拆解成为不同的数据段
    :param filename 待打开文件名称
    :param strsplit 内容字串分隔符号
    return 以list形式返回分隔出的内容
    '''
    normalized_dictionary_tokens = []
    if os.path.isfile(filename):
        try:
            f =open(filename, 'r')
            raw_data = f.read()
        # 按照空格将字符串进行切分，成单个单词
            #data = raw_data.split(" ")
            '''
            data = raw_data.split(strsplit)
            for token in data:
                requestData = token
                normalized_dictionary_tokens.append(requestData)
            '''

            symbol = "[" + strsplit + "]+"
            # 一次性分割字符串
            result = re.split(symbol, raw_data)
            # 去除空字符
            normalized_dictionary_tokens = [x for x in result if x]

            f.close()
            return normalized_dictionary_tokens
        except FileNotFoundError:
            print "File is not found."
        except PersmissionError:
            print "You don't have permission to access this file."
        except Exception,e:
            print "Open the file error :"+filename+'.The error message is following:'+e

def moveFile(src, dst): #将OriPath文件夹及其下的文件，转移到DestPath中,采用 os.rename ，通用方法，没有文件类型限制  
     """Recursively move a file or directory to another location. 
  
     If the destination is on our current filesystem, then simply use 
     rename.  Otherwise, copy src to the dst and then remove src. 
     A lot more could be done here...  A look at a mv.c shows a lot of 
     the issues this implementation glosses over. 
  
     """ 
  
     try: 
         os.rename(src, dst) 
     except OSError: 
         if os.path.isdir(src): 
             if destinsrc(src, dst): 
                 raise Error, "Cannot move a directory '%s' into itself '%s'."   % (src, dst) 
             copytree(src, dst, symlinks=True) 
             rmtree(src) 
         else: 
             copy2(src,dst) 
             os.unlink(src) 

def getFileCreatetime(filename,timeType=1): # 获取文件创建时间 timeType =1 返回时间戳，其他返回时间日期型
    if not os.path.isdir(filename) and not os.path.isfile(filename):
        return False
    createtime  = os.path.getctime(filename)
    timestr = TimetampToTimeStr(createtime)
    timestamp =  int(createtime)
    if timeType == 1 :
        returnTime = timestamp
        #print 1
    else:
        returnTime = timestr
        #print 2
    return returnTime


def getFileModifiedtime(filename,timeType=1): # 获取文件最后修改时间 timeType =1 返回时间戳，其他返回时间日期型
    #if not os.path.isdir(filename) and not os.path.isfile(filename):
    #   return False
    Modifiedtime  = os.path.getmtime(filename)
    timestr = TimetampToTimeStr(Modifiedtime)
    timestamp =  int(Modifiedtime)
    if timeType == 1 :
        returnTime = timestamp
        #print 1
    else:
        returnTime = timestr
        #print 2
    return returnTime
#文件操作---End

#文件业务处理操作---begin
def MoveFile(OriPath,DestPath): #将OriPath文件加下的文件，逐个转移到DestPath中
    if not os.path.isdir(OriPath) and not os.path.isfile(OriPath): #判断原目录是否是有效目录或者文件名
        return False
    if not os.path.isdir(DestPath) :  #判断目标目录是否是有效目录
        return False
    try :
        if os.path.isfile(OriPath):
            file_path = os.path.split(OriPath) #分割出目录与文件
            lists = file_path[1].split('.') #分割出文件与文件扩展名
            file_ext = lists[-1] #取出后缀名(列表切片操作)
            unOperation_ext = ['jpg','bmp','log']#用于限制处理文件的类型，可自定义扩展，以'，'分隔
            if file_ext not in unOperation_ext:
            #os.rename(path,file_path[0]+'/'+lists[0]+'_fc.'+file_ext)
                DestFileLocation = os.path.join(DestPath,file_path[1])
                print DestFileLocation
                if os.path.exists(DestFileLocation):
                    os.remove(DestFileLocation)
                shutil.move(OriPath,DestPath)
          #或者
        #img_ext = 'bmp|jpeg|gif|psd|png|jpg'
        #if file_ext in img_ext:
        #    print('ok---'+file_ext)
        elif os.path.isdir(OriPath):
            for x in os.listdir(OriPath):
                MoveFile(os.path.join(OriPath,x),DestPath) #os.path.join()在路径处理上很有用
    except :
        return 'Error during  files archiving'

def IsFileInTimestampRange(filename, beginTimeStemp,endTimeStemp) :#判断文件是否在指定的时间范围内，主要用于增量处理或者更新
    if not os.path.isdir(filename) and not os.path.isfile(filename): #判断原目录是否是有效目录或者文件名
        return False
    filetimstamp = getFileModifiedtime(filename)
    #debug on
    '''
    print beginTimeStemp
    print TimetampToTimeStr(beginTimeStemp)
    print filetimstamp
    print TimetampToTimeStr(filetimstamp)
    print endTimeStemp
    print TimetampToTimeStr(endTimeStemp)
    '''
    #debug off
    if  filetimstamp >= beginTimeStemp and filetimstamp <= endTimeStemp :
        #print 'in this range'
        return True
    else :
        #print 'Not in this range'
        return False

def ScanFolderFiles(OriPath,archivePath, beginTimeStemp='',endTimeStemp=''): #将OriPath文件夹下指定相关时间范围内的文件，逐个转移到DestPath中
    strSplitSymbol= "\s" #用于区分处理文件中字符串的分隔，使用正则方式分隔，默认\s指所有空字符、换行、换页字符用于区隔
    returnDataList = []
    if not os.path.isdir(OriPath) and not os.path.isfile(OriPath): #判断原目录是否是有效目录或者文件名
        return False
    if not os.path.isdir(archivePath) :  #判断目标目录是否是有效目录
        return False
    try :
        if os.path.isfile(OriPath):
            file_path = os.path.split(OriPath) #分割出目录与文件
            lists = file_path[1].split('.') #分割出文件与文件扩展名
            file_ext = lists[-1] #取出后缀名(列表切片操作)
            unOperation_ext = ['jpg','bmp','log']
            if file_ext not in unOperation_ext:
                #os.rename(path,file_path[0]+'/'+lists[0]+'_fc.'+file_ext)
                if beginTimeStemp =='' or endTimeStemp=='':
                    #returnDataList.append(openFile(OriPath))
                    returnDataList.extend(openFile(OriPath,strSplitSymbol))

                    DestFileLocation = os.path.join(archivePath,file_path[1])
                    print DestFileLocation
                    if os.path.exists(DestFileLocation):
                        os.remove(DestFileLocation)

                    shutil.move(OriPath,archivePath)
                    #moveFile(OriPath,archivePath)
                elif IsFileInTimestampRange(OriPath,beginTimeStemp,endTimeStemp) :
                    #returnDataList.append(openFile(OriPath))
                    #if file_path[1] == '152834622281011.txt':
                        #raise RuntimeError('testError')
                    returnDataList.extend(openFile(OriPath,strSplitSymbol))
                    DestFileLocation = os.path.join(archivePath,file_path[1])
                    print DestFileLocation
                    if os.path.exists(DestFileLocation):
                        os.remove(DestFileLocation)
                    shutil.move(OriPath,archivePath)
                    #moveFile(OriPath,archivePath)
          #或者
        #img_ext = 'bmp|jpeg|gif|psd|png|jpg'
        #if file_ext in img_ext:
        #    print('ok---'+file_ext)
        elif os.path.isdir(OriPath):
            for x in os.listdir(OriPath):
                returnDataList.extend(ScanFolderFiles(os.path.join(OriPath,x),archivePath,beginTimeStemp,endTimeStemp) )#os.path.join()在路径处理上很有用
        return returnDataList
    except Exception,e:
        FailurePath = getFailureFolderPath()
        print  'Error during  files archiving :'+file_path[1]+',and the file will be moved to the folder:'+FailurePath
        print e     
        #if os.path.isdir(FailureFilePath) :  #判断原目录是否是有效目录
        DestfailureFileLocation = os.path.join(FailurePath,file_path[1])
        if os.path.exists(DestfailureFileLocation):
            os.remove(DestfailureFileLocation)
        shutil.move(OriPath,FailurePath)
        return returnDataList
#文件业务处理操作---End

#文件压缩处理--Begin

def ZipFile(OriPath,DestZipPath,isDelOri = False,zipfilename="Firewarning"): #将OriPath文件加下的文件，压缩到DestPath中，todo: 并删除原有文件
    if not os.path.isdir(OriPath) and not os.path.isfile(OriPath): #判断原目录是否是有效目录或者文件名
        return False
    if not os.path.isdir(DestZipPath) :  #判断目标目录是否是有效目录
        return False
    try :
        ''''' 
        将文件夹下的文件保存到zip文件中。 
        :param OriPath: 待备份文件或者文件夹 
        :param DestZipPath: 备份路径
        :param zipfilename: 备份基本名文件名（用于却别备份类别）+时间戳  
        :param isDelOri: 是否删除源文件 
        :return: boolean值，成功或者失败
        '''  
        today = time.strftime('%Y%m%d')  
        now = time.strftime('%H%M%S')  
        fileList=[]
        #lsDestZipPath = DestZipPath+ os.sep+ today 
        lsDestZipPath=os.path.join(DestZipPath,today) 
        if not os.path.exists(lsDestZipPath):  
            createFolder(lsDestZipPath)   #os.mkdir(lsDestZipPath)  
            print('mkdir successful')  
        target = os.path.join(lsDestZipPath,zipfilename+now + '.zip')
        newZip = zipfile.ZipFile(target,'w') 
        for dirpath,dirnames,filenames in os.walk(OriPath):  
            for filename in filenames:  
                fileList.append(os.path.join(dirpath,filename)) 
                #print os.path.join(dirpath,filename) 
        for tar in fileList:  
            newZip.write(tar,tar[len(OriPath):])#tar为写入的文件，tar[len(filePath)]为保存的文件名，保持从备份目录到子目录的所有目录结构 
            #newZip.write(tar)#tar为写入的文件，保持从根目录到子目录的所有目录结构
        newZip.close()  
        print('backup to',target)  
        if isDelOri :
            #print(os.path.dirname(OriPath),OriPath)
            shutil.rmtree(os.path.dirname(OriPath)) #shutil.rmtree删除目录及子目录中的所有内容，os.removedirs递归删除目录子目录，remove针对文件，rmdir针对空文件夹
            #os.remove(os.path.dirname(OriPath))
        return True
    except Exception, e:
        print 'Error during  files archiving, the detial information is following : '+e
        return False

def unZip(zippedFilePath,unzipPath):  #解压zip文件到指定路径 
    ''''' 
    解压zip文件到指定路径 
    :param zippedFilePath: 待解压文件 
    :param unzipPath: 解压路径 
    :return:  
    '''
    if not os.path.isdir(zippedFilePath) and not os.path.isfile(zippedFilePath): #判断原目录是否是有效目录或者文件名
        return False
    if not os.path.isdir(unzipPath) :  #判断目标目录是否是有效目录
        return False
    try :  
        file = zipfile.ZipFile(zippedFilePath)  
        file.extractall(unzipPath)  
        print ('unzip the file {} successfully to '+ unzipPath).format(zippedFilePath)
    except Exception, e:
        print 'Error during  files unzippint, the detial information is following : '+str(e)
        return False
#文件压缩处理--End

def GetMsgBody(MsgTemlate,Paramdict = {'Name': 'Zara', 'Age': 7}):
    ''''' 
    将消息模板MsgTemlate中需要替换的内容以 Paramdict字典方式传入的对象，逐个键值匹配，每个键值在模板中的形式是'$[键值]'(注意大小写敏感）
    :param MsgTemlate: 消息模板内容Content，以Str方式传入 
    :param Paramdict: 解压路径 
    :return:  返回完整消息内容
    ''' 
    returnMsgBody = MsgTemlate
    ParamKeylist  = Paramdict.keys()
    for x in ParamKeylist:#轮询字典中的每个key，并对模板进行替换
        strlabal = str(x) #根据传入的参数字典内容将邮件模板中的对应项目进行替换
        OriStr = '$['+strlabal+']'#在模板中需要动态替换的值，未来考虑产品化时在数据库中维护，并与模板名称绑定
        NewStr = str(Paramdict[strlabal])
        returnMsgBody = returnMsgBody.replace(OriStr,NewStr)
    return returnMsgBody

#Warning处理--Begin
class SendMailClientMgt:
    def __init__(self, MailboxSMTPsrv='smtp.sina.com'):
        self.__MailboxSMTPsrv=MailboxSMTPsrv
        self.__MailTemplate = u'小朋友$[Name]同学,今年$[Age]岁'

    def sendMail(self,MailboxUser,MailboxPWD,MailTo,MailTitle,MailMessage):
        ''''' 
        :param MailboxUser: 发件人邮箱地址 
        :param MailboxPWD: 发件人邮箱登录密码
        :param MailTo: 收件人邮箱地址 
        :param MailTitle: 邮件标题
        :param MailMessage: 邮件内容  
        :return:  返回发送成功或者失败的消息
        ''' 
        # f = open(file_new,'rb')
        # mail_body = f.read()
        # f.close()
        # 读取最新测试报告的内容
        #with open("H:\\AS-automation\as-testcase\Api_01\m66y.zip", "rb") as f:
        #mail_body = f.read()
        if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$',MailTo): 
            return u"邮件地址格式错误:"+ MailTo
        msg = MIMEMultipart()
        body = MIMEText(MailMessage, 'HTML', 'utf-8')#邮件内容
        msg['Subject'] = Header(MailTitle, 'utf-8')#邮件的标题
        msg['From'] = MailboxUser
        msg['To'] = MailTo
        msg.attach(body)
        #
        #
        #添加附件
        '''
        att=MIMEText(open("H:\\AS-automation\\as-testcase\\Api_01\\m66y.zip","rb").read(),"base64","utf-8")#打开附件地址
        att["Content-Type"] = "application/octet-stream"
        att["Content-Disposition"] ='attachment; filename="m66y.zip"'
        msg.attach(att)
        '''
        #
        #
        #发送邮件
   
        try:
            s = smtplib.SMTP(self.__MailboxSMTPsrv)
            s.login(MailboxUser,MailboxPWD)  # 登录邮箱的账户和密码
            s.sendmail(MailboxUser,MailTo, msg.as_string())#发送邮件
            s.quit()
            return u"Status：Success。邮件发送成功" 
        except Exception,e:
            return u"Status：Error。无法发送邮件,详细原因："+e
    

        
class SystemInfo(object):
    """
    Get operating system information
    """
    def __init__(self):
        pass

    def network_info(self,pbPrnic=True):
        #net_io_counters() 
        try:
            result = psutil.net_io_counters(pernic=pbPrnic)
            print result
        except Exception, e:
            print e
        finally:
            return result

    def net_connections(self) :
        #net_connection() 
        try:
            result = psutil.net_connections()
            print result
        except Exception, e:
            print e
        finally:
            return result
 
    def process_info(self):
        """
        :return: A list of all process details of the system
        """
        proc, all_processes = [],  psutil.process_iter()
        for items in all_processes:
            try:
                procinfo = items.as_dict(attrs=["pid", "name"])
                try:
                    #the process start path
                    p_path_cwd = items.cwd().decode("gbk")
 
                    #the process accounts for system memory uasge
                    proc_mem_percent = items.memory_percent()
 
                    #the process starts cmdline content
                    cmdlines = str(items.cmdline())
 
                    #the process accounts for system CPU usage
                    cpu_percent = items.cpu_percent(interval=1)
                except Exception,e:
                    try:
                        p_path_cwd = items.exe()
                    except Exception,e:p_path_cwd = e.name
                p_status, p_create_time, proc_user, proc_io_info = items.status(), items.create_time(),items.username() , {}
 
                try:
                    proc_io = items.io_counters()
                    proc_io_info["ReadCount"] = proc_io.read_count
                    proc_io_info["WriteCount"] = proc_io.write_count
                    proc_io_info["ReadBytes"] = proc_io.read_bytes
                    proc_io_info["WriteBytes"] = proc_io.write_bytes
                except Exception,e:pass
                procinfo.update({"path": p_path_cwd,
                                 "cmdline":cmdlines,
                                 "cpu_percent":cpu_percent,
                                 "status": p_status,
                                 "CreateTime": p_create_time,
                                 "MemPercent": proc_mem_percent,
                                 "user": proc_user,
                                 "DiskIo": proc_io_info})
            except Exception, e:pass
            finally:
                proc.append(procinfo)
        return proc

     
    def QueryServerInfo(self):
        global cput,cp
        cput=psutil.cpu_times()
        cp=psutil.disk_io_counters()



class SMSClientMgt:
    def __init__(self, ACCESS_KEY_ID = "LTAIfiRSUppU9kiO", ACCESS_KEY_SECRET = "suTc9XmYlV88BMXo1mDRJMxid2NYrB"):
        #对于阿里的短信网关，不可以修改
        self.__REGION = "cn-hangzhou"
        self.__PRODUCT_NAME = "Dysmsapi"
        self.__DOMAIN = "dysmsapi.aliyuncs.com"
        #由申请相关阿里短信网关服务时返回获得
        self.__ACCESS_KEY_ID = ACCESS_KEY_ID
        self.__ACCESS_KEY_SECRET = ACCESS_KEY_SECRET
        


    def sendSMS(self,business_id, phone_numbers, sign_name, template_code, template_param=None):
        ''''' 
        :param business_id: 发件系统用于自身业务管理的唯一业务号 
        :param phone_numbers: 接受短信手机号码，可以用','区隔多个手机号
        :param sign_name: 在阿里云短信服务开通时申请的应用对应签名 
        :param template_code: 在阿里云短信服务开通时申请的应用对应模板编号
        :param template_param: 在阿里云短信服务开通时申请的应用对应模板中需要替换的具体内容  
        :return:  返回发送成功或者失败的消息
        ''' 
        try :
            acs_client = AcsClient(self.__ACCESS_KEY_ID, self.__ACCESS_KEY_SECRET, self.__REGION)
            region_provider.add_endpoint(self.__PRODUCT_NAME, self.__REGION, self.__DOMAIN)
        except Exception,e:
            print e 

        smsRequest = SendSmsRequest.SendSmsRequest()
        # 申请的短信模板编码,必填
        smsRequest.set_TemplateCode(template_code)

        # 短信模板变量参数
        if template_param is not None:
            smsRequest.set_TemplateParam(template_param)
        
        # 设置业务请求流水号，必填。
        smsRequest.set_OutId(business_id)

        # 短信签名
        smsRequest.set_SignName(sign_name)
        # 数据提交方式
        # smsRequest.set_method(MT.POST)
        
        # 数据提交格式
        # smsRequest.set_accept_format(FT.JSON)
        
        # 短信发送的号码列表，必填。
        smsRequest.set_PhoneNumbers(phone_numbers)

        # 调用短信发送接口，返回json
        smsResponse = acs_client.do_action_with_exception(smsRequest)

        # TODO 业务处理
        return smsResponse

    def querySendDetail(self, phone_number, page_size, current_page, send_date,biz_id=""):
        ''''' 
        用于查询业务已经发送的短信及内容
        :param biz_id: 发件系统用于自身业务管理的唯一业务号，可选 
        :param phone_numbers: 接受短信手机号码，可以用','区隔多个手机号
        :param page_size: 每次返回的每页数量 
        :param current_page: 当前页数
        :param send_date: 短信发送的时间 
        :return:  返回发送查询得到的数据
        ''' 
        try :
            acs_client = AcsClient(self.__ACCESS_KEY_ID, self.__ACCESS_KEY_SECRET, self.__REGION)
            region_provider.add_endpoint(self.__PRODUCT_NAME, self.__REGION, self.__DOMAIN)
        except Exception,e:
            print e 
        queryRequest = QuerySendDetailsRequest.QuerySendDetailsRequest()
        # 查询的手机号码
        queryRequest.set_PhoneNumber(phone_number)
        # 可选 - 流水号
        if not biz_id =="":
            queryRequest.set_BizId(biz_id)
        # 必填 - 发送日期 支持30天内记录查询，格式yyyyMMdd
        queryRequest.set_SendDate(send_date)
        # 必填-当前页码从1开始计数
        queryRequest.set_CurrentPage(current_page)
        # 必填-页大小
        queryRequest.set_PageSize(page_size)
        # 数据提交方式
        # queryRequest.set_method(MT.POST)
        # 数据提交格式
        # queryRequest.set_accept_format(FT.JSON)
        # 调用短信记录查询接口，返回json
        queryResponse = acs_client.do_action_with_exception(queryRequest)
        # TODO 业务处理
        return queryResponse

#Waring处理--end

#d ='4F00010012040f080612020202020202010101010101300004'
#print(GetChecksumValue(d))

class prpcrypt(): #用于完成特殊字符串的存储加密,例如数据库访问用户名和密码
    def __init__(self, key,Vi=b"0000000000000000",length = 16):
        self.key = key
        self.strlength = length #加密字串的长度只能是16的倍数
        self.Vi = Vi
        count = len(key)
        if(count % self.strlength != 0) :
            add = self.strlength - (count % self.strlength)
        else:
            add = 0
        self.keyAdd = add
        self.key = self.key + ('\0' * self.keyAdd)
        self.mode = AES.MODE_CBC
    '''
    调用示例
    pc = prpcrypt("0123456789ABCDEF")      #初始化密钥
    e = pc.encrypt("liangqihui@sina.com.cn")
    d = pc.decrypt(e)
    '''
    #加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.Vi)
        #这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        
        count = len(text)
        if(count % self.strlength != 0) :
            Txtadd = self.strlength - (count % self.strlength)
        else:
            Txtadd = 0
            
        text = text + ('\0' * Txtadd)
        self.ciphertext = cryptor.encrypt(text)
        #因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        #所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)
     
    #解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode,self.Vi)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')

class SqlPaser():
    def __init__():
        pass
    
    def getInsertSqlStr(self, Sqltemplate="",psTable="user",psParamdict = {'Name': 'Zara', 'Age': 7}):
        ''''' 
        将消息模板MsgTemlate中需要替换的内容以 Paramdict字典方式传入的对象，逐个键值匹配，每个键值在模板中的形式是'$[键值]'(注意大小写敏感）
        :param MsgTemlate: 消息模板内容Content，以Str方式传入 
        :param Paramdict: 解压路径 
        :return:  返回完整消息内容
        ''' 
        returnMsgBody = MsgTemlate
        ParamKeylist  = Paramdict.keys()
        for x in ParamKeylist:#轮询字典中的每个key，并对模板进行替换
            strlabal = str(x) #根据传入的参数字典内容将邮件模板中的对应项目进行替换
            OriStr = '$['+strlabal+']'#在模板中需要动态替换的值，未来考虑产品化时在数据库中维护，并与模板名称绑定
            NewStr = str(Paramdict[strlabal])
            returnMsgBody = returnMsgBody.replace(OriStr,NewStr)
        return returnMsgBody
 
 
class ImgMgt():
	def __init__():
		pass
	'''
		python图片处理
		@author:fc_lamp
		@blog:http://fc-lamp.blog.163.com/
	'''


	#等比例压缩图片
	def resizeImg(self,**args):
		args_key = {'ori_img':'','dst_img':'','dst_w':'','dst_h':'','save_q':75}
		arg = {}
		for key in args_key:
			if key in args:
				arg[key] = args[key]
			
		im = image.open(arg['ori_img'])
		ori_w,ori_h = im.size
		widthRatio = heightRatio = None
		ratio = 1
		if (ori_w and ori_w > arg['dst_w']) or (ori_h and ori_h > arg['dst_h']):
			if arg['dst_w'] and ori_w > arg['dst_w']:
				widthRatio = float(arg['dst_w']) / ori_w #正确获取小数的方式
			if arg['dst_h'] and ori_h > arg['dst_h']:
				heightRatio = float(arg['dst_h']) / ori_h

			if widthRatio and heightRatio:
				if widthRatio < heightRatio:
					ratio = widthRatio
				else:
					ratio = heightRatio

			if widthRatio and not heightRatio:
				ratio = widthRatio
			if heightRatio and not widthRatio:
				ratio = heightRatio
				
			newWidth = int(ori_w * ratio)
			newHeight = int(ori_h * ratio)
		else:
			newWidth = ori_w
			newHeight = ori_h
			
		im.resize((newWidth,newHeight),image.ANTIALIAS).save(arg['dst_img'],quality=arg['save_q'])

		'''
		image.ANTIALIAS还有如下值：
		NEAREST: use nearest neighbour
		BILINEAR: linear interpolation in a 2x2 environment
		BICUBIC:cubic spline interpolation in a 4x4 environment
		ANTIALIAS:best down-sizing filter
		'''

	#裁剪压缩图片
	def clipResizeImg(self,**args):
		
		args_key = {'ori_img':'','dst_img':'','dst_w':'','dst_h':'','save_q':75}
		arg = {}
		for key in args_key:
			if key in args:
				arg[key] = args[key]
			
		im = image.open(arg['ori_img'])
		ori_w,ori_h = im.size

		dst_scale = float(arg['dst_h']) / arg['dst_w'] #目标高宽比
		ori_scale = float(ori_h) / ori_w #原高宽比

		if ori_scale >= dst_scale:
			#过高
			width = ori_w
			height = int(width*dst_scale)

			x = 0
			y = (ori_h - height) / 3
			
		else:
			#过宽
			height = ori_h
			width = int(height*dst_scale)

			x = (ori_w - width) / 2
			y = 0

		#裁剪
		box = (x,y,width+x,height+y)
		#这里的参数可以这么认为：从某图的(x,y)坐标开始截，截到(width+x,height+y)坐标
		#所包围的图像，crop方法与php中的imagecopy方法大为不一样
		newIm = im.crop(box)
		im = None

		#压缩
		ratio = float(arg['dst_w']) / width
		newWidth = int(width * ratio)
		newHeight = int(height * ratio)
		newIm.resize((newWidth,newHeight),image.ANTIALIAS).save(arg['dst_img'],quality=arg['save_q'])
		

	#水印(这里仅为图片水印)
	def waterMark(self,**args):
		args_key = {'ori_img':'','dst_img':'','mark_img':'','water_opt':''}
		arg = {}
		for key in args_key:
			if key in args:
				arg[key] = args[key]
			
		im = image.open(arg['ori_img'])
		ori_w,ori_h = im.size

		mark_im = image.open(arg['mark_img'])
		mark_w,mark_h = mark_im.size
		option ={'leftup':(0,0),'rightup':(ori_w-mark_w,0),'leftlow':(0,ori_h-mark_h),
				 'rightlow':(ori_w-mark_w,ori_h-mark_h)
				 }
		

		im.paste(mark_im,option[arg['water_opt']],mark_im.convert('RGBA'))
		im.save(arg['dst_img'])
		

			
	#Demon
	#源图片
	#ori_img = 'D:/tt.jpg'
	#水印标
	#mark_img = 'D:/mark.png'
	#水印位置(右下)
	#water_opt = 'rightlow'
	#目标图片
	#dst_img = 'D:/python_2.jpg'
	#目标图片大小
	#dst_w = 94
	#dst_h = 94
	#保存的图片质量
	#save_q = 35
	#裁剪压缩
	#clipResizeImg(ori_img=ori_img,dst_img=dst_img,dst_w=dst_w,dst_h=dst_h,save_q = save_q)
	#等比例压缩
	#resizeImg(ori_img=ori_img,dst_img=dst_img,dst_w=dst_w,dst_h=dst_h,save_q=save_q)
	#水印
	#waterMark(ori_img=ori_img,dst_img=dst_img,mark_img=mark_img,water_opt=water_opt)
