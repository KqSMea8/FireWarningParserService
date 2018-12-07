#!/usr/bin/env python
# -*- coding=utf-8 -*-
import struct

#0D 10 12 34 56 78 90 12 01 00 00 00 09 01 01 00 00 00 00 00 00 00 D2 FF
def packageUpStream(): # eventType,PhoneNum,DeviceID,InfoFlag,MachineNo,Warning):
    #上行消息格式：24字节
    #起始符(1)+事件类型(1)+电话号码(6)+收发器ID(4)+信息标识(1)+机号(1)+报警信息(8) +校验和(1)+结束符(1)                                       
    packMsgData = struct.pack('8B2H12B',0xd,0x10,12,34,56,0xAA,0xAA,0xAA,0x0100,0x0000,0x09,0x02,0x03,0,0,0,0,0,0,0x0,0xB9,0xff)
    binfile=open('/home/steven/Desktop/upMsg_sample.dat','wb')
    binfile.write(packMsgData)
    binfile.close()

def packageUpStreamGB():
    #@@
    packMsgData = struct.pack('2B2H6B6B6BHB2B4B6B3B',64,64,0x0001,0x0201,20,25,13,24,11,17,0x00,0x50,0x56,0xc0,0x00,0x01,0x00,0x50,0x56,0xc0,0x00,0x08,0xC,0x2,0x1,0x1,116,101,115,116,10,11,15,24,11,17,0x55,35,35)
    binfile=open('/home/steven/Desktop/GBupMsg_sample.dat','wb')
    binfile.write(packMsgData)
    binfile.close()


if __name__ == '__main__':
    packageUpStream()
    packageUpStreamGB()