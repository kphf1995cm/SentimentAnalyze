#!/usr/bin/python
#-*- coding:UTF-8 -*-
def mye(level):
    if level<1:
        raise Exception("Invaild level!",level)

def genExcep():
    try:
        mye(0)
        print 3
    except "Invaild level!":
        print 1
    else:
        print 2

def ioExcp():
    try:
        f=open("test.txt",'r')
        print 2
    except IOError:
        print 'error, can not find the file'
    else:
        print 'success'
        f.close()

def tryFinalTest():
    try:
        f=open('test.txt','r')
        print 1
    finally:# 无论是否发生异常都会执行
        print 'error'

def testExcp():
    try:
        1 / 0
        print 2
    except Exception as e:
        '''异常的父类，可以捕获所有的异常'''
        print "0不能被除"
    else:
        '''保护不抛出异常的代码'''
        print "没有异常"
    finally:
        print "最后总是要执行我"

if __name__=='__main__':
    testExcp()