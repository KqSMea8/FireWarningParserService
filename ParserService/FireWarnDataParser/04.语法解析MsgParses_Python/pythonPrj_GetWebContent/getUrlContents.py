# -*- coding: utf-8 -*-
# @Author: leonliang
# @Date:   2018-04-08 09:33:09
# @Last Modified by:   leonliang
# @Last Modified time: 2018-04-08 18:24:20
#coding:utf-8
import urllib2
import os
import re
import sys
import urllib
import string
import BeautifulSoup #导入解析html源码模块
import xlwt #导入excel操作模块

#检查url地址  
def check_link(url):  
    try:  
          
        r = requests.get(url)  
        r.raise_for_status()  
        r.encoding = r.apparent_encoding  
        return r.text  
    except:  
        print('无法链接服务器！！！')  



row = 0
col = 0
style0 = xlwt.easyxf('font: name Times SimSun')
wb = xlwt.Workbook(encoding='utf-8')
ws = wb.add_sheet('Sheet1',cell_overwrite_ok=True)
for num in range(1,291):#页数控制
	url = "http://www.scholaracademy.org/tushu/admin_system_manage/tjgl/bookstatistics.asp?ToPage="+str(num) #循环ip地址
	header = {
	        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0",
	        "Referer":"http://www.scholaracademy.org/tushu/admin_system_manage/tjgl/bookstatistics.asp"
	    }
	req = urllib2.Request(url,data=None,headers=header)
	resContent = urllib2.urlopen(url).read()
	resContent = resContent.decode('gb18030').encode('utf8')
	soup = BeautifulSoup.BeautifulSoup(resContent)

	newv = str(soup)
	#trs = soup.findAll('tr')
	'''
	print trs[0] 
	for tr in trs:
		row = row + 1
		tds = tr.findAll('td')
		print(tds[0] )
    	for td in tds:
    		col = col +1
    		ws.write(row,col,td.string)  # 第几行，列1  列2...列n

    	col = 0
	'''
	res_tr = r'<tr>(.*?)</tr>'
	m_tr =  re.findall(res_tr,newv,re.S|re.M|re.X)
	print  '正在抓取'+str(num)+'页'
	#print(len(m_tr))
	#print(m_tr[5])
	for line in m_tr:
		row = row + 1
		#print line
		res_td = r'<td height="24" bgcolor="#F2F8FF">&nbsp;(.*?)</td>'
		m_td = re.findall(res_td,line,re.S|re.M)
		#print(m_td)
		#print(len(m_td))
		for nn in m_td:
			col = col +1
			ws.write(row,col,unicode(nn,'utf-8'))  # 第几行，列1  列2...列n#print unicode(nn,'utf-8')
		col = 0
	
wb.save('c:\\20180408.xls')

print '操作完成！'

