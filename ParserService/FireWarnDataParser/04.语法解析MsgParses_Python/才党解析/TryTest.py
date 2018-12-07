# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-03-28 10:38:45
# @Last Modified by:   leonliang
# @Last Modified time: 2018-03-28 12:26:02

import toolkits
from GBMsgDataDefine import *
'''
teststr = getPackageValueByDef("4040710101013B0D0D1A03120100000000000000000000013000020201010B28010101230800000000000000000000000000000000000000000000000000000000000000003B0F0D1A03120D2323","6|12")
print(teststr)
teststr = ParserTimeStr(teststr)
print(teststr)
'''
tempstr = "4040710101013B0D0D1A03120100000000000000000000013000020201010B28010101230800000000000000000000000000000000000000000000000000000000000000003B0F0D1A03120D2323"
#print(str_checksum(tempstr,'0D'))
#print(get_chechsumdata(tempstr))
toolkits.IsNumber
print(ParserGBMsgByJsonDef(tempstr))


#print(getTextDefExcutedResult("commend:1+1=2"))

