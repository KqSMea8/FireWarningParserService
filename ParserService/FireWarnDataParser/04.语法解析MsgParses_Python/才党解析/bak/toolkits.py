# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-03-27 22:42:42
# @Last Modified by:   leonliang
# @Last Modified time: 2018-03-28 05:38:20
import types
import re
import random 


""" 
验证所有表单提交的数据 
"""  
  
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
			retrunStr = b[i] + strSplit + returnStr
	return returnStr

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

''''' 
实际计算校验和时，解释为无符号整数还是带符号整数，结果必然是一样的。因为基于补码方式存储，计算加法时都是按位加，然后该进位的就进位。 
只是最终的结果，如果是带符号整数，最高位会被解释符号位 
'''  
  
def char_checksum(data, byteorder='little')   :
    ''''' 
    char_checksum 按字节计算校验和。每个字节被翻译为带符号整数 
    @param data: 字节串 
    @param byteorder: 大/小端 
    '''  
    length = len(data)  
    checksum = 0  
    for i in range(0, length):  
        x = int.from_bytes(data[i:i+1], byteorder, signed=True)  
        if x>0 and checksum >0:  
            checksum += x  
            if checksum > 0x7F: # 上溢出  
                checksum = (checksum&0x7F) - 0x80 # 取补码就是对应的负数值  
        elif x<0 and checksum <0:  
            checksum += x  
            if checksum < -0x80: # 下溢出  
                checksum &= 0x7F  
        else:  
            checksum +=x # 正负相加，不会溢出  
        #print(checksum)      
      
    return checksum  
      
  
def uchar_checksum(data, byteorder='little'):  
    ''''' 
    char_checksum 按字节计算校验和。每个字节被翻译为无符号整数 
    @param data: 字节串 
    @param byteorder: 大/小端 
    '''  
    length = len(data)  
    checksum = 0  
    for i in range(0, length):  
        checksum += int.from_bytes(data[i:i+1], byteorder, signed=False)  
        checksum &= 0xFF # 强制截断  
          
    return checksum  
  