# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-06-21 17:37:47
# @Last Modified by:   leonliang
# @Last Modified time: 2018-07-01 19:01:24
import re
import time
import os
import MySQLdb
import shutil
import uuid
import socket
import psutil
import smtplib #mail
import zipfile   #zipfiles
from email.mime.text import MIMEText #mail
from email.header import Header #mail
from email.mime.multipart import MIMEMultipart #mail
#from FWWebAPI.aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest #sms
#from FWWebAPI.aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest #sms
#from aliyunsdkcore.client import AcsClient #sms
#from aliyunsdkcore.profile import region_provider  #sms
#from aliyunsdkcore.http import method_type as MT  #sms
#from aliyunsdkcore.http import format_type as FT  #sms


#时间戳转换----------begin
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
            return normalized_dictionary_tokens
        except FileNotFoundError:
            print "File is not found."
        except PersmissionError:
            print "You don't have permission to access this file."
        except Exception,e:
            print "Open the file error :"+filename+'.The error message is following:'+e
        finally :
            f.close()

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
        returnVal = True
    else :
        #print 'Not in this range'
        returnVal = False

    return returnVal

def ScanFolderFiles(OriPath,archivePath, beginTimeStemp='',endTimeStemp=''): #将OriPath文件夹下指定相关时间范围内的文件，逐个转移到DestPath中
    strSplitSymbol= "\s" #用于区分处理文件中字符串的分隔，使用正则方式分隔，默认\s指所有空字符、换行、换页字符用于区隔
    returnDataList = []
    #OriPath = unicode(OriPath,'utf-8')
    #archivePath =unicode(archivePath,'utf-8')
    if not os.path.isdir(OriPath) and not os.path.isfile(OriPath): #判断原目录是否是有效目录或者文件名
    	print OriPath
        return False
    if not os.path.isdir(archivePath) :  #判断目标目录是否是有效目录
    	print archivePath
        return False
    try :
        if os.path.isfile(OriPath):
            file_path = os.path.split(OriPath) #分割出目录与文件
            lists = file_path[1].split('.') #分割出文件与文件扩展名
            file_ext = lists[-1] #取出后缀名(列表切片操作)
            unOperation_ext = ['pdm']#'jpg','bmp','log','pdm'

            if file_ext  in unOperation_ext:
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
        #return returnDataList
    except Exception,e:
        FailurePath = getFailureFolderPath()
        print  'Error during  files archiving :'+file_path[1]+',and the file will be moved to the folder:'+FailurePath
        print e     
        #if os.path.isdir(FailureFilePath) :  #判断原目录是否是有效目录
        DestfailureFileLocation = os.path.join(FailurePath,file_path[1])
        if os.path.exists(DestfailureFileLocation):
            os.remove(DestfailureFileLocation)
        shutil.move(OriPath,FailurePath)
    finally:
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
        returnVal =  True
    except Exception, e:
        print 'Error during  files archiving, the detial information is following : '+e
        returnVal = False
    finally:
        return returnVal

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
        returnVal =  True
    except Exception, e:
        print 'Error during  files unzippint, the detial information is following : '+str(e)
        returnVal =  False
    finally :
        return returnVal
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
            #s.quit()
            returnVal =  u"Status：Success。邮件发送成功" 
        except Exception,e:
             returnVal =  u"Status：Error。无法发送邮件,详细原因："+e
        finally :
            s.quit()
            return returnVal
    



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


#读取文件，并将文件中的内容逐行提取

print 'start at :'+TimetampToTimeStr(getNowToTimestamp())
GetDataList = []
Orifolder = unicode('D:\\01.综合业务系统本地同步开发资源库\\','utf-8')
Destfolder = unicode('D:\\work\DataStore\pdms\\','utf-8')
DestZipfolder = unicode('D:\work\DataStore\Firewarning\Zip\\','utf-8')
ServerName = getServerName()
ServerIP =getServerIP()
LastOptTimeStamp = 1529576239
CurrentTimeStamp =getNowToTimestamp()
print CurrentTimeStamp
ArchFolder = Destfolder#getArchivedFolderPath(Destfolder,CurrentTimeStamp)
createFolder(Destfolder)
llist = ScanFolderFiles(Orifolder,ArchFolder)
#print llist
#ZipFile(Destfolder,DestZipfolder)
#ZipFile('D:\work\DataStore\Firewarning\Done2\\',DestZipfolder,True)
#unZip(r'D:\work\DataStore\Firewarning\Zip\20180624\Firewarning104442.zip',r'D:\work\DataStore\Firewarning\Unzip')
#测试消息体拼接
#print(GetMsgBody( u'小朋友$[Name]同学,今年$[Age]岁'))


#测试邮件发送成功
'''
#mailsrv = SendMailClientMgt()
#print(mailsrv.sendMail('liangqihui@sina.com.cn','804270sina','liang_qihui@hotmail.com','mail start at :'+TimetampToTimeStr(getNowToTimestamp()),u'测试邮件正文'))
'''

#测试短消息发送成功 templatecode SMS_137689254
'''
------------------------
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"
ACCESS_KEY_ID = "LTAIfiRSUppU9kiO"
ACCESS_KEY_SECRET = "suTc9XmYlV88BMXo1mDRJMxid2NYrB"
RecievePhonelist="18621119006,13778066793,1860027053"
acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

---------------------------------
RecievePhonelist="18621119006"
__business_id = uuid.uuid1()
#print(__business_id)
params = "{\"status\":\"异常\",\"Build\":\"机关大楼\",\"min\":\"10\",\"CaseID\":\"1234567\"}"
#smsClient = SMSClientMgt()
#print(smsClient.sendSMS(__business_id, RecievePhonelist, "消防火警监控平台测试", "SMS_137659377", params))
#print(smsClient.querySendDetail("18621119006", 10, 1, "20180623"))
'''


#显示当前进程状态
'''
info = psutil.virtual_memory()
print u'内存使用(M)：',psutil.Process(os.getpid()).memory_info().rss/1024/1024 
print u'总内存(G)：',info.total/1024/1024/1024
print u'内存占比：',info.percent
print u'cpu个数：',psutil.cpu_count()
print llist
print 'end at :'+TimetampToTimeStr(getNowToTimestamp())
'''
#MoveFile(Destfolder,Orifolder)
#print getFileCreatetime('E:\Software\Navicat for MySQL\msvcr100.dll')


#显示当前服务器状态
'''
------------------------------
print getMacAddress()
print getServerName()
print getServerIP('2013-20160918ZU1')
print getServerIP()
print socket.gethostname()
'''

#targetdir = getArchivedFolderPath(Destfolder,int(time.time()))
#createFolder(targetdir)
'''
tss1 = '2013-10-10 23:40:00'    
print TimeStrToTimetamp(tss1)

tss2  = 1529576239
print TimetampToTimeStr(tss2)

print getNowToTimestamp()

#print int(time.time())
'''
'''''''''''''''
nowtimestamp =getNowToTimestamp()

if IsFileInTimestampRange(Orifolder+'1.mp4',1427300510,nowtimestamp):
    MoveFile(Orifolder+'1.mp4',Destfolder)
'''''''''''''''
'''
os.listdir(dirname)：列出dirname下的目录和文件
os.getcwd()：获得当前工作目录
os.curdir:返回当前目录（'.')
os.chdir(dirname):改变工作目录到dirname

os.path.isdir(name):判断name是不是一个目录，name不是目录就返回false
os.path.isfile(name):判断name是不是一个文件，不存在name也返回false
os.path.exists(name):判断是否存在文件或目录name
os.path.getsize(name):获得文件大小，如果name是目录返回0L

os.path.abspath(name):获得绝对路径
os.path.normpath(path):规范path字符串形式
os.path.split(name):分割文件名与目录（事实上，如果你完全使用目录，它也会将最后一个目录作为文件名而分离，同时它不会判断文件或目录是否存在）
os.path.splitext():分离文件名与扩展名
os.path.join(path,name):连接目录与文件名或目录
os.path.basename(path):返回文件名
os.path.dirname(path):返回文件路径

os.remove(dir) #dir为要删除的文件夹或者文件路径
os.rmdir(path) #path要删除的目录的路径。需要说明的是，使用os.rmdir删除的目录必须为空目录，否则函数出错。

os.path.getmtime(name) ＃获取文件的修改时间 

os.stat(path).st_mtime＃获取文件的修改时间

os.stat(path).st_ctime #获取文件修改时间

os.path.getctime(name)#获取文件的创建时间

shutil.move('d:/c.png','e:/') 把文件从前方移动到制定目录
'''