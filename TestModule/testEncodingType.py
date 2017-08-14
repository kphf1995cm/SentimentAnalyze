
# -*- coding: utf-8 -*-
import chardet
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
print sys.getdefaultencoding()

file_name='C:/Users\kuangp@wangsu.com\Desktop/11111.txt'
def read_txt():
    f=open(file_name,'r')
    s=f.readlines()
    for x in s:
        print x,chardet.detect(x)
    f.close()

def write_txt_unicode():
    f = open(file_name, 'a')
    f.write(u'你好\n')
    f.close()

def write_txt_utf_8():
    f = open(file_name, 'a')
    f.write(u'你好\n'.encode('utf-8'))
    f.close()
def write_txt_gbk():
    f = open(file_name, 'a')
    f.write(u'你好\n'.encode('gbk'))
    f.close()

if __name__=='__main__':
    file_name = 'D:/crambData\crambData4/output3.txt'
    read_txt()