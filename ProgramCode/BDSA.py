#! /usr/bin/env python2.7
#coding=utf-8

"""
using PyQt4 package

author: Kuang Peng
last edited: August 2017
"""

import os
import sys

from PyQt4.QtGui import QTextCursor

import predictDataPosNegProbility as pdpnp
import selectBestClassifier as sbc
import sentimentAnalyzeBasedDict as sabd
import textProcessing as tp
import unlabelDataProcessToLabel as udptl
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import QString
import basicParmSetDialog
import dynamicParmSetDialog
import dyLineParmSetDialog
import time
import random
import xlrd
import math

class SA(QtGui.QMainWindow):

    def __init__(self):
        super(SA,self).__init__()
        self.initUI()
    # 查看分类结果
    def viewClsResDialog(self):
        self.clearScreenInfo()
        srcPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                    'D:/ReviewHelpfulnessPrediction/PredictClassRes/')
        fileDir,fileName,fileType=self.parseFilePath(str(srcPath))
        if fileType==".txt":
            showData=tp.get_txt_str_data(srcPath,'lines')
            self.textOutput.setText(showData)
        elif fileType==".xls":
            showData=''
            table = xlrd.open_workbook(srcPath)
            sheet = table.sheets()[0]
            rows=sheet.nrows
            for rowPos in range(rows):
                #print ' '.join(sheet.row_values(rowPos)),type(' '.join(sheet.row_values(rowPos)))
                showData+=((' '.join(sheet.row_values(rowPos)))+'\n'.decode('utf-8'))
            self.textOutput.setText(showData)
    #查看含不良内容弹幕数据
    def viewStrangeWordsDialog(self):
        self.clearScreenInfo()
        srcPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                    'D:/ReviewHelpfulnessPrediction/StrangeWords/')
        showData = tp.get_txt_str_data(srcPath, 'lines')
        self.textOutput.setText(showData)
    #查看情感波动曲线图
    def viewFigDialog(self):
        self.clearScreenInfo()
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                  'D:/ReviewHelpfulnessPrediction/SentimentLineFig/')
        pixmap = QtGui.QPixmap(fname)
        self.pngOutput.setPixmap(pixmap)

    #过滤客观语句
    def filtDataDialog(self):
        srcPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                  'D:/crambData/')
        fileDir, fileName, fileType = self.parseFilePath(str(srcPath))
        dstDir='D:/ReviewHelpfulnessPrediction/BulletData/'
        dstPath=dstDir+fileName+'.txt'
        udptl.filt_objective_sentence(srcPath,'lines',dstPath)
        self.clearScreenInfo()
        self.statusMessage.setText(u'过滤后数据保存在：'+dstPath)
    #删除重复语句
    def removeDupDataDialog(self):
        srcPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                    'D:/ReviewHelpfulnessPrediction/BulletData/')
        fileDir,fileName,fileType=self.parseFilePath(str(srcPath))
        dstDir = 'D:/ReviewHelpfulnessPrediction/LabelingData/'
        dstPath = dstDir + fileName + '.xls'
        #udptl.filt_objective_sentence(srcPath, 'lines', dstPath)
        self.clearScreenInfo()
        if os.path.exists(dstPath)==False:
            udptl.remove_duplicate_comment(srcPath,'lines',dstPath)
            self.statusMessage.setText(u'去重后数据保存在：' + dstPath)
        else:
            self.statusMessage.setText(dstPath+u'该文件已存在')
    #txt转excel 转换为规范标注形式
    def saveTxtToExcelDialog(self):
        srcPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                    'D:/crambData/')
        fileDir, fileName, fileType = self.parseFilePath(str(srcPath))
        dstDir = 'D:/ReviewHelpfulnessPrediction/LabelingData/'
        dstPath = dstDir + fileName + '.xls'
        self.clearScreenInfo()
        if os.path.exists(dstPath) == False:
            udptl.change_txt_to_excel(srcPath,'lines',dstPath)
            self.statusMessage.setText(u'转化后数据保存在：'+dstPath)
        else:
            self.statusMessage.setText(dstPath+u'该文件已存在')
    #保存标注数据和关键字
    def saveLabelAndKeyWordToSpeNameDialog(self):
        srcPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                    'D:/ReviewHelpfulnessPrediction/LabelingData/')
        fileDir,fileName,fileType=self.parseFilePath(str(srcPath))
        dstDir = 'D:/ReviewHelpfulnessPrediction/SpeNameLabeledData/'
        keyWordDir='D:/ReviewHelpfulnessPrediction/KeyWords/'
        errorRow=udptl.extract_keyword_from_spe_name_labeldata(srcPath,dstDir,keyWordDir,fileName)
        f=open('D:/ReviewHelpfulnessPrediction/LabelDataID.txt','a')
        f.write(fileName+'\n')
        f.close()
        self.clearScreenInfo()
        self.statusMessage.setText(u'标记数据保存目录：' + dstDir+' '+fileName)
        errorStr=''
        for x in errorRow:
            for y in x:
                errorStr+=str(y)+' '
            errorStr+='\n'
        self.textOutput.setText(errorStr)
    #合并标注数据
    def unionLabelData(self):
        sheetNameList = [['subjective_data', 'objective_data'], ['postive_data', 'negtive_data'],
                         ['erotic_data', 'normal_data']]
        speNameLabelDataDir='D:/ReviewHelpfulnessPrediction/SpeNameLabeledData'
        labeledDataDir='D:/ReviewHelpfulnessPrediction/LabelReviewData'
        keyWordDir='D:/ReviewHelpfulnessPrediction/KeyWords'
        labelDataIdList=tp.get_txt_data('D:/ReviewHelpfulnessPrediction/LabelDataID.txt','lines')
        nameSet=set([])
        for x in labelDataIdList:
            nameSet.add(x)
        nameStr=''
        f=open('D:/ReviewHelpfulnessPrediction/LabelDataID.txt','w')
        for x in nameSet:
            f.write(x+'\n')
            nameStr+=str(x)
            nameStr+='\n'
        f.close()
        posNegDataNum=udptl.unionFewLabelData(speNameLabelDataDir,nameSet,labeledDataDir)
        udptl.unionKeyWords(keyWordDir,nameSet)
        self.clearScreenInfo()
        self.textOutput.setText(nameStr)
        self.statusMessage.setText(u'主观数据个数：'+str(posNegDataNum[0]).decode('utf-8')+u' 客观数据个数：'+str(posNegDataNum[1]).decode('utf-8')+'\n'.decode('utf-8')+
                                   u'积极数据个数：' + str(posNegDataNum[2]).decode('utf-8') + u' 消极数据个数：' + str(
            posNegDataNum[3]).decode('utf-8') + '\n'.decode('utf-8') +u'不良数据个数：'+str(posNegDataNum[4]).decode('utf-8')+u' 正常数据个数：'+str(posNegDataNum[5]).decode('utf-8')+'\n'.decode('utf-8')+
            u'关键词所在目录：'+keyWordDir+'\n'+u'合并后标记数据所在目录：'+labeledDataDir)
    #解析文件路径 提取文件目录 文件名 文件类型
    def parseFilePath(self,path):
        strs=path.split('/')
        nameType=strs[len(strs)-1].split('.')
        strs.pop(len(strs)-1)
        fileDir='/'.join(strs)
        fileName=nameType[0]
        fileType='.'+nameType[1]
        return fileDir,fileName,fileType
    #更改原始数据路径
    def changeRawPathDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                  'D:/crambData/')
        rawData=tp.get_txt_str_data(fname,'lines')
        self.rawDataPath=fname
        self.statusMessage.setText(u'原始数据路径更改为：'+fname)
        self.textOutput.setText(rawData)
    #更改标记（训练）数据路径
    def changeLabelDataPathDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                  'D:/ReviewHelpfulnessPrediction/LabelReviewData')
        f=open('D:/ReviewHelpfulnessPrediction/LabelDataPath.txt','w')
        f.write(str(fname))
        f.close()
        self.statusMessage.setText(u'标记数据路径更改为：'+fname)
    #提取文件名中时间
    def extractFileNameTime(self,fileName):
        name=fileName.split('-')
        if len(name)>2:
            return name[1]
        else:
            return ''
    #清空屏幕信息
    def clearScreenInfo(self):
        self.textOutput.setText('')
        self.pngOutput.setText('')
        self.statusMessage.setText('')
        emptyPng = QtGui.QPixmap("")
        self.pngOutput.setPixmap(emptyPng)
        self.workMode=-1
        if self.timer.isActive():
            self.timer.stop()
    #删除文件
    def removeFile(self,filePath):
        if os.path.exists(filePath):
            os.remove(filePath)
    #删除过去带有时间的结果数据
    def removePastDataDialog(self):
        curTime = time.strftime('%Y.%m.%d.%H.%M.%S', time.localtime(time.time()))
        clfResDir = 'D:/ReviewHelpfulnessPrediction\PredictClassRes'
        figDir = 'D:/ReviewHelpfulnessPrediction\SentimentLineFig'
        strangeWordDir = 'D:/ReviewHelpfulnessPrediction\StrangeWords'
        fileDirPathList=[clfResDir,figDir,strangeWordDir]
        removedFileName=''
        for fileDirPath in fileDirPathList:
            fileDir=os.listdir(fileDirPath)
            for file in fileDir:
                name=self.extractFileNameTime(file)
                if name:
                    self.removeFile(fileDirPath+'/'+file)
                    removedFileName+=(fileDirPath+'/'+file+'\n').decode('utf-8')
        self.clearScreenInfo()
        self.textOutput.setText(removedFileName)
    #删除过去所有结果数据
    def clearPastAllDataDialog(self):
        clfResDir = 'D:/ReviewHelpfulnessPrediction\PredictClassRes'
        figDir = 'D:/ReviewHelpfulnessPrediction\SentimentLineFig'
        strangeWordDir = 'D:/ReviewHelpfulnessPrediction\StrangeWords'
        fileDirPathList = [clfResDir, figDir, strangeWordDir]
        removedFileName = ''
        for fileDirPath in fileDirPathList:
            fileDir = os.listdir(fileDirPath)
            for file in fileDir:
                self.removeFile(fileDirPath + '/' + file)
                removedFileName += (fileDirPath + '/' + file + '\n').decode('utf-8')
        self.clearScreenInfo()
        self.textOutput.setText(removedFileName)
    #运行过程中修改参数
    def modifyParmDialog(self):
        windowSize, sentBounder, posBounder, negBounder, timeSize, messageNum, drawSpeed, ok = dyLineParmSetDialog.getParmValue()
        if ok:
            #self.workMode = 3
            ms = drawSpeed  # 隔多少ms画一次图
            if ms > 1000:
                ms = 1000
            # if self.timer.isActive() == False:
            #     self.timer.start(ms, self)
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            self.timeSize = timeSize * 1000 / ms
            #print self.timeSize,self.timeRun
            self.dyLineShowWidth = messageNum
            if self.timer.isActive() == False:
                self.timer.start(ms, self)
            else:
                self.timer.stop()
                self.timer.start(ms, self)
    #每隔一定时间激发一次
    def timerEvent(self,e):
        if self.timeRun>=self.timeSize:
            self.timeRun=0
            if self.workMode==1:
                self.showCurCrabStaticPngML()
            elif self.workMode==2:
                self.showAllCrabStaticPngML()
            elif self.workMode==3:
                self.analyzeRawDataML()
            elif self.workMode==8:
                self.analyzeCurShowAllStaticPngML()
            elif self.workMode==5:
                self.showCurCrabStaticPngDA()
            elif self.workMode==6:
                self.showAllCrabStaticPngDA()
            elif self.workMode==7:
                self.analyzeRawDataDA()
            elif self.workMode==9:
                self.analyzeCurShowAllStaticPngDA()
            return
        if self.workMode==-1 or self.workMode==0 or self.workMode==4:
            self.progressBar.setValue(0)
        else:
            self.timeRun += 1
            # print self.timeRun
            if self.workMode == 3 or self.workMode == 7:
                # self.showDySentLineML()
                self.update()
            self.progressBar.setValue(self.timeRun * 100 / self.timeSize)
    #窗口更新时候激发
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.workMode==3 or self.workMode==7:
            self.showDySentLineML(qp)
        qp.end()
    # 相邻刻度值之间距离确定 刻度数量动态适应屏幕大小 可能刻度值位置不准确
    def drawLine2(self, qp, sw, sh, w, h, showData):
        middleW = sw + w / 2
        middleH = sh + h / 2
        qp.drawLine(sw, sh + h, sw + w, sh + h)  # x
        qp.drawLine(sw, sh, sw, sh + h)
        qp.drawLine(sw, sh, sw + w, sh)
        qp.drawLine(sw + w, sh, sw + w, sh + h)

        qp.drawLine(sw, middleH, sw + 5, middleH)
        qp.drawLine(sw, sh + h / 4, sw + 5, sh + h / 4)
        qp.drawLine(sw, sh + 3 * h / 4, sw + 5, sh + 3 * h / 4)

        qp.drawLine(middleW, sh + h - 5, middleW, sh + h)
        qp.drawLine(sw + w / 4, sh + h - 5, sw + w / 4, sh + h)
        qp.drawLine(sw + 3 * w / 4, sh + h - 5, sw + 3 * w / 4, sh + h)
        qp.setPen(QtCore.Qt.blue)
        x = range(1, len(showData) + 1)
        if self.sentBounder < 0:
            minSent = -self.sentBounder
        else:
            minSent = self.sentBounder
        heightRange = int((minSent + 10) * 2)
        widthRange = int(self.dyLineShowWidth)
        showAxisWidth = 50
        xAxisNum = w / showAxisWidth
        yAxisNum = h / showAxisWidth
        if xAxisNum != 0 and yAxisNum != 0:
            xValueInterval = widthRange / xAxisNum
            yValueInterval = heightRange / yAxisNum
            xPosInterval = w / xAxisNum
            yPosInterval = h / yAxisNum
        else:
            xValueInterval = widthRange
            yValueInterval = heightRange
            xPosInterval = w
            yPosInterval = h
        xTextWidth = 5
        xTextHeight = 8
        xTextPos = sw
        xTextValue = 0
        # QPainter.drawText(QRect, int, QString) -> QRect
        # 绘制x轴刻度
        while xTextPos <= sw + w:
            rect = QtCore.QRect(xTextPos, sh + h + 2, xTextPos + xTextWidth, sh + h + 2 + xTextHeight)
            qp.drawText(rect, 0, QString(str(xTextValue)))
            xTextValue += xValueInterval
            xTextPos += xPosInterval
        yTextWidth = 5
        yTextHeight = 8
        yTextPos = sh + h
        yTextValue = -heightRange / 2
        # 绘制y轴刻度
        while yTextPos >= sh:
            rect = QtCore.QRect(sw - yTextWidth - 12, yTextPos - yTextHeight, sw - 12, yTextPos)
            qp.drawText(rect, 0, QString(str(yTextValue)))
            yTextValue += yValueInterval
            yTextPos -= yPosInterval

        xStd = []
        yStd = []
        for pos in range(len(showData)):
            xStd.append(sw + x[pos] * w / widthRange)
            yStd.append(middleH - showData[pos] * h / heightRange)
        for pos in range(1, len(x)):
            qp.drawLine(xStd[pos - 1], yStd[pos - 1], xStd[pos], yStd[pos])
            # qp.drawPoint(sw+x[pos]*w/widthRange,middleH-showData[pos]*h/heightRange)
    # 相邻刻度值大小确定
    def drawLine(self, qp, sw, sh, w, h, showData):
        middleW = sw + w / 2
        middleH = sh + h / 2
        qp.drawLine(sw, sh + h, sw + w, sh + h)  # x
        qp.drawLine(sw, sh, sw, sh + h)
        qp.drawLine(sw, sh, sw + w, sh)
        qp.drawLine(sw + w, sh, sw + w, sh + h)

        qp.drawLine(sw, middleH, sw + 5, middleH)
        # qp.drawLine(sw, sh+h/4, sw + 5, sh+h/4)
        # qp.drawLine(sw, sh+3*h/4, sw + 5, sh+3*h/4)

        qp.drawLine(middleW, sh + h - 5, middleW, sh + h)
        # qp.drawLine(sw+w/4, sh + h - 5, sw+w/4, sh + h)
        # qp.drawLine(sw+3*w/4, sh + h - 5, sw+3*w/4, sh + h)

        qp.setPen(QtCore.Qt.blue)
        x = range(1, len(showData) + 1)
        if self.sentBounder < 0:
            minSent = -self.sentBounder
        else:
            minSent = self.sentBounder
        if self.windowSize>minSent+10:
            minHeight=minSent+10
        else:
            minHeight=self.windowSize
        heightRange = int(minHeight * 2)
        widthRange = int(self.dyLineShowWidth)
        #print heightRange, widthRange,
        textWidth = 6
        textHeight = 8

        fiveHeight = 5 * h / float(heightRange)
        fiveHeightStartValue = -math.floor(heightRange / 2 / 5)
        #print fiveHeightStartValue,
        fiveHeightStartPos = middleH - fiveHeightStartValue * fiveHeight
        while fiveHeightStartPos > sh:
            rect = QtCore.QRect(sw - textWidth - 12, fiveHeightStartPos - textHeight / 2, sw,
                                fiveHeightStartPos + textHeight / 2)
            qp.drawText(rect, 0, QString(str(int(fiveHeightStartValue * 5))))
            fiveHeightStartPos -= fiveHeight
            fiveHeightStartValue += 1
            # qp.drawLine(sw-5,fiveHeightStartPos,sw,fiveHeightStartPos)

        twentyWidth = 20 * w / float(widthRange)
        twentyWidthStartValue = math.floor(widthRange / 2 / 20)
        #print twentyWidthStartValue
        twentyWidthStartPos = middleW - twentyWidthStartValue * twentyWidth
        twentyWidthStartValue = (widthRange / 2 - twentyWidthStartValue * 20) / float(20)
        while twentyWidthStartPos < sw + w:
            rect = QtCore.QRect(twentyWidthStartPos - textWidth / 2, sh + h, twentyWidthStartPos + textWidth / 2,
                                sh + h + textHeight)
            qp.drawText(rect, 0, QString(str(int(twentyWidthStartValue * 20))))
            twentyWidthStartPos += twentyWidth
            twentyWidthStartValue += 1
            # qp.drawLine(twentyWidthStartPos,sh+h,twentyWidthStartPos,sh+h+5)

        xStd = []
        yStd = []
        for pos in range(len(showData)):
            xStd.append(sw + x[pos] * w / widthRange)
            yStd.append(middleH - showData[pos] * h / heightRange)
        for pos in range(1, len(x)):
            qp.drawLine(xStd[pos - 1], yStd[pos - 1], xStd[pos], yStd[pos])
            # qp.drawPoint(sw+x[pos]*w/widthRange,middleH-showData[pos]*h/heightRange)
    # 绘制情感波动曲线 应用于绘制动图
    def showDySentLineML(self, qp):
        if self.dataEndPos - self.lastDrawPos <= self.dyLineShowWidth:
            showData = self.sentValueList[self.lastDrawPos:self.dataEndPos]
        else:
            showData = self.sentValueList[self.lastDrawPos:self.lastDrawPos + self.dyLineShowWidth]
            self.lastDrawPos += 1
        # print showData
        qp.setPen(QtCore.Qt.black)
        textRect = self.textOutput.rect()
        pngRect = self.pngOutput.rect()
        sw = textRect.width()
        showRect = pngRect
        self.drawLine(qp, sw + 35, 0 + 40, showRect.width() - 30, showRect.height() - 25, showData)

    # workMode 0-3 8机器学习方法
    #选择效果最佳分类器
    def selectBestClfDialog(self):
        message,clfNameAcc=sbc.handleSelectClfWork()
        processResStr=''
        for x in clfNameAcc:
            processResStr+=(x+'\n')
        self.clearScreenInfo()
        self.textOutput.setText(processResStr)
        self.statusMessage.setText(message)
    def selectBestClfTenFoldDialog(self):
        message,clfNameAcc=sbc.handleSelectClfWorkTenFold()
        processResStr=''
        for x in clfNameAcc:
            processResStr+=(x+'\n')
        self.clearScreenInfo()
        self.textOutput.setText(processResStr)
        self.statusMessage.setText(message)

    #显示当前抓取数据的情感曲线、append新的不良内容（需要使用到上次得到的posProbility的最后面windowSize-1个）
    def showCurCrabStaticPngML(self):
        self.lastPos, self.oldPosProbility, self.oldRawReview, curTime, strangeFlag,strangeWords, sentLinePath, clfResPath = pdpnp.sentiAnalyzeBaseUIMLFromLastPos(
            self.oldPosProbility, self.oldRawReview, self.lastPos, self.fileDir, self.fileName, self.fileType,
            self.windowSize, self.posBounder, self.negBounder,
            self.sentBounder)
        strangeTimeDir='D:/ReviewHelpfulnessPrediction/StrangeTimes/'
        strangeTimePath=strangeTimeDir+self.fileName+'.txt'
        if os.path.exists(strangeTimePath)==True:
            strangeTimeSet=tp.get_txt_data(strangeTimePath,'lines')
        else:
            strangeTimeSet=[]
        if strangeWords:
            # self.textOutput.setText(strangeWords)
            # self.textOutput.moveCursor(QTextCursor.End,QTextCursor.MoveAnchor)
            self.textOutput.append(str(curTime).decode('utf-8')+'\n'.decode('utf-8')+strangeWords)
        if os.path.exists(sentLinePath) == True:
            sentLinePng = QtGui.QPixmap(sentLinePath)
            self.pngOutput.setPixmap(sentLinePng)
        else:
            self.pngOutput.setText(u'没有新的弹幕消息')
        strangeTimeStr = ''
        f=open(strangeTimePath,'w')
        for x in strangeTimeSet:
            strangeTimeStr += (x + '\n')
            f.write(x+'\n')
        f.close()
        self.statusMessage.setText(
            u'主播房间号:' + self.fileName + '\n' + u'时间段:\n' + strangeTimeStr + '\n' + u'分类结果所在路径:' + clfResPath)
    #预测当前抓取数据情感倾向 计算全部数据的情感得分 显示全部数据的情感曲线（需要使用到之前得到的posProbility）
    def showAllCrabStaticPngML(self):
        self.lastPos, self.oldPosProbility, self.oldRawReview, curTime, strangeWordPath, sentLinePath, clfResPath = pdpnp.sentiAnalyzeBaseUIMLFromPosAll(
            self.oldPosProbility, self.oldRawReview, self.lastPos, self.fileDir, self.fileName, self.fileType,
            self.windowSize, self.posBounder, self.negBounder,
            self.sentBounder)
        strangeTimeDir = 'D:/ReviewHelpfulnessPrediction/StrangeTimes/'
        strangeTimePath = strangeTimeDir + self.fileName + '.txt'
        if os.path.exists(strangeTimePath) == True:
            strangeTimeSet = tp.get_txt_data(strangeTimePath, 'lines')
        else:
            strangeTimeSet = []
        if os.path.exists(strangeWordPath) == True:
            curStrangeWordNum=tp.get_txt_data(strangeWordPath,'line')
            if curStrangeWordNum>self.lastStrangeWordNum:
                self.lastStrangeWordNum=curStrangeWordNum
                strangeTimeSet.append(curTime)
            strangeWords = tp.get_txt_str_data(strangeWordPath, 'lines')
            self.textOutput.setText(strangeWords)
            self.textOutput.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        else:
            self.textOutput.setText(u'未发现不良内容')
        if os.path.exists(sentLinePath) == True:
            sentLinePng = QtGui.QPixmap(sentLinePath)
            self.pngOutput.setPixmap(sentLinePng)
        else:
            self.pngOutput.setText(u'窗口设置过大或抓取消息数过少')
        strangeTimeStr = ''
        f = open(strangeTimePath, 'w')
        for x in strangeTimeSet:
            strangeTimeStr += (x + '\n')
            f.write(x + '\n')
        f.close()
        self.statusMessage.setText(
            u'主播房间号:' + self.fileName + '\n' + u'时间段:\n' + strangeTimeStr + '\n' + u'分类结果所在路径:' + clfResPath)
    #预测分析当前展示全部静态图（需要使用到上次得到的posProbility的最后面windowSize-1个、需要之前全部的sentValueList）
    def analyzeCurShowAllStaticPngML(self):
        self.lastPos, self.sentValueList,self.oldPosProbility, self.oldRawReview, curTime, strangeFlag,strangeWords, sentLinePath, clfResPath = pdpnp.sentiAnalyzeBaseUIMLFromLastPosShowALl(
            self.sentValueList,self.oldPosProbility, self.oldRawReview, self.lastPos, self.fileDir, self.fileName, self.fileType,
            self.windowSize, self.posBounder, self.negBounder,
            self.sentBounder)
        strangeTimeDir='D:/ReviewHelpfulnessPrediction/StrangeTimes/'
        strangeTimePath=strangeTimeDir+self.fileName+'.txt'
        if os.path.exists(strangeTimePath)==True:
            strangeTimeSet=tp.get_txt_data(strangeTimePath,'lines')
        else:
            strangeTimeSet=[]
        if strangeWords:
            # self.textOutput.setText(strangeWords)
            # self.textOutput.moveCursor(QTextCursor.End,QTextCursor.MoveAnchor)
            self.textOutput.append(str(curTime).decode('utf-8')+'\n'.decode('utf-8')+strangeWords)
        if os.path.exists(sentLinePath) == True:
            sentLinePng = QtGui.QPixmap(sentLinePath)
            self.pngOutput.setPixmap(sentLinePng)
        else:
            self.pngOutput.setText(u'没有新的弹幕消息')
        strangeTimeStr = ''
        f=open(strangeTimePath,'w')
        for x in strangeTimeSet:
            strangeTimeStr += (x + '\n')
            f.write(x+'\n')
        f.close()
        self.statusMessage.setText(
            u'主播房间号:' + self.fileName + '\n' + u'时间段:\n' + strangeTimeStr + '\n' + u'分类结果所在路径:' + clfResPath)
    #预测当前抓取数据情感倾向（需要使用到上次得到的posProbility的最后面windowSize-1个、需要之前全部的sentValueList）
    def analyzeRawDataML(self):
        desDir = 'D:/ReviewHelpfulnessPrediction/PredictClassRes'
        figDir = 'D:/ReviewHelpfulnessPrediction/SentimentLineFig'
        strangeWordDir = 'D:/ReviewHelpfulnessPrediction/StrangeWords'
        curTime = time.strftime('%Y.%m.%d.%H.%M.%S', time.localtime(time.time()))
        rawDataSetPath = self.fileDir + '/' + self.fileName + self.fileType
        strangeWordPath = strangeWordDir + '/' + self.fileName + 'ML.txt'
        classifyResPath = desDir + '/' + self.fileName +'-'+ str(curTime) +'-'+ 'ML.xls'
        sentimentLinePath = figDir + '/' + self.fileName +'-'+ str(curTime) +'-'+ 'SCML.png'
        posNegRatioPath = figDir + '/' + self.fileName +'-'+ str(curTime) +'-'+ 'PNRML.png'
        newPosProbility, resSavePath, newRawReview, curPos = pdpnp.predictFromPosTxtDataSentTagProToExcel(rawDataSetPath,
                                                                                                    classifyResPath,
                                                                                                    self.lastPos)
        posProbility = self.oldPosProbility + newPosProbility
        rawReview = self.oldRawReview + newRawReview
        strangeFlag = False
        strangeWords=''
        if len(posProbility) != 0:
            sentValueList, posRatioList, negRatioList, strangeWordPos = pdpnp.analyzeSentimentProList(posProbility,
                                                                                                     self.windowSize,
                                                                                                     self.posBounder,
                                                                                                     self.negBounder,
                                                                                                     self.sentBounder)
            overallPosRatio = pdpnp.getOverallPosRatio(posProbility, self.posBounder)
            overallNegRatio = pdpnp.getOverallNegRatio(posProbility, self.negBounder)
            finalStrangeWordPos = pdpnp.unionStrangeWordPos(strangeWordPos)
            if len(posProbility) >= self.windowSize:
                pdpnp.drawSentimentLine(sentValueList, sentimentLinePath)
                pdpnp.drawPosNegRatioPie(overallPosRatio, overallNegRatio, posNegRatioPath)
            # outputStrangeWords(finalStrangeWordPos, rawReview)
            if len(strangeWordPos) > 0:
                pdpnp.appendStrangeWordsToTxt(curTime, finalStrangeWordPos, rawReview, strangeWordPath)
                strangeWords=pdpnp.getStrangeWords(finalStrangeWordPos, rawReview)
                strangeFlag = True
            if len(posProbility) > self.windowSize - 1:
                self.oldPosProbility = posProbility[len(posProbility) - self.windowSize + 1:len(posProbility)]
                self.oldRawReview = rawReview[len(rawReview) - self.windowSize + 1:len(rawReview)]
        self.lastPos=curPos
        self.sentValueList+=sentValueList
        self.dataEndPos=len(self.sentValueList)

        # 输出不良内容、主播房间号、时间
        strangeTimeDir = 'D:/ReviewHelpfulnessPrediction/StrangeTimes/'
        strangeTimePath = strangeTimeDir + self.fileName + '.txt'
        if os.path.exists(strangeTimePath) == True:
            strangeTimeSet = tp.get_txt_data(strangeTimePath, 'lines')
        else:
            strangeTimeSet = []
        if strangeFlag==True:
            strangeTimeSet.append(curTime)
        if strangeWords:
            self.textOutput.append(str(curTime).decode('utf-8')+'\n'.decode('utf-8')+strangeWords)
        strangeTimeStr = ''
        f = open(strangeTimePath, 'w')
        for x in strangeTimeSet:
            strangeTimeStr += (x + '\n')
            f.write(x + '\n')
        f.close()
        self.statusMessage.setText(
            u'主播房间号:' + self.fileName + '\n' + u'时间段:\n' + strangeTimeStr + '\n' + u'分类结果所在路径:' + classifyResPath)
        print sentValueList


    #显示静态图像 用于综合分析整天数据 workMode=0
    def mlHandleStaticDialog(self):
        #windowSize,posBounder,negBounder,sentScoreBounder
        windowSize, sentBounder, posBounder, negBounder, ok = basicParmSetDialog.getParmValue()
        if ok:
            self.workMode=0
            if self.timer.isActive():
                self.timer.stop()
            self.windowSize=windowSize
            self.sentBounder=sentBounder
            self.posBounder=posBounder
            self.negBounder=negBounder
            fileDir,fileName,fileType=self.parseFilePath(str(self.rawDataPath))
            strangeWordPath,sentLinePath,clfResPath=pdpnp.sentiAnalyzeBaseUIML(fileDir,fileName,fileType,windowSize,posBounder,negBounder,sentBounder)
            if os.path.exists(strangeWordPath)==True:
                strangeWords=tp.get_txt_str_data(strangeWordPath,'lines')
                self.textOutput.setText(strangeWords)
            else:
                self.textOutput.setText(u'未发现不良内容')
            if os.path.exists(sentLinePath)==True:
                sentLinePng=QtGui.QPixmap(sentLinePath)
                self.pngOutput.setPixmap(sentLinePng)
            else:
                self.pngOutput.setText(u'窗口设置过大或抓取消息数过少')

            self.statusMessage.setText(u'主播房间号:'+fileName+'\n'+u'分类结果所在路径:'+clfResPath)
    #适时预测并分析刚产生弹幕数据，绘制当前数据静态图像 异常话语后续添加 workMode=1
    def mlShowCurCrabStaticPngDialog(self):
        windowSize, sentBounder, posBounder, negBounder,timeSize,ok = dynamicParmSetDialog.getParmValue()
        if ok:
            self.workMode=1
            if self.timer.isActive() == False:
                self.timer.start(1000, self)
            else:
                self.timer.stop()
                self.timer.start(1000,self)
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            self.timeSize=timeSize
            print self.timeSize
            self.fileDir, self.fileName, self.fileType = self.parseFilePath(str(self.rawDataPath))
            self.removeFile('D:/ReviewHelpfulnessPrediction/StrangeTimes/' + self.fileName + '.txt')
            self.timeRun=0
            self.lastPos=0
            self.oldPosProbility = []
            self.oldRawReview = []
            self.textOutput.setText('')
            self.showCurCrabStaticPngML()
    #适时预测刚产生弹幕数据，分析所有数据，绘制所有数据静态图像 异常话语覆盖 workMode=2
    def mlShowAllCrabStaticPngDialog(self):
        windowSize, sentBounder, posBounder, negBounder, timeSize, ok = dynamicParmSetDialog.getParmValue()
        if ok:
            self.workMode=2
            if self.timer.isActive() == False:
                self.timer.start(1000, self)
            else:
                self.timer.stop()
                self.timer.start(1000,self)
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            self.timeSize = timeSize
            self.fileDir, self.fileName, self.fileType = self.parseFilePath(str(self.rawDataPath))
            self.removeFile('D:/ReviewHelpfulnessPrediction/StrangeTimes/' + self.fileName + '.txt')
            self.timeRun = 0
            self.lastPos=0
            self.oldPosProbility = []
            self.oldRawReview = []
            self.textOutput.setText('')
            self.showAllCrabStaticPngML()
    # 绘制动图 workMode=3
    def mlDrawDynamicLineDialog(self):
        windowSize, sentBounder, posBounder, negBounder, timeSize,messageNum,drawSpeed,ok = dyLineParmSetDialog.getParmValue()
        print timeSize,drawSpeed
        if ok:
            self.workMode = 3
            ms=drawSpeed #隔多少ms画一次图
            if ms>1000:
                ms=1000
            # if self.timer.isActive() == False:
            #     self.timer.start(ms, self)
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            self.timeSize=timeSize*1000/ms
            self.dyLineShowWidth = messageNum
            self.fileDir, self.fileName, self.fileType = self.parseFilePath(str(self.rawDataPath))
            self.removeFile('D:/ReviewHelpfulnessPrediction/StrangeTimes/'+self.fileName+'.txt')
            self.timeRun = 0
            self.lastPos = 0
            self.lastDrawPos = 0
            self.oldPosProbility = []
            self.oldRawReview = []
            self.sentValueList = []
            # clear past content
            self.textOutput.setText("")
            self.pngOutput.setText("")
            emptyPng = QtGui.QPixmap("")
            self.pngOutput.setPixmap(emptyPng)
            self.analyzeRawDataML()
            if self.timer.isActive() == False:
                self.timer.start(ms, self)
            else:
                self.timer.stop()
                self.timer.start(ms,self)
    # 预测分析当前展示全部静态图 workMode=8
    def mlPreAnaCurDataShowAllStaticPngDialog(self):
        windowSize, sentBounder, posBounder, negBounder, timeSize, ok = dynamicParmSetDialog.getParmValue()
        if ok:
            self.workMode = 8
            if self.timer.isActive() == False:
                self.timer.start(1000, self)
            else:
                self.timer.stop()
                self.timer.start(1000, self)
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            self.timeSize = timeSize
            self.fileDir, self.fileName, self.fileType = self.parseFilePath(str(self.rawDataPath))
            self.removeFile('D:/ReviewHelpfulnessPrediction/StrangeTimes/' + self.fileName + '.txt')
            self.timeRun = 0
            self.lastPos = 0
            self.oldPosProbility = []
            self.oldRawReview = []
            self.sentValueList=[]
            self.textOutput.setText('')
            self.analyzeCurShowAllStaticPngML()


    #基于字典方法 workMode 4-7 9
    # 得到字典精度
    def getBasedDictAccuracy(self):
        self.clearScreenInfo()
        accuracy,dataNum=sabd.testLabelDataAcc()
        self.statusMessage.setText(u'精度:'+(str(accuracy)+'\n').decode('utf-8')+u'测试数据数量:'+str(dataNum).decode('utf-8'))
    def showCurCrabStaticPngDA(self):
        self.lastPos, self.oldPosProbility, self.oldRawReview, curTime, strangeFlag, strangeWords, sentLinePath, clfResPath = sabd.sentiAnalyzeBaseDictFromLastPosUI(
            self.oldPosProbility, self.oldRawReview, self.lastPos, self.fileDir, self.fileName, self.fileType,
            self.windowSize, self.posBounder, self.negBounder,
            self.sentBounder)
        strangeTimeDir = 'D:/ReviewHelpfulnessPrediction/StrangeTimes/'
        strangeTimePath = strangeTimeDir + self.fileName + '.txt'
        if os.path.exists(strangeTimePath) == True:
            strangeTimeSet = tp.get_txt_data(strangeTimePath, 'lines')
        else:
            strangeTimeSet = []
        if strangeWords:
            # self.textOutput.setText(strangeWords)
            # self.textOutput.moveCursor(QTextCursor.End,QTextCursor.MoveAnchor)
            self.textOutput.append(str(curTime).decode('utf-8') + '\n'.decode('utf-8') + strangeWords)
        if os.path.exists(sentLinePath) == True:
            sentLinePng = QtGui.QPixmap(sentLinePath)
            self.pngOutput.setPixmap(sentLinePng)
        else:
            self.pngOutput.setText(u'没有新的弹幕消息')
        strangeTimeStr = ''
        f = open(strangeTimePath, 'w')
        for x in strangeTimeSet:
            strangeTimeStr += (x + '\n')
            f.write(x + '\n')
        f.close()
        self.statusMessage.setText(
            u'主播房间号:' + self.fileName + '\n' + u'时间段:\n' + strangeTimeStr + '\n' + u'分类结果所在路径:' + clfResPath)
    def showAllCrabStaticPngDA(self):
        self.lastPos, self.oldPosProbility, self.oldRawReview, curTime, strangeWordPath, sentLinePath, clfResPath = sabd.sentiAnalyzeBaseDictFromPosALLUI(
            self.oldPosProbility, self.oldRawReview, self.lastPos, self.fileDir, self.fileName, self.fileType,
            self.windowSize, self.posBounder, self.negBounder,
            self.sentBounder)
        strangeTimeDir = 'D:/ReviewHelpfulnessPrediction/StrangeTimes/'
        strangeTimePath = strangeTimeDir + self.fileName + '.txt'
        if os.path.exists(strangeTimePath) == True:
            strangeTimeSet = tp.get_txt_data(strangeTimePath, 'lines')
        else:
            strangeTimeSet = []
        if os.path.exists(strangeWordPath) == True:
            curStrangeWordNum=tp.get_txt_data(strangeWordPath,'line')
            if curStrangeWordNum>self.lastStrangeWordNum:
                self.lastStrangeWordNum=curStrangeWordNum
                strangeTimeSet.append(curTime)
            strangeWords = tp.get_txt_str_data(strangeWordPath, 'lines')
            self.textOutput.setText(strangeWords)
            self.textOutput.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        else:
            self.textOutput.setText(u'未发现不良内容')
        if os.path.exists(sentLinePath) == True:
            sentLinePng = QtGui.QPixmap(sentLinePath)
            self.pngOutput.setPixmap(sentLinePng)
        else:
            self.pngOutput.setText(u'窗口设置过大或抓取消息数过少')
        strangeTimeStr = ''
        f = open(strangeTimePath, 'w')
        for x in strangeTimeSet:
            strangeTimeStr += (x + '\n')
            f.write(x + '\n')
        f.close()
        self.statusMessage.setText(
            u'主播房间号:' + self.fileName + '\n' + u'时间段:\n' + strangeTimeStr + '\n' + u'分类结果所在路径:' + clfResPath)
    def analyzeRawDataDA(self):
        desDir = 'D:/ReviewHelpfulnessPrediction/PredictClassRes'
        figDir = 'D:/ReviewHelpfulnessPrediction/SentimentLineFig'
        strangeWordDir = 'D:/ReviewHelpfulnessPrediction/StrangeWords'
        curTime = time.strftime('%Y.%m.%d.%H.%M.%S', time.localtime(time.time()))
        rawDataSetPath = self.fileDir + '/' + self.fileName + self.fileType
        strangeWordPath = strangeWordDir + '/' + self.fileName + 'DA.txt'
        classifyResPath = desDir + '/' + self.fileName +'-'+ str(curTime) +'-'+ 'DA.txt'
        sentimentLinePath = figDir + '/' + self.fileName +'-'+ str(curTime) +'-'+ 'SCDA.png'
        posNegRatioPath = figDir + '/' + self.fileName +'-'+ str(curTime) +'-'+ 'PNRDA.png'
        newRawReview, curPos=tp.get_txt_data_from_pos(rawDataSetPath,'lines',self.lastPos)
        sentimentScoreList = sabd.get_review_set_sentiement_score(newRawReview)
        newPosProbility=sabd.get_sentiment_overall_score_to_txt(sentimentScoreList,newRawReview,classifyResPath)
        posProbility = self.oldPosProbility + newPosProbility
        rawReview = self.oldRawReview + newRawReview
        strangeFlag = False
        strangeWords=''
        if len(posProbility) != 0:
            sentValueList, posRatioList, negRatioList, strangeWordPos = sabd.analyzeSentimentProList(posProbility,
                                                                                                     self.windowSize,
                                                                                                     self.posBounder,
                                                                                                     self.negBounder,
                                                                                                     self.sentBounder)
            overallPosRatio = sabd.getOverallPosRatio(posProbility, self.posBounder)
            overallNegRatio = sabd.getOverallNegRatio(posProbility, self.negBounder)
            finalStrangeWordPos = sabd.unionStrangeWordPos(strangeWordPos)
            if len(posProbility) >= self.windowSize:
                sabd.drawSentimentLine(sentValueList, sentimentLinePath)
                sabd.drawPosNegRatioPie(overallPosRatio, overallNegRatio, posNegRatioPath)
            # outputStrangeWords(finalStrangeWordPos, rawReview)
            if len(strangeWordPos) > 0:
                sabd.appendStrangeWordsToTxt(curTime, finalStrangeWordPos, rawReview, strangeWordPath)
                strangeWords=sabd.getStrangeWords(finalStrangeWordPos, rawReview)
                strangeFlag = True
            if len(posProbility) > self.windowSize - 1:
                self.oldPosProbility = posProbility[len(posProbility) - self.windowSize + 1:len(posProbility)]
                self.oldRawReview = rawReview[len(rawReview) - self.windowSize + 1:len(rawReview)]
        self.lastPos=curPos
        self.sentValueList+=sentValueList
        self.dataEndPos=len(self.sentValueList)

        # 输出不良内容、主播房间号、时间
        strangeTimeDir = 'D:/ReviewHelpfulnessPrediction/StrangeTimes/'
        strangeTimePath = strangeTimeDir + self.fileName + '.txt'
        if os.path.exists(strangeTimePath) == True:
            strangeTimeSet = tp.get_txt_data(strangeTimePath, 'lines')
        else:
            strangeTimeSet = []
        if strangeFlag==True:
            strangeTimeSet.append(curTime)
        if strangeWords:
            self.textOutput.append(str(curTime).decode('utf-8')+'\n'.decode('utf-8')+strangeWords)
        strangeTimeStr = ''
        f = open(strangeTimePath, 'w')
        for x in strangeTimeSet:
            strangeTimeStr += (x + '\n')
            f.write(x + '\n')
        f.close()
        self.statusMessage.setText(
            u'主播房间号:' + self.fileName + '\n' + u'时间段:\n' + strangeTimeStr + '\n' + u'分类结果所在路径:' + classifyResPath)
        print sentValueList
    def analyzeCurShowAllStaticPngDA(self):
        self.lastPos, self.sentValueList,self.oldPosProbility, self.oldRawReview, curTime, strangeFlag,strangeWords, sentLinePath, clfResPath = sabd.sentiAnalyzeBaseDictFromLastPosShowAllUI(
            self.sentValueList,self.oldPosProbility, self.oldRawReview, self.lastPos, self.fileDir, self.fileName, self.fileType,
            self.windowSize, self.posBounder, self.negBounder,
            self.sentBounder)
        strangeTimeDir='D:/ReviewHelpfulnessPrediction/StrangeTimes/'
        strangeTimePath=strangeTimeDir+self.fileName+'.txt'
        if os.path.exists(strangeTimePath)==True:
            strangeTimeSet=tp.get_txt_data(strangeTimePath,'lines')
        else:
            strangeTimeSet=[]
        if strangeWords:
            # self.textOutput.setText(strangeWords)
            # self.textOutput.moveCursor(QTextCursor.End,QTextCursor.MoveAnchor)
            self.textOutput.append(str(curTime).decode('utf-8')+'\n'.decode('utf-8')+strangeWords)
        if os.path.exists(sentLinePath) == True:
            sentLinePng = QtGui.QPixmap(sentLinePath)
            self.pngOutput.setPixmap(sentLinePng)
        else:
            self.pngOutput.setText(u'没有新的弹幕消息')
        strangeTimeStr = ''
        f=open(strangeTimePath,'w')
        for x in strangeTimeSet:
            strangeTimeStr += (x + '\n')
            f.write(x+'\n')
        f.close()
        self.statusMessage.setText(
            u'主播房间号:' + self.fileName + '\n' + u'时间段:\n' + strangeTimeStr + '\n' + u'分类结果所在路径:' + clfResPath)

    def daHandleStaticDialog(self):
        windowSize, sentBounder, posBounder, negBounder, ok = basicParmSetDialog.getParmValue()
        if ok:
            self.workMode=4
            if self.timer.isActive():
                self.timer.stop()
            self.windowSize=windowSize
            self.sentBounder=sentBounder
            self.posBounder=posBounder
            self.negBounder=negBounder
            fileDir,fileName,fileType=self.parseFilePath(str(self.rawDataPath))
            strangeWordPath,sentLinePath,clfResPath=sabd.sentiAnalyzeBaseDictUI(fileDir,fileName,fileType,windowSize,posBounder,negBounder,sentBounder)
            if os.path.exists(strangeWordPath)==True:
                strangeWords=tp.get_txt_str_data(strangeWordPath,'lines')
                self.textOutput.setText(strangeWords)
            else:
                self.textOutput.setText(u'未发现不良内容')
            if os.path.exists(sentLinePath)==True:
                sentLinePng=QtGui.QPixmap(sentLinePath)
                self.pngOutput.setPixmap(sentLinePng)
            else:
                self.pngOutput.setText(u'窗口设置过大或抓取消息数过少')

            self.statusMessage.setText(u'主播房间号:'+fileName+'\n'+u'分类结果所在路径:'+clfResPath)
    def daShowCurCrabStaticPngDialog(self):
        windowSize, sentBounder, posBounder, negBounder,timeSize,ok = dynamicParmSetDialog.getParmValue()
        if ok:
            self.workMode=5
            if self.timer.isActive() == False:
                self.timer.start(1000, self)
            else:
                self.timer.stop()
                self.timer.start(1000,self)
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            self.timeSize=timeSize
            self.fileDir, self.fileName, self.fileType = self.parseFilePath(str(self.rawDataPath))
            self.removeFile('D:/ReviewHelpfulnessPrediction/StrangeTimes/' + self.fileName + '.txt')
            self.timeRun=0
            self.lastPos=0
            self.oldPosProbility=[]
            self.oldRawReview=[]
            self.textOutput.setText('')
            self.showCurCrabStaticPngDA()
    def daShowAllCrabStaticPngDialog(self):
        windowSize, sentBounder, posBounder, negBounder, timeSize, ok = dynamicParmSetDialog.getParmValue()
        if ok:
            self.workMode=6
            if self.timer.isActive() == False:
                self.timer.start(1000, self)
            else:
                self.timer.stop()
                self.timer.start(1000,self)
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            self.timeSize = timeSize
            self.fileDir, self.fileName, self.fileType = self.parseFilePath(str(self.rawDataPath))
            self.removeFile('D:/ReviewHelpfulnessPrediction/StrangeTimes/' + self.fileName + '.txt')
            self.timeRun = 0
            self.lastPos=0
            self.oldPosProbility = []
            self.oldRawReview = []
            self.textOutput.setText('')
            self.showAllCrabStaticPngDA()
    def daDrawDynamicLineDialog(self):
        windowSize, sentBounder, posBounder, negBounder, timeSize,messageNum,drawSpeed,ok = dyLineParmSetDialog.getParmValue()
        print timeSize,drawSpeed
        if ok:
            self.workMode = 7
            ms=drawSpeed #隔多少ms画一次图
            if ms>1000:
                ms=1000
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            self.timeSize=timeSize*1000/ms
            self.dyLineShowWidth = messageNum
            self.fileDir, self.fileName, self.fileType = self.parseFilePath(str(self.rawDataPath))
            self.removeFile('D:/ReviewHelpfulnessPrediction/StrangeTimes/'+self.fileName+'.txt')
            self.timeRun = 0
            self.lastPos = 0
            self.lastDrawPos = 0
            self.oldPosProbility = []
            self.oldRawReview = []
            self.sentValueList = []
            # clear past content
            self.textOutput.setText("")
            self.pngOutput.setText("")
            emptyPng = QtGui.QPixmap("")
            self.pngOutput.setPixmap(emptyPng)
            self.analyzeRawDataDA()
            if self.timer.isActive() == False:
                self.timer.start(ms, self)
            else:
                self.timer.stop()
                self.timer.start(ms,self)
    def daPreAnaCurDataShowAllStaticPngDialog(self):
        windowSize, sentBounder, posBounder, negBounder, timeSize, ok = dynamicParmSetDialog.getParmValue()
        if ok:
            self.workMode = 9
            if self.timer.isActive() == False:
                self.timer.start(1000, self)
            else:
                self.timer.stop()
                self.timer.start(1000, self)
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            self.timeSize = timeSize
            self.fileDir, self.fileName, self.fileType = self.parseFilePath(str(self.rawDataPath))
            self.removeFile('D:/ReviewHelpfulnessPrediction/StrangeTimes/' + self.fileName + '.txt')
            self.timeRun = 0
            self.lastPos = 0
            self.oldPosProbility = []
            self.oldRawReview = []
            self.sentValueList=[]
            self.textOutput.setText('')
            self.analyzeCurShowAllStaticPngDA()
    #初始化图形界面
    def initUI(self):
        self.dyLineShowWidth=100#画动态图时显示消息数
        self.sentValueList=[]
        self.lastDrawPos=0
        self.dataEndPos=len(self.sentValueList) #该点刚好超界
        self.workMode=-1 #工作模式设置
        self.lastStrangeWordNum=0
        self.fileDir=''
        self.fileName=''
        self.fileType=''
        self.lastPos=0
        self.oldPosProbility=[]
        self.oldRawReview=[]
        self.timeSize=300
        self.timeRun=0
        self.timer=QtCore.QBasicTimer()
        self.rawDataPath="D:/ReviewHelpfulnessPrediction\BulletData/pdd.txt"
        self.windowSize=30
        self.sentBounder=-0.4*self.windowSize
        self.posBounder=0.6
        self.negBounder=0.4
        widget=QtGui.QWidget()
        self.setCentralWidget(widget)
        hbox = QtGui.QHBoxLayout(self)
        self.textOutput = QtGui.QTextEdit()
        self.textOutput.setFrameShape(QtGui.QFrame.StyledPanel)

        self.pngOutput=QtGui.QLabel(self)
        self.pngOutput.setFrameShape(QtGui.QFrame.StyledPanel)
        #self.showWindow=QtGui.QFrame(self)
        self.statusMessage=QtGui.QLabel(self)
        self.statusMessage.setFrameShape(QtGui.QFrame.StyledPanel)
        self.statusMessage.setText(u'当前原始数据路径:'+self.rawDataPath)

        self.progressBar=QtGui.QProgressBar(self)

        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.textOutput)
        splitter1.addWidget(self.pngOutput)
        #splitter1.addWidget(self.showWindow)

        splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.statusMessage)
        splitter2.addWidget(self.progressBar)

        hbox.addWidget(splitter2)
        #self.setLayout(hbox)
        #self.setCentralWidget(hbox)
        widget.setLayout(hbox)
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

        viewClfResAction=QtGui.QAction(QtGui.QIcon('viewClfRes.png'),u'查看预测结果',self)
        #viewClfResAction.setShortcut('Ctrl+N')
        viewClfResAction.triggered.connect(self.viewClsResDialog)

        viewStrangeWordsAction = QtGui.QAction(QtGui.QIcon('viewStrangeWords.png'), u'查看不良内容', self)
        #viewStrangeWordsAction.setShortcut('Ctrl+N')
        viewStrangeWordsAction.triggered.connect(self.viewStrangeWordsDialog)

        viewFigAction = QtGui.QAction(QtGui.QIcon('viewFig.png'), u'查看图片', self)
        #viewFigAction.setShortcut('Ctrl+N')
        viewFigAction.triggered.connect(self.viewFigDialog)

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), u'退出', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)

        changeRawDataPathAction=QtGui.QAction(QtGui.QIcon('changeRawDataPath.png'), u'更改原始数据路径', self)
        #changeRawDataPathAction.setShortcut('Ctrl+R')
        changeRawDataPathAction.triggered.connect(self.changeRawPathDialog)

        changeLabelDataPathAction = QtGui.QAction(QtGui.QIcon('changeLabelDataPath.png'), u'更改标记数据路径', self)
        #changeLabelDataPathAction.setShortcut('Ctrl+L')
        changeLabelDataPathAction.triggered.connect(self.changeLabelDataPathDialog)

        removePastDataAction=QtGui.QAction(QtGui.QIcon('removePastData.png'),u'删除之前数据',self)
        #removePastDataAction.setShortcut('Ctrl+R+P')
        removePastDataAction.triggered.connect(self.removePastDataDialog)

        clearPastAllDataAction = QtGui.QAction(QtGui.QIcon('clearPastAllData.png'), u'删除所有结果数据', self)
        # removePastDataAction.setShortcut('Ctrl+R+P')
        clearPastAllDataAction.triggered.connect(self.clearPastAllDataDialog)

        selectBestClfAction=QtGui.QAction(QtGui.QIcon('selectBestClfAction.png'), u'训练分类器', self)
        #selectBestClfAction.setShortcut('Ctrl+B')
        selectBestClfAction.triggered.connect(self.selectBestClfDialog)

        selectBestClfTenFoldAction = QtGui.QAction(QtGui.QIcon('selectBestClfTenFoldAction.png'), u'训练分类器之十折交叉验证', self)
        # selectBestClfAction.setShortcut('Ctrl+B')
        selectBestClfTenFoldAction.triggered.connect(self.selectBestClfTenFoldDialog)

        filtObjDataAction=QtGui.QAction(QtGui.QIcon('filtObjData.png'),u'过滤',self)
        filtObjDataAction.setShortcut('Ctrl+F')
        #filtObjDataAction.setStatusTip(u'过滤数据')
        filtObjDataAction.triggered.connect(self.filtDataDialog)

        removeDupDataAction=QtGui.QAction(QtGui.QIcon('removeDupData.png'),u'删重',self)
        #removeDupDataAction.setShortcut('Ctrl+D')
        removeDupDataAction.triggered.connect(self.removeDupDataDialog)

        changeTxtToExcelAction=QtGui.QAction(QtGui.QIcon('changeTxtToExcel.png'),u'格式转化',self)
        #changeTxtToExcelAction.setShortcut('Ctrl+E')
        changeTxtToExcelAction.triggered.connect(self.saveTxtToExcelDialog)

        saveLabelToSpeNameAction=QtGui.QAction(QtGui.QIcon('saveLabelToSpeName.png'),u'保存标记数据',self)
        #saveLabelToSpeNameAction.setShortcut('Ctrl+T')
        saveLabelToSpeNameAction.triggered.connect(self.saveLabelAndKeyWordToSpeNameDialog)

        unoinLabelKeyWordAction=QtGui.QAction(QtGui.QIcon('unoinLabelKeyWord.png'),u'合并标记数据',self)
        #unoinLabelKeyWordAction.setShortcut('Ctrl+U')
        unoinLabelKeyWordAction.triggered.connect(self.unionLabelData)

        modifyParmAction=QtGui.QAction(QtGui.QIcon('modifyParm.png'),u'修改参数',self)
        modifyParmAction.triggered.connect(self.modifyParmDialog)

        mlHandleStaticTxtAction=QtGui.QAction(QtGui.QIcon('mlHandleStaticTxt.png'),u'预测分析展示全部静态图',self)
        #mlHandleStaticTxtAction.setShortcut('Ctrl+M+S')
        mlHandleStaticTxtAction.triggered.connect(self.mlHandleStaticDialog)

        mlShowCurCrabStaticPngAction=QtGui.QAction(QtGui.QIcon('mlShowCurCrabStatic.png'),u'预测分析当前展示当前静态图',self)
        #mlShowCurCrabStaticPngAction.setShortcut('Ctrl+M+D')
        mlShowCurCrabStaticPngAction.triggered.connect(self.mlShowCurCrabStaticPngDialog)

        mlShowAllCrabStaticPngAction=QtGui.QAction(QtGui.QIcon('mlShowAllCrabStatic.png'),u'预测当前分析展示全部静态图',self)
        #mlShowAllCrabStaticPngAction.setShortcut('Ctrl+P')
        mlShowAllCrabStaticPngAction.triggered.connect(self.mlShowAllCrabStaticPngDialog)

        mlPreAnaCurShowAllStaticPngAction = QtGui.QAction(QtGui.QIcon('mlPreAnaCurShowAllStatic.png'), u'预测分析当前展示全部静态图', self)
        #mlPreAnaCurShowAllStaticPngAction.setShortcut('Ctrl+P')
        mlPreAnaCurShowAllStaticPngAction.triggered.connect(self.mlPreAnaCurDataShowAllStaticPngDialog)

        mlDrawDySentLineAction=QtGui.QAction(QtGui.QIcon('mlDrawDySentLine'),u'预测分析当前展示当前动图',self)
        #mlDrawDySentLineAction.setShortcut('Ctrl+L+D')
        mlDrawDySentLineAction.triggered.connect(self.mlDrawDynamicLineDialog)



        getBasedDictAccAction=QtGui.QAction(QtGui.QIcon('getBasedDictAcc.png'),u'精度',self)
        getBasedDictAccAction.triggered.connect(self.getBasedDictAccuracy)

        daHandleStaticTxtAction = QtGui.QAction(QtGui.QIcon('daHandleStaticTxt.png'), u'预测分析展示全部静态图', self)
        #daHandleStaticTxtAction.setShortcut('Ctrl+M+S')
        daHandleStaticTxtAction.triggered.connect(self.daHandleStaticDialog)

        daShowCurCrabStaticPngAction = QtGui.QAction(QtGui.QIcon('daShowCurCrabStatic.png'), u'预测分析当前展示当前静态图', self)
        #daShowCurCrabStaticPngAction.setShortcut('Ctrl+M+D')
        daShowCurCrabStaticPngAction.triggered.connect(self.daShowCurCrabStaticPngDialog)

        daShowAllCrabStaticPngAction = QtGui.QAction(QtGui.QIcon('daShowAllCrabStatic.png'), u'预测当前分析展示全部静态图', self)
        #daShowAllCrabStaticPngAction.setShortcut('Ctrl+P')
        daShowAllCrabStaticPngAction.triggered.connect(self.daShowAllCrabStaticPngDialog)

        daPreAnaCurShowAllStaticPngAction = QtGui.QAction(QtGui.QIcon('daPreAnaCurShowAllStatic.png'), u'预测分析当前展示全部静态图', self)
        #daShowAllCrabStaticPngAction.setShortcut('Ctrl+P')
        daPreAnaCurShowAllStaticPngAction.triggered.connect(self.daPreAnaCurDataShowAllStaticPngDialog)

        daDrawDySentLineAction = QtGui.QAction(QtGui.QIcon('mlDrawDySentLine'), u'预测分析当前展示当前动图', self)
        #daDrawDySentLineAction.setShortcut('Ctrl+L+D')
        daDrawDySentLineAction.triggered.connect(self.daDrawDynamicLineDialog)

        #self.statusBar()


        menubar = self.menuBar()
        fileMenu = menubar.addMenu(u'设置')
        fileMenu.addAction(changeRawDataPathAction)
        fileMenu.addAction(changeLabelDataPathAction)
        fileMenu.addAction(modifyParmAction)
        fileMenu.addAction(removePastDataAction)
        fileMenu.addAction(clearPastAllDataAction)
        fileMenu.addAction(viewClfResAction)
        fileMenu.addAction(viewFigAction)
        fileMenu.addAction(viewStrangeWordsAction)
        fileMenu.addAction(exitAction)
        #预处理菜单项
        preProcessMenu=menubar.addMenu(u'预处理')
        preProcessMenu.addAction(filtObjDataAction)
        preProcessMenu.addAction(removeDupDataAction)
        preProcessMenu.addAction(changeTxtToExcelAction)
        preProcessMenu.addAction(saveLabelToSpeNameAction)
        preProcessMenu.addAction(unoinLabelKeyWordAction)
        #机器学习
        machineLearnMenu=menubar.addMenu(u'机器学习')
        machineLearnMenu.addAction(changeRawDataPathAction)
        machineLearnMenu.addAction(selectBestClfAction)
        machineLearnMenu.addAction(selectBestClfTenFoldAction)
        machineLearnMenu.addAction(mlHandleStaticTxtAction)
        machineLearnMenu.addAction(mlShowCurCrabStaticPngAction)
        machineLearnMenu.addAction(mlShowAllCrabStaticPngAction)
        machineLearnMenu.addAction(mlPreAnaCurShowAllStaticPngAction)
        machineLearnMenu.addAction(mlDrawDySentLineAction)
        basedDictMenu=menubar.addMenu(u'词典')
        basedDictMenu.addAction(changeRawDataPathAction)
        basedDictMenu.addAction(getBasedDictAccAction)
        basedDictMenu.addAction(daHandleStaticTxtAction)
        basedDictMenu.addAction(daShowCurCrabStaticPngAction)
        basedDictMenu.addAction(daShowAllCrabStaticPngAction)
        basedDictMenu.addAction(daPreAnaCurShowAllStaticPngAction)
        basedDictMenu.addAction(daDrawDySentLineAction)

        # toolbar = self.addToolBar('Exit')
        # toolbar.addAction(exitAction)

        self.setGeometry(200, 200, 600, 400)
        self.setWindowTitle('Main window')
        self.show()

def main():
    app=QtGui.QApplication(sys.argv)
    sa=SA()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()