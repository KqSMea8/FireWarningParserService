# -*- coding: utf-8 -*-
# @Author: liangqihui
# @Date:   2018-06-29 16:11:06
# @Last Modified by:   Leon Liang
# @Last Modified time: 2018-06-29 19:22:33

import os 
import re
import time
import socket
import psutil
import MySQLdb
from DBUtils.PooledDB import PooledDB
import Config as GlobalVar
import toolkits 
#import FWWebAPI.Business.Config as GlobalVar
#import FWWebAPI.Business.toolkits as toolkits
from threading import Timer



class SrvControlBase(object):
    """docstring for SrvControl"""
    def __init__(self, psSrvName,DB=GlobalVar.DBConfig,pitimerInterval = GlobalVar.ServiceConfig["SrvInterval"],piTimeoutInterval= GlobalVar.ServiceConfig["TimeoutInterval"],pisrvGroupid=0 ): #{"host":"","port":"3306","user":"root","pwd":"1qazxsw@","db":"firewarning","charset":"utf8"}
        #super(ClassName, self).__init__()
        '''
        @param psSrvName #当前服务名称,用于区别各个不同的服务内容类别,但是系统数据库中有groupid用于识别同名srvname但是mac地址不相同的服务器,作为cluster内容进行运行
        @param DB #用于获得数据库访问信息,从Business/Config.py中DBConfig配置
        @pitimerInterval #用于获得服务运行的间隔从Business/Config.py中ServiceConfig配置
        @piTimeoutInterval #用于获得监控服务进行心跳访问运行的间隔,从Business/Config.py中ServiceConfig配置
        '''
        self.SrvName = psSrvName
        self.SrvMacAddress = toolkits.getMacAddress()
        self.ServerName = toolkits.getServerName()
        self.ServerIPAddress = toolkits.getServerIP()
        self.HostName = socket.gethostname()
        self.timer_interval = pitimerInterval #每5秒扫描一次
        self.TimeoutInterval = piTimeoutInterval #监控服务每120秒向数据库更新一次心跳状态,如果数据库中最后一次心跳LastSuccessHeartBeat时间超过360秒(3次心跳),则服务状态isactive将被更新为0,ServerStatus被设置为Stop
        self.SrvInstID = 0
        self.SrvInstSerNumTag = "SrvInstSERIALNUM"
        self.SrvInstExecSerNumTag = "SrvInstExecSERIALNUM"
        self.SrvGroupID =pisrvGroupid
        self.conn = MySQLdb.connect(host=DB["host"],port=int(DB["port"]),user=DB["user"],passwd=DB["pwd"],db=DB["db"],charset=DB["charset"]) #方法一
        #self.pool = PooledDB(MySQLdb,5,DB["host"],user=DB["user"],passwd=DB["pwd"],db='warning',port=int(DB["port"]),charset =DB["charset"]) #方法二,5为连接池里的最少连接数--本地库
        
        '''
        self.conn= MySQLdb.connect(   # 连接数据库
            host='',   # 连接你要取出数据库的ip，如果是本机可以不用写
            port = 3306,
            user='***',     # 你的数据库用户名
            passwd='******',# 你的数据库密码
            db ='firewarning',
            charset='utf8',)
        '''


    def getConnection(self):
        return self.conn # 方法一
        #return self.pool.connection()  #方法二,以后每次需要数据库连接就是用connection（）函数获取连接就好了

    def getSerNum(self,SerNumTag =  'SrvInstExecSERIALNUM' ): #SerNumTag = 'SrvInstExecSERIALNUM'
        conn = self.getConnection()
        getSerNumSql= 'select _nextval(\''+SerNumTag+'\')'
        try:
            with conn:
                lcur = conn.cursor()
                sql = getSerNumSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchone()
                #conn.close() #getConnection实现方法二 可close,方法一不用close
                strSerNum = str(serNum[0])
                return strSerNum
        except Exception, e:
            raise e

    #-------------------Service Instance------------启停状态操作信息更新 Begin------------
    def getMaxSrvVersionID(self,psSrvName ,psSrvMacAdd  ): #用于获取最大的服务版本号
        conn = self.getConnection()
        getMaxSrvVerSql= "select ifnull(max(VersionID),0) from srvhostcontrolmgt where SrvName = '"+psSrvName +"' and servermacadd = '"+psSrvMacAdd +"'"
        try:
            with conn:
                lcur = conn.cursor()
                sql = getMaxSrvVerSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchone()
                #conn.close() #getConnection实现方法二 可close,方法一不用close
                strSerNum = str(int(serNum[0])+1)
                return strSerNum
        except Exception, e:
            raise e           

    def SrvStart(self,psSrvName ,pssrvMacAdd,pisrvGroupid=0 ):#用于继承，override 成为具体的服务代码（从其他库中引用的具体函数）
        print psSrvName+u"服务已经启动："+ toolkits.TimetampToTimeStr(toolkits.getNowToTimestamp())
        conn = self.getConnection()
        strTable = "srvhostcontrolmgt"
        strColumnsStatement  = ""
        strValuesStatement = ""
        OriStr = "@{Table}"
        InsertSql = GlobalVar.SqlStrTemplates["InsertSql"]
        InsertSql = InsertSql.replace(OriStr,strTable)
        UpdateSql = GlobalVar.SqlStrTemplates["UpdateSql"]
        SrvInstDataSet ={"ID" :self.SrvInstID,
                    "Servername" :  self.ServerName,
                    "SrvName" :psSrvName,
                    "ServerMacAdd" :pssrvMacAdd,
                    "ServerIPAdd" :self.ServerIPAddress,
                    "ServerStatus":"Running",
                    "SrvStartTime":"UNIX_TIMESTAMP( )",
                    "SrvStartStopTime": "",
                    "SrvInterval": self.timer_interval,
                    "TimeoutInterval" : self.TimeoutInterval,
                    "LastSuccessHeartBeat" : "",
                    "Isactive": 1,
                    "VersionID" : 0,
                    "SrvConfig" : "",
                    "Comments" : "",
                    "GroupID" :pisrvGroupid #当服务启动在不同机器上且需要连续计算最后执行时间时候,将groupid设置为非0数字,由groupid和srvname进行联合分组
                    }
        

        # if IsString(obj) :
            #lstemp = " '"+ obj+ "' "        
        try:
            returnSrvInstID = self.getSrvStatus(psSrvName,pssrvMacAdd,"Running")# 确认是否有运行状态的
            if returnSrvInstID >0:
                scriptPath = self.getDictCur("SELECT executescript FROM srvhostcontrolmgt WHERE ID = %d" % (returnSrvInstID))
                if len(scriptPath) >0:                    
                    if os.path.exists(scriptPath[0]["executescript"]):
                        print("running service %s" % scriptPath[0]["executescript"])
                        execfile(scriptPath[0]["executescript"])
                return returnSrvInstID #判断是否已经有Running状态的服务实例,如有返回ID

            returnSrvInstID = self.getSrvStatus(psSrvName,pssrvMacAdd,"Suspended")# 确认是否有挂起状态的
            if returnSrvInstID >0:                 
                 return returnSrvInstID

            returnSrvInstID = self.getSrvStatus(psSrvName,pssrvMacAdd,"Resume")# 确认是否有准备恢复状态的
            if returnSrvInstID >0:                 
                 return returnSrvInstID

            returnSrvInstID = self.getSerNum(self.SrvInstSerNumTag)
            SrvInstDataSet["ID"] = returnSrvInstID
            SrvInstDataSet["VersionID"] = self.getMaxSrvVersionID(psSrvName,pssrvMacAdd)
            SrvInstDataSet["Comments"] = ' Comments= CONCAT(now(),":服务被启动" ,  ) ,"; ",ifnull(comments,"")'
            #SrvInstDataSet["Comments"] = " Comments= CONCAT(now(),':服务被启动' ,  )"
            ParamKeylist  = SrvInstDataSet.keys()
            ParamValuelist = SrvInstDataSet.values()
            #for x in ParamKeylist:#轮询字典中的每个key，并对模板进行替换
                #strlabal = str(x) #根据传入的参数字典内容将sql模板中的对应项目进行替换
                #NewStr = NewStr+", "+str(strlabal)
            NewStr = ' , '.join(ParamKeylist)
            OriStr = '$[ColumnsStatement]'#在模板中需要动态替换的值，未来考虑产品化时在数据库中维护，并与模板名称绑定
            InsertSql = InsertSql.replace(OriStr,NewStr)

            NewStr =""
            for x in ParamValuelist:#轮询字典中的每个key，并对模板进行替换
                lstemp = str(x)
                if len(lstemp)==0:
                    lstemp = "null"
                elif lstemp not in ["now()","UNIX_TIMESTAMP( )","CURRENT_TIMESTAMP()"]:
                   if toolkits.IsString(x) :
                       lstemp = " '"+ str(x)+ "' "
                if len(NewStr) == 0 :
                    NewStr = lstemp
                else :
                    NewStr = NewStr+' , '+ lstemp
        
            OriStr = '$[ValuesStatement]'#在模板中需要动态替换的值，未来考虑产品化时在数据库中维护，并与模板名称绑定
            InsertSql = InsertSql.replace(OriStr,NewStr)


            UpdateSql = UpdateSql.replace("@{Table}",strTable)
            UpdateSql = UpdateSql.replace("$[SetValuesStatement]","Isactive = 0,")
            UpdateSql = UpdateSql.replace("$[ClauseStatement]","ID not in( "+str(returnSrvInstID)+") and SrvName = '"+psSrvName +"' and servermacadd = '"+pssrvMacAdd +"' ")
            #unOperation_ext = ["running","stop","suspended","crash"]
            #print InsertSql
            #return InsertSql # 返回值 


            with conn:
                lcur = conn.cursor()
                sql = InsertSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchone()
                #conn.close() #getConnection实现方法二 可close,方法一不用close
                #strSerNum = str(serNum[0])
                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                self.SrvInstID = returnSrvInstID
                return returnSrvInstID
        except Exception, e:
            raise e
        #更新服务启动时刻
       

    def SrvStop(self,psrvInstID,psReason=""):#用于继承，override 成为具体的服务代码（从其他库中引用的具体函数）
        print self.SrvName+u"服务已经停止："+ toolkits.TimetampToTimeStr(toolkits.getNowToTimestamp())
        conn = self.getConnection()
        strTable = "srvhostcontrolmgt"
        
        UpdateSql = GlobalVar.SqlStrTemplates["UpdateSql"]

        # if IsString(obj) :
            #lstemp = " '"+ obj+ "' "
        try:
            returnSrvInstID = self.getSrvStatus(self.SrvName,self.SrvMacAddress,"Running")# 确认是否有运行状态的
            if returnSrvInstID <>psrvInstID:
                self.SrvStop(returnSrvInstID) #用于递归遍历所有状态不是stop的服务

            UpdateSql = UpdateSql.replace("@{Table}",strTable)
            if len(psReason)>0 :
                psReason = "("+psReason+")"
            SetValuesStatement = "ServerStatus='Stop',Isactive = 0,SrvStartStopTime=UNIX_TIMESTAMP( ),Comments= CONCAT(now() , ':服务被停止' "+psReason+",'; ',ifnull(comments,'')) "
            UpdateSql = UpdateSql.replace("$[SetValuesStatement]",SetValuesStatement)
            UpdateSql = UpdateSql.replace("$[ClauseStatement]","ID ="+str(psrvInstID)+" and SrvName = '"+self.SrvName +"' and servermacadd = '"+self.SrvMacAddress +"' ")
            unOperation_ext = ["running","stop","suspended","crash","resume"]
            print UpdateSql
            #return InsertSql # 返回值 


            with conn:
                lcur = conn.cursor()
               
                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                self.SrvInstID = 0
                return returnSrvInstID
        except Exception, e:
            raise e

    def SrvCrash(self,psrvInstID,psReason=""):#用于继承，override 成为具体的服务代码（从其他库中引用的具体函数）
        print self.SrvName+u"服务已经崩溃："+ toolkits.TimetampToTimeStr(toolkits.getNowToTimestamp())
        conn = self.getConnection()
        strTable = "srvhostcontrolmgt"
        
        UpdateSql = GlobalVar.SqlStrTemplates["UpdateSql"]

        # if IsString(obj) :
            #lstemp = " '"+ obj+ "' "
        try:
            returnSrvInstID = self.getSrvStatus(self.SrvName,self.SrvMacAddress,"Running")# 确认是否有运行状态的
            if returnSrvInstID <>psrvInstID:
                self.SrvCrash(returnSrvInstID) #用于递归遍历所有状态不是stop的服务

            UpdateSql = UpdateSql.replace("@{Table}",strTable)
            if len(psReason)>0 :
                psReason = "("+psReason+")"
            SetValuesStatement = "ServerStatus='Stop',Isactive = 0,SrvStartStopTime=UNIX_TIMESTAMP( ),Comments= CONCAT(now() , ':服务被停止' "+psReason+",'; ',ifnull(comments,'')) "
            UpdateSql = UpdateSql.replace("$[SetValuesStatement]",SetValuesStatement)
            UpdateSql = UpdateSql.replace("$[ClauseStatement]","ID ="+str(psrvInstID)+" and SrvName = '"+self.SrvName +"' and servermacadd = '"+self.SrvMacAddress +"' ")
            unOperation_ext = ["running","stop","suspended","crash"]
            print UpdateSql
            #return InsertSql # 返回值 


            with conn:
                lcur = conn.cursor()
               
                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                self.SrvInstID = 0
                return returnSrvInstID
        except Exception, e:
            raise e    

    def SrvSuspend(self,psrvInstID):#用于继承，override 成为具体的服务代码（从其他库中引用的具体函数）
        print psrvName+"服务已经挂起："+toolkits.TimetampToTimeStr(toolkits.getNowToTimestamp())
        conn = self.getConnection()
        strTable = "srvhostcontrolmgt"
        
        UpdateSql = GlobalVar.SqlStrTemplates["UpdateSql"]

        # if IsString(obj) :
            #lstemp = " '"+ obj+ "' "
        try:
            returnSrvInstID = self.getSrvStatus(self.SrvName,self.SrvMacAddress,"Suspended")# 确认是否有挂起状态的
            if returnSrvInstID <>psrvInstID:
                self.SrvStop(psrvInstID) #发现有更新的suspend状态的服务,则返回最新的服务ID,同时关闭当前目标服务状态为Stop
                return returnSrvInstID

            UpdateSql = UpdateSql.replace("@{Table}",strTable)
            UpdateSql = UpdateSql.replace("$[SetValuesStatement]","ServerStatus='Suspended',Isactive = 1,LastSuccessHeartBeat =UNIX_TIMESTAMP( ),Comments= CONCAT(  now()  ,':服务被挂起'  ,'; ',ifnull(comments,'') )")
            UpdateSql = UpdateSql.replace("$[ClauseStatement]","ID ="+str(psrvInstID)+" and SrvName = '"+self.SrvName +"' and servermacadd = '"+self.SrvMacAddress +"' ")
            unOperation_ext = ["running","stop","suspended","crash","resume"]
            print UpdateSql
            #return InsertSql # 返回值 


            with conn:
                lcur = conn.cursor()
               
                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                self.SrvInstID = 0
                return returnSrvInstID
        except Exception, e:
            raise e
    
    def SrvResume(self,psrvInstID):#用于继承，override 成为具体的服务代码（从其他库中引用的具体函数）
        print psrvName+"服务已经开始恢复(结束挂起)："+toolkits.TimetampToTimeStr(toolkits.getNowToTimestamp())
        conn = self.getConnection()
        strTable = "srvhostcontrolmgt"
        
        UpdateSql = GlobalVar.SqlStrTemplates["UpdateSql"]

        # if IsString(obj) :
            #lstemp = " '"+ obj+ "' "
        try:
            returnSrvInstID = self.getSrvStatus(self.SrvName,self.SrvMacAddress,"Resume")# 确认是否有挂起状态的
            if returnSrvInstID <>psrvInstID:
                self.SrvStop(psrvInstID) #发现有更新的suspend状态的服务,则停止当前服务状态
                returnSrvInstID = self.SrvResume(returnSrvInstID) #发现有更新的suspend状态的服务,则恢复最新的服务状态到Running
                return returnSrvInstID 

            UpdateSql = UpdateSql.replace("@{Table}",strTable)
            UpdateSql = UpdateSql.replace("$[SetValuesStatement]","ServerStatus='Resume',Isactive = 1,LastSuccessHeartBeat =UNIX_TIMESTAMP( ),Comments= CONCAT(  now()  ,':服务被挂起后,重新恢复' ,'; ',ifnull(comments,'')) ")
            UpdateSql = UpdateSql.replace("$[ClauseStatement]","ID ="+str(psrvInstID)+" and SrvName = '"+self.SrvName +"' and servermacadd = '"+self.SrvMacAddress +"' ")
            unOperation_ext = ["running","stop","suspended","crash","resume"]
            print UpdateSql
            #return InsertSql # 返回值 


            with conn:
                lcur = conn.cursor()
               
                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                self.SrvInstID = 0
                return returnSrvInstID
        except Exception, e:
            raise e
               

    def getSrvStatus(self,psSrvName ,pssrvMacAdd ,pssrvStatus=""):#获得当前服务的状态，并更新最后一次成功获得心跳状态的时间
        conn = self.getConnection()
        
        getSrvStatusSql= "select id,SrvName,servermacadd,ServerStatus,Isactive,VersionID from srvhostcontrolmgt where SrvName = '"+psSrvName +"' and servermacadd = '"+pssrvMacAdd +"' "
        unOperation_ext = ["running","stop","suspended","crash"]
        if len(pssrvStatus)>0 :
            if pssrvStatus.lower() in unOperation_ext:
                getSrvStatusSql = getSrvStatusSql + " and lower(ServerStatus) = '"+pssrvStatus.lower() +"' "
        getSrvStatusSql = getSrvStatusSql + " order by id desc LIMIT 1"    
        try:
            with conn:
                lcur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
                sql = getSrvStatusSql
                returnCuros = lcur.execute(sql)                
                serNum = lcur.fetchone()
                #conn.close() #getConnection实现方法二 可close,方法一不用close
                if not serNum: return 0

                strSrvID = serNum["id"]
                strServerStatus = serNum["ServerStatus"]
                if len(pssrvStatus)>0 :
                    returnStr = strSrvID
                else :
                    returnStr = strServerStatus
                 
                return returnStr
        except Exception, e:
            raise e
        
    def getSrvHeartBeatVerify(self,psrvInstID):#获得当前服务的心跳状态，并更新最后一次成功获得心跳状态的时间
        conn = self.getConnection()
        strTable = "srvhostcontrolmgt"
        
        UpdateSql = GlobalVar.SqlStrTemplates["UpdateSql"]
        unOperation_ext =["stop","crash"] #["running","stop","suspended","crash"]

        getSrvStatusSql= "select id,SrvName,servermacadd,ServerStatus,Isactive,VersionID,TimeoutInterval,SrvStartTime,SrvStartStopTime from srvhostcontrolmgt where ID = "+str(psrvInstID)
        getSrvStatusSql = getSrvStatusSql + " order by id desc LIMIT 1" 
        
        UpdateSql = UpdateSql.replace("@{Table}",strTable)
        UpdateSql = UpdateSql.replace("$[SetValuesStatement]"," LastSuccessHeartBeat =UNIX_TIMESTAMP( )")
        UpdateSql = UpdateSql.replace("$[ClauseStatement]","ID ="+str(psrvInstID)+" and SrvName = '"+self.SrvName +"' and servermacadd = '"+self.SrvMacAddress +"' ")

           
        try:
            with conn:
                lcur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
                sql = getSrvStatusSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchone()
                #conn.close() #getConnection实现方法二 可close,方法一不用close
                if not serNum: return 0

                strSrvID = serNum["id"]

                if serNum["ServerStatus"] in unOperation_ext :
                    print "No active Service Instance."
                    return 0

                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                self.SrvInstID = strSrvID
                return strSrvID
        except Exception, e:
            raise e         

    def VerifySrvStatus(self,psrvInstID):#批量根据心跳时间判断更新服务状态
        #select   *,UNIX_TIMESTAMP(),unix_timestamp('2018-07-02 02:41:54'), from_unixtime(1530470874),unix_timestamp('2018-07-02 02:47:54')-unix_timestamp('2018-07-02 02:41:54')
        conn = self.getConnection()
        strTable = "srvhostcontrolmgt"
        
       
        unOperation_ext =["stop","crash"] #["running","stop","suspended","crash"]

        #getSrvStatusSql= "select id,SrvName,servermacadd,ServerStatus,Isactive,VersionID,TimeoutInterval,SrvStartTime,SrvStartStopTime,LastSuccessHeartBeat, unix_timestamp()- ifnull(LastSuccessHeartBeat,0) as DisconnectTime from srvhostcontrolmgt where ID = "+str(psrvInstID)
        #getSrvStatusSql = getSrvStatusSql + " order by id desc LIMIT 1" 
        #getSrvStatusSql ="select id,SrvName,servermacadd,ServerStatus,Isactive,VersionID,TimeoutInterval,SrvStartTime,SrvStartStopTime,LastSuccessHeartBeat, unix_timestamp()- ifnull(LastSuccessHeartBeat,0) as DisconnectTime  from srvhostcontrolmgt where (unix_timestamp()- ifnull(LastSuccessHeartBeat,0))>(TimeoutInterval*3)"
        
        UpdateSql = "update srvhostcontrolmgt set Isactive=0 ,ServerStatus = 'Stop' , Comments = CONCAT(now() , ':服务被停止(由于系统心跳更新时间过长)','; ',ifnull(comments,''))  where (unix_timestamp()- ifnull(LastSuccessHeartBeat,0))>(TimeoutInterval*3) and Isactive =1;;"
           
        try:
            with conn:
                lcur = conn.cursor()
                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                #conn.close() #getConnection实现方法二 可close,方法一不用close
                if not serNum: return 0
                     
        except Exception, e:
            raise e         

    #-------------------Service Instance------------启停状态操作信息更新 End------------

    #-------------------Service Instance Execution------------服务执行操作操作信息更新 Begin------------
    def getServerPerfmonInfo(): #获得当前服务器的性能信息
        '''
        info = psutil.virtual_memory()
        returnServerInfoDict["UsedMemory"]= u"内存使用(M):"+str(psutil.Process(os.getpid()).memory_info().rss/1024/1024) 
        returnServerInfoDict["TotalMemory"] = u"总内存(G)："+ str(info.total/1024/1024/1024)
        returnServerInfoDict["percentMemory"] = u'内存占比：'+str(info.percent)
        returnServerInfoDict["CpuNum"] = u'cpu个数：'+str(psutil.cpu_count())
        '''
        returnServerInfoDict = {}
        try:
            info = psutil.virtual_memory()
            returnServerInfoDict["UsedMemory"]= u"内存使用(M):"+str(psutil.Process(os.getpid()).memory_info().rss/1024/1024) 
            returnServerInfoDict["TotalMemory"] = u"总内存(G)："+ str(info.total/1024/1024/1024)
            returnServerInfoDict["percentMemory"] = u'内存占比：'+str(info.percent)
            returnServerInfoDict["CpuNum"] = u'cpu物理个数：'+str(psutil.cpu_count(logical=False))
            returnServerInfoDict["CpuTime"] = u'cpu用时信息：'+str(psutil.cpu_times())
            returnServerInfoDict["DiskUsage"] = u'磁盘利用率:'+str(psutil.disk_usage())
            return returnServerInfoDict
        except Exception,e:
            return e
        

    def setSrvLastExecStartTimestamp(self,piSrvID,piCurrentTimestamp = 0 ):#设置当前服务的最后一次正常开始执行时刻
        conn = self.getConnection()
        SrvInstExecDataSet ={"ID" : 0,
                                                                "SrvID " : 0,
                                                                "GroupID" : 0,
                                                                "SrvLastStartTime" : "UNIX_TIMESTAMP( )",           #时间戳-最后一次轮询服务进程启动时间
                                                                "SrvLastCloseTime":  0,                             #"UNIX_TIMESTAMP( )", #时间戳-最后一次轮询服务进程完成时间,
                                                                "SuccessFilesCount" : 0,                            #成功解析文件数量',
                                                                "FailureFilesCount": 0,                             #失败数量',
                                                                "RetryFilesCount": 0,                               #重试数量',
                                                                "ServerPerfmon": "",                                 #服务器当前性能数据dashboard',
                                                                "IsDeleted": 0,                                     #用于逻辑删除，并通过脚本进行批量删除',
                                                                "LastModifiedTime" : "UNIX_TIMESTAMP( )",
                                                                "Comments": ""                                      #备注',
                                                        }
        strTable = "srvruningstatus"
        strColumnsStatement  = ""
        strValuesStatement = ""
        OriStr = "@{Table}"
        InsertSql = GlobalVar.SqlStrTemplates["InsertSql"]
        InsertSql = InsertSql.replace(OriStr,strTable)
        UpdateSql = GlobalVar.SqlStrTemplates["UpdateSql"]
        
        

        # if IsString(obj) :
            #lstemp = " '"+ obj+ "' "
        try:
            SrvInstExecID = getSerNum(self.SrvInstExecSerNumTag)
            SrvInstExecDataSet["ID"] = SrvInstExecID
            SrvInstExecDataSet["Comments"] = " Comments= CONCAT(now(), ':服务被启动' ,  ) ,'; ',ifnull(comments,'')"
            if SrvInstExecDataSet["SrvID"] == 0 :
                SrvInstExecDataSet["SrvID"] = self.SrvInstID
            if piCurrentTimestamp>0 :
                SrvInstExecDataSet["SrvLastStartTime"] = piCurrentTimestamp

            Perfinfo = getServerPerfmonInfo() #获取服务器性能信息
            SrvInstExecDataSet["ServerPerfmon"] = str(Perfinfo)

            ParamKeylist  = SrvInstExecDataSet.keys()
            ParamValuelist = SrvInstExecDataSet.values()
            #for x in ParamKeylist:#轮询字典中的每个key，并对模板进行替换
                #strlabal = str(x) #根据传入的参数字典内容将sql模板中的对应项目进行替换
                #NewStr = NewStr+", "+str(strlabal)
            NewStr = ' , '.join(ParamKeylist)
            OriStr = '$[ColumnsStatement]'#在模板中需要动态替换的值，未来考虑产品化时在数据库中维护，并与模板名称绑定
            InsertSql = InsertSql.replace(OriStr,NewStr)

            NewStr =""
            for x in ParamValuelist:#轮询字典中的每个key，并对模板进行替换
                lstemp = str(x)
                if len(lstemp)==0:
                    lstemp = "null"
                elif lstemp not in ["now()","UNIX_TIMESTAMP( )","CURRENT_TIMESTAMP()"]:
                   if toolkits.IsString(x) :
                       lstemp = " '"+ str(x)+ "' "
                if len(NewStr) == 0 :
                    NewStr = lstemp
                else :
                    NewStr = NewStr+' , '+ lstemp
        
            OriStr = '$[ValuesStatement]'#在模板中需要动态替换的值，未来考虑产品化时在数据库中维护，并与模板名称绑定
            InsertSql = InsertSql.replace(OriStr,NewStr)


            with conn:
                lcur = conn.cursor()
                sql = InsertSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchone()
                #conn.close() #getConnection实现方法二 可close,方法一不用close
                #strSerNum = str(serNum[0])
                return SrvInstExecID
        except Exception, e:
            raise e
        pass

    def getSrvLastExecStartTimestamp(self,psrvInstID,piGroupid = 0):#设置当前服务的执行启动时间为最后一次正常执行完毕时间
        conn = self.getConnection()
        strTable = "srvruningstatus"
        
       
        getSrvStatusSql= "select id,SrvID,SrvLastStartTime,GroupID from "+strTable+" where IsDeleted=0 "

        if piGroupid>0 : #如果两个实例为一组,则由groupid和srvname来决定
           
            getSrvStatusSql = getSrvStatusSqlsrvid+"and srvid in (select id from srvhostcontrolmgt  where	srvname in	(select srvname from srvhostcontrolmgt where ID = "+str(psrvInstID)+") "+" and Groupid = "+str(piGroupid)+")"
            
            '''
                select * 
                from srvruningstatus
                where srvid in (select id from srvhostcontrolmgt  where	srvname in	(select srvname from srvhostcontrolmgt where id =9) and groupid = 1 )
            '''

        else :
            
            getSrvStatusSql = getSrvStatusSql + " and SrvID = "+str(psrvInstID)

        getSrvStatusSql = getSrvStatusSql + " order by id desc LIMIT 1" 
        #getSrvStatusSql ="select id,SrvName,servermacadd,ServerStatus,Isactive,VersionID,TimeoutInterval,SrvStartTime,SrvStartStopTime,LastSuccessHeartBeat, unix_timestamp()- ifnull(LastSuccessHeartBeat,0) as DisconnectTime  from srvhostcontrolmgt where (unix_timestamp()- ifnull(LastSuccessHeartBeat,0))>(TimeoutInterval*3)"
        
        #UpdateSql = "update srvhostcontrolmgt set Isactive=0 ,ServerStatus = 'Stop' , Comments = CONCAT(now() , ':服务被停止(由于系统心跳更新时间过长)','; ',ifnull(comments,''))  where (unix_timestamp()- ifnull(LastSuccessHeartBeat,0))>(TimeoutInterval*3) and Isactive =1;;"
           
        try:
            with conn:
                lcur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                #conn.close() #getConnection实现方法二 可close,方法一不用close
                if not serNum: return 0

                return serNum["SrvLastStartTime"]     
        except Exception, e:
            raise e

    def setSrvLastExecfailureTimestamp(self,psrvInstExecID,piCurrentTimestamp,piFailureFilesCount=0,piSuccessFilesCount=0,piRetryFilesCount=0):#设置当前服务最后一次的执行失败时间
        conn = self.getConnection()
        strTable = "srvruningstatus"
        
        UpdateSql = GlobalVar.SqlStrTemplates["UpdateSql"]

        # if IsString(obj) :
            #lstemp = " '"+ obj+ "' "
        try:
            UpdateSql = UpdateSql.replace("@{Table}",strTable)
            UpdateSql = UpdateSql.replace("$[SetValuesStatement]","RetryFilesCount="+str(piRetryFilesCount)+" ,SuccessFilesCount="+str(piSuccessFilesCount)+" ,FailureFilesCount="+str(piFailureFilesCount)+" , SrvLastCloseTime ="+str(piCurrentTimestamp)+" ,LastModifiedTime =UNIX_TIMESTAMP( ),Comments= CONCAT(  now()  ,':服务存在异常,服务中断'  ,'; ',ifnull(comments,'') )")
            UpdateSql = UpdateSql.replace("$[ClauseStatement]","ID ="+str(psrvInstExecID))
            
            print UpdateSql
            #return InsertSql # 返回值 


            with conn:
                lcur = conn.cursor()
               
                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                self.SrvInstID = 0
                return returnSrvInstID
        except Exception, e:
            raise e

    def getSrvLastExecfailureTimestamp(self,psrvInstID,groupid=0):#获得当前服务的执行失败时间为最后一次失败时间
        conn = self.getConnection()
        strTable = "srvruningstatus"
        getSrvStatusSql= "select id,SrvID,SrvLastStartTime,GroupID from "+strTable+" where IsDeleted=0 and failurefilescount>0 "
        if piGroupid>0 : #如果两个实例为一组,则由groupid和srvname来决定
            getSrvStatusSql = getSrvStatusSqlsrvid+"and srvid in (select id from srvhostcontrolmgt  where	srvname in	(select srvname from srvhostcontrolmgt where ID = "+str(psrvInstID)+") "+" and Groupid = "+str(piGroupid)+")"
            '''
                select * 
                from srvruningstatus
                where srvid in (select id from srvhostcontrolmgt  where	srvname in	(select srvname from srvhostcontrolmgt where id =9) and groupid = 1 )
            '''
        else :
            getSrvStatusSql = getSrvStatusSql + " and SrvID = "+str(psrvInstID)
        getSrvStatusSql = getSrvStatusSql + " order by id desc LIMIT 1" 
        #getSrvStatusSql ="select id,SrvName,servermacadd,ServerStatus,Isactive,VersionID,TimeoutInterval,SrvStartTime,SrvStartStopTime,LastSuccessHeartBeat, unix_timestamp()- ifnull(LastSuccessHeartBeat,0) as DisconnectTime  from srvhostcontrolmgt where (unix_timestamp()- ifnull(LastSuccessHeartBeat,0))>(TimeoutInterval*3)"
        #UpdateSql = "update srvhostcontrolmgt set Isactive=0 ,ServerStatus = 'Stop' , Comments = CONCAT(now() , ':服务被停止(由于系统心跳更新时间过长)','; ',ifnull(comments,''))  where (unix_timestamp()- ifnull(LastSuccessHeartBeat,0))>(TimeoutInterval*3) and Isactive =1;;"
           
        try:
            with conn:
                lcur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                #conn.close() #getConnection实现方法二 可close,方法一不用close
                if not serNum: return 0
                return serNum["SrvLastStartTime"]      #注意,由于失败的时候,需要到failure的文件夹下进行重新的试跑failure 问题,因此如果需要确定时间,则应该从上一次执行出错的批次时间进行failure文件夹中文档的处理,因此不是用SrvLastCloseTime
        except Exception, e:
            raise e

    def setSrvLastExecEndTimestamp(self,psrvInstExecID,piCurrentTimestamp,piSuccessFilesCount=0,piRetryFilesCount=0):#设置当前服务的执行结束时间为最后一次正常结束时间
        conn = self.getConnection()
        strTable = "srvruningstatus"
        
        UpdateSql = GlobalVar.SqlStrTemplates["UpdateSql"]

        # if IsString(obj) :
            #lstemp = " '"+ obj+ "' "
        try:
            UpdateSql = UpdateSql.replace("@{Table}",strTable)
            UpdateSql = UpdateSql.replace("$[SetValuesStatement]","RetryFilesCount="+str(piRetryFilesCount)+" ,SuccessFilesCount="+str(piSuccessFilesCount)+" ,FailureFilesCount=0 , SrvLastCloseTime ="+str(piCurrentTimestamp)+" ,LastModifiedTime =UNIX_TIMESTAMP( ),Comments= CONCAT(  now()  ,':服务正常执行完毕'  ,'; ',ifnull(comments,'') )")
            UpdateSql = UpdateSql.replace("$[ClauseStatement]","ID ="+str(psrvInstExecID))
            print UpdateSql
            #return InsertSql # 返回值 
            with conn:
                lcur = conn.cursor()
               
                sql = UpdateSql
                returnCuros = lcur.execute(sql)
                serNum = lcur.fetchall()
                self.SrvInstID = 0
                return returnSrvInstID
        except Exception, e:
            raise e
        
    def getSrvLastExecEndTimestamp(self,psrvInstID):#获得当前服务的最后一次结束时间
        pass
    #-------------------Service Instance Execution------------服务执行操作操作信息更新 End------------

    def SrvSericeMgt(self,psrvName,psaction,pstimer_interval=GlobalVar.ServiceConfig["SrvInterval"],pbRestartfromlastExecTime=True):#用于进行服务的轮询，每XX时间间隔执行一次，知道状态为stop
        try:
            print "服务启动于:"+TimetampToTimeStr(getNowToTimestamp())
 
            t=Timer(self.timer_interval,self.SrvStart(psrvName))

            t.start()
            while True:
                
                try:
                     # sleep for the remaining seconds of interval
                    time_remaining = pstimer_interval-time.time()%pstimer_interval
                    print("Sleeping until %s (%s seconds)..."%((time.ctime(time.time()+time_remaining)), time_remaining))
                    time.sleep(time_remaining)
                    print("Starting command.")

                    srvStatus = self.getSrvStatus(psrvName)
                    if srvStatus.lower() in ["stop","crash"] :
                        self.SrvStop(psrvName)
                        self.SrvInstID = 0
                        break
                        #更新服务停止时间

                    if srvStatus.lower() == "suspended" :
                        self.SrvInstID = self.SrvSuspend(psrvName)
                        print 'main service is suspended' 
                        continue
                    if srvStatus.lower() == "resume" :
                        self.SrvInstID = self.SrvStart(psrvName)
                        print 'main service is resuming'
                        continue 
                    else:
                        print 'main service is still running'
                        time.sleep(0.1)
                        if pbRestartfromlastExecTime:
                            lastsrvstart = self.getSrvLastExecStartTimestamp(self.SrvInstID)
                        CurrentTimestamp = int(time.time())#未来如果需要部署到多台分布式服务器，则需要换为数据库时间
                        srvInstExecID = setSrvLastExecStartTimestamp(self.SrvInstID,CurrentTimestamp)
                        #执行代码逻辑 
                        CurrentFinishTimestamp  =  int(time.time())#未来如果需要部署到多台分布式服务器，则需要换为数据库时间
                        self.setSrvLastExecEndTimestamp(srvInstExecID,CurrentFinishTimestamp)
                except Exception,e:
                    CurrentFailureTimestamp  =  int(time.time())#未来如果需要部署到多台分布式服务器，则需要换为数据库时间
                    if srvInstExecID>0 :
                        setSrvLastExecfailureTimestamp(srvInstExecID,CurrentFailureTimestamp)
                    
        except Exception,e:
            print str(e)
        finally :
            print "服务停止于:"+TimetampToTimeStr(getNowToTimestamp())

    def getDictCur(self, psSql="SELECT * FROM user"): #方法一返回游标
        #conn = pymysql.connect(psConnectStr, charset='utf8')
        conn = self.getConnection()
        try:
            with conn:
                lcur = conn.cursor(MySQLdb.cursors.DictCursor)
                sql = psSql
                returnCuros = lcur.execute(sql)
                u = lcur.fetchall()
                #conn.close() #getConnection实现方法二 可close,方法一不用close
                return u
        except Exception, e:
            raise e

    def getfildname(self,pcur):#方法一
        return [d[0].lower() for d in pcur.description]


    def getDictData(self,psSql="SELECT * FROM user"): #方法一
        '''
        返回一个sql查询中指定列所有记录的多键子段内容和值子段内容：返回结果集为一个列表，每个列表中的每一个元素为多维维数据集合，每个字段及其内容对饮该行数据形成字典的key和value
        
        '''
        cur = self.getDictCur(psSql)
        
        fieldnames = self.getfildname(cur)

        #fieldnames = [d[0].lower() for d in cur.description]
        while True:
            rows = cur.fetchmany()
            if not rows: return
            for row in rows:
                yield dict(zip(fieldnames, row))

    #def makedict(self, cursor, psDictname = "userinfo", psSql="SELECT * FROM user", pskeyColName="user_id", psValueColName="user_name"): # psDictname为“字典名称|Key对应数据库字段|字典Value对应数据库字段”
    def makedict(self, psDictInfo = "userinfo|user_id|user_name", psSql="SELECT * FROM user"): # 方法二psDictInfo中由“字典名称|Key对应数据库字段|字典Value对应数据库字段”
        '''
        返回一个sql查询中指定列所有记录的键子段内容和值子段内容：返回结果集为一个二维数据集合
        @psDictname 字典名称
        @pskeyColName Key对应数据库字段
        @psValueColName字典Value对应数据库字段 
        @psDictInfo= 合并参数“字典名称|Key对应数据库字段|字典Value对应数据库字段”
        
        '''
        #Dictname = psDictname
        #keyColName = pskeyColName
        #ValueColName = psValueColName
        paramlist =  psDictInfo.split("|")
        if len(paramlist) <3 :
            return "字典定义参数错误，未能正确定义自定名称、字典key值域或者字典value值域"

        Dictname =  paramlist[0]
        keyColName = paramlist[1]
        ValueColName = paramlist[2]
        conn = self.getConnection()


        try:
            with conn:
                # 获取连接上的字典cursor，注意获取的方法，
                # 每一个cursor其实都是cursor的子类
                cur = conn.cursor(MySQLdb.cursors.DictCursor)
                # 执行MySQL语句,这里获取id从begin 到 end 的数据
                cur.execute(psSql )
                # 获取数据方法
                rows = cur.fetchall()
                # 遍历数据（比上一个更直接一点）
                dict_temp = dict()
                dict_temp["dictname"] = Dictname
                
                # print rows
                for row in rows:
                    # 这里，可以使用键值对的方法，由键名字来获取数据
                    # print "%s %s" % (row["user_id"], row["user_name"])
                    # print "%s" % (row["user_id"])
                    #self.user_list.append(row["user_id"])
                    # print user_list
                    dict_temp[row[keyColName]]=row[ValueColName]
                return dict_temp
        except Exception, e:
            raise e


    #更新数据苦数据
    #说明：
#使用时直接调用saveAll方法，其他方法将被saveAll调用，你可以无视
#saveAll参数说明：
#   table 表名
#   datas 数据的数组 例 ：[{"key1":"value1","key2":"value2"},{"key1":"value1","key2":"value2"}] 建议数组大小不要超过一千。  一个大的列表，其中每一行是一个字典
#   searchKeys 用于确定唯一行的键的数组，如用户表的用户名，选课表的课程ID与学生ID等 例 ["user_id","class_id"]
#   ifIgnoreSearchKey 是否忽略searchKey 如果你的searchKeys 是自增长的ID 你肯定不希望插入的时候插入这个字段 "1"是，"0"否
#   ifNotUpdate 是否不做更新操作 如果这个设为 "0" ,datas中数据如果已在数据库中，将不会做更新操作
#getConnection 方法中的DB 是从配置文件中导入的配置字典，现在设定默认值


def saveAll(self,table,datas,searchKeys,ifIgnoreSearchKey,ifNotUpdate):
    print datas
    conn = self.getConnection()
    cursor = conn.cursor()
    where = []
    #转义数据,避免sql发生错误
    for data in datas:
        for key in data:
            data[key] = MySQLdb.escape_string(str(data[key]))
    for searchKey in searchKeys:
        searchKeyDatas = []
        for data in datas:
            searchKeyDatas.append(data[searchKey])
        searchKeyDatasString = "`"+searchKey+"` in ('"+"','".join(searchKeyDatas)+"')"
        where.append(searchKeyDatasString)
    whereString = " AND ".join(where)
    selectSql = "SELECT `"+"`,`".join(searchKeys)+"` from "+table+" WHERE " + whereString
    cursor.execute(selectSql)
    conn.commit()
    results = cursor.fetchall()
    updateData = []
    insertData = []
    existKey = []
    for result in results:
        keyValue = []
        for value in result:
            keyValue.append(str(value))
        existKey.append(",".join(keyValue))
    for data in datas:
        keyValue = []
        for key in searchKeys:
            keyValue.append(data[key])
        currentKey = ",".join(keyValue)
        if currentKey in existKey:
            updateData.append(data)
        else:
            insertData.append(data)
    if ifNotUpdate == "0":
        updateAll(updateData,table,searchKeys)
    insertAll(insertData,table,searchKeys,ifIgnoreSearchKey)
    conn.close()
    pass

def updateAll(self,datas,table,searchKeys):
    #同时更新多条数据
    if len(datas) == 0:
        return
    conn = self.getConnection()
    cursor = conn.cursor()
    sets = {}
    updateSql = "UPDATE `"+table+"` set "
    whereValues = []
    whereKey = "WHERE CONCAT(`"+"`,',',`".join(searchKeys)+"`) IN "
    for data in datas:
        whereValue = []
        for searchKey in searchKeys:
            whereValue.append(data[searchKey])
        whereValueString = ",".join(whereValue)
        whereValues.append(whereValueString)
        for key in data:
            if key in searchKeys:
                pass
            else:
                searchValue = []
                for searchKey in searchKeys:
                    searchValue.append(str(data[searchKey]))
                searchValueString = ",".join(searchValue)
                try:
                    sets[key][searchValueString] = data[key]
                except KeyError as e:
                    sets[key] = {}
                    sets[key][searchValueString] = data[key]
    searchKeysString = "(`"+"`,',',`".join(searchKeys)+"`)"
    whereValuesString = "('"+"','".join(whereValues)+"')"
    setStringArray = []
    for key1 in sets:
        setString = ""
        for key2 in sets[key1]:
            if setString == "":
                setString = "`"+key1+"` = CASE WHEN (CONCAT"+searchKeysString+"='"+key2+"') THEN '"+sets[key1][key2]+"'"
            else:
                setString = setString + " WHEN (CONCAT"+searchKeysString+"='"+key2+"') THEN '"+sets[key1][key2]+"'"
        setString += " END "
        setStringArray.append(setString)
    setStrings = ",".join(setStringArray)
    whereStrings = whereKey + whereValuesString
    updateSql += setStrings
    updateSql += whereStrings
    print updateSql
    try:
        cursor.execute(updateSql)
        result = cursor.fetchall()
    except Exception as e:
        print e.message
        print updateSql
    conn.commit()
    conn.close()

def insertAll(self,datas,table,searchKeys,ifIgnoreSearchKey):
    #多条数据同时添加
    if len(datas) == 0:
        return
    conn = self.getConnection()
    cursor = conn.cursor()
    keys=[]
    for key in datas[0]:
        if key not in searchKeys or ifIgnoreSearchKey!= "1":
            keys.append(key)
    insertSql = "INSERT INTO "+table+" (`"+"`,`".join(keys)+"`) VALUES "
    valueStrings = []
    for data in datas:
        value = []
        for key in keys:
            value.append(data[key])
        valueString = "('" + "','".join(value) + "')"
        valueStrings.append(valueString)
    insertSql += ",".join(valueStrings)
    print insertSql
    try:
        cursor.execute(insertSql)
        conn.commit()
        #conn.close()
    except Exception as e:
        print insertSql
        print e.message


if __name__ == '__main__':
    g_pc = toolkits.prpcrypt(GlobalVar.PublicKey)
    #g_pc = toolkits.prpcrypt("0123456789ABCDEF")      #初始化密钥
    #d = g_pc.encrypt(g_DB["pwd"])#加密
    #d = g_DB["pwd"]
    #print g_DB["pwd"]
    #print d
    #print g_pc.encrypt(GlobalVar.SendMailConfig["MailboxPWD"])
    GlobalVar.DBConfig["pwd"] = g_pc.decrypt(GlobalVar.DBConfig["pwd"]) #数据库访问解密
    GlobalVar.SendMailConfig["MailboxPWD"] = g_pc.decrypt(GlobalVar.SendMailConfig["MailboxPWD"]) #邮箱密码解密 
    try :
        lSrvControl = SrvControlBase("FWMonintorParserSrv") 
        ActiveID = lSrvControl.SrvStart(lSrvControl.SrvName,lSrvControl.SrvMacAddress) 
        print(lSrvControl.getSrvHeartBeatVerify(ActiveID))
        lSrvControl.SrvStop(lSrvControl.SrvInstID)  
        print(lSrvControl.getSrvHeartBeatVerify(ActiveID))
    except  Exception , e:
        print e
        
           