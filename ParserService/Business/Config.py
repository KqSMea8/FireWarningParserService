# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-03-26 15:16:42
# @Last Modified by:   leonliang
# @Last Modified time: 2018-03-28 11:28:48
import os
import re
import time

PublicKey = "0123456789ABCDEF"

FileMgtConfig = {   "Orifolder" : "D:\work\DataStore\Firewarning\Ori\\",#待处理原始文件夹
                    "Destfolder" : "D:\work\DataStore\Firewarning\Done\\",#已经处理后移动至目标文件夹
                    "DestZipfolder" : "D:\work\DataStore\Firewarning\Zip\\", #解压缩文件目标文件夹
                    "DestFailurefolder" : "D:\work\DataStore\Firewarning\Failure\\", #错误后重试目标文件夹
                    "SysLogsfolder" : "D:\work\DataStore\Firewarning\Logs\\",#系统日志主目录文件夹
                    "InstExecLogsfolder" : "D:\work\DataStore\Firewarning\Logs\Exec\\"#服务调用处理执行明细日志主目录文件夹
                }


DBConfig = {"host":"localhost",
      "port":"3306",
      "user":"warning",
      "pwd": "a93efaba3dc8806a64bf3985f7dfc71b",#"AAAA:1qazxsw@"
      "db":"warning",
      "charset":"utf8"
      }

''' #正式云服务器
DBConfig = {"host":"121.43.58.151",
      "port":"3306",
      "user":"warning",
      "pwd": "339a690c7e318484a6e53dce6f8004a6",#"AAAA:1qazxsw2"
      "db":"warning",
      "charset":"utf8"
      }
'''

SendSMSConfig = { "REGION" : "cn-hangzhou",
            "PRODUCT_NAME" : "Dysmsapi",
            "DOMAIN" : "dysmsapi.aliyuncs.com",
            "ACCESS_KEY_ID" : "LTAIfiRSUppU9kiO",
            "ACCESS_KEY_SECRET" : "suTc9XmYlV88BMXo1mDRJMxid2NYrB",
            "RecievePhonelist" : "18621119006,13778066793,1860027053"
            }

SendMailConfig ={   "MailboxUser" : "liangqihui@sina.com.cn",#发件人邮箱地址 
                    "MailboxPWD" :  "b0fbe5cbac5ab300d14a6511cb66703d",#发件人邮箱登录密码,'b0fbe5cbac5ab300d14a6511cb66703d'
                    "MailboxSMTPsrv" : 'smtp.sina.com'  #SMPT服务器
               }

ServiceConfig = {   "SrvInterval" : 5,
                    "TimeoutInterval" : 120
                }

SqlStrTemplates = { "InsertSql" : "insert into @{Table} ($[ColumnsStatement]) values ($[ValuesStatement]) ",
                    "UpdateSql" : "update @{Table} set $[SetValuesStatement] where 1=1 and ($[ClauseStatement])",
                    "DeleteSql" : "delete from @{Table}  where  1=1 and ($[ClauseStatement])",
                    "SelectSql" : "select ($[ColumnsStatement]) from @{Table} where 1=1 and ($[ClauseStatement])",
                    "SelectTopSql" : "select ($[ColumnsStatement]) from @{Table} where 1=1 and ($[ClauseStatement]) $[OrderbyStatement] limit $[topNum]"
                    
                }

