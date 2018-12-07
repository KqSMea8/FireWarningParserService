# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-06-21 17:37:47
# @Last Modified by:   leonliang
# @Last Modified time: 2018-06-22 11:10:57
import logging
from logging.handlers import RotatingFileHandler;
import os.path;

C_APP_NAME = "Service Moniter 1.0";
C_LOG_DIR = os.path.altsep.join([os.path.curdir,'service.log']);
C_CONFIG_PATH = os.path.altsep.join([os.path.curdir,'config.xml']);
C_LOG_SIZE = 1048576;
C_LOG_FILES = 3;

C_APP_SITE = "http://www.lenovohit.com";

#用字典保存日志级别
format_dict = {
   1 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
   2 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
   3 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
   4 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
   5 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
}

#开发日志系统， 既要把日志输出到控制台， 还要写入日志文件   
class Logger():
    def __init__(self, logname, loglevel, logger):
        '''
           指定保存日志的文件路径，日志级别，以及调用文件
           将日志存入到指定的文件中
        '''
        
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.DEBUG)
        
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        # 定义handler的输出格式
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = format_dict[int(loglevel)]
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def getlog(self):
        return self.logger


def InitLog():
    logging.getLogger().setLevel(logging.ERROR)
    RtHandler = RotatingFileHandler(filename=C_LOG_DIR,maxBytes=C_LOG_SIZE,backupCount=C_LOG_FILES)
    RtHandler.setLevel(logging.ERROR)
    RtHandler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    logging.getLogger().addHandler(RtHandler)
    logging.getLogger().addHandler(consoleHandler)
    logging.info('监控开始执行')
    return logging.getLogger()

InitLog()

