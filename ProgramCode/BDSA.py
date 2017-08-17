#! /usr/bin/env python2.7
#coding=utf-8

"""
using PyQt4 package

author: Kuang Peng
last edited: August 2017
"""

import os
import sys
import predictDataPosNegProbility as pdpnp
import selectBestClassifier as sbc
import sentimentAnalyzeBasedDict as sabd
import textProcessing as tp
import unlabelDataProcessToLabel as udptl
from PyQt4 import QtGui
from PyQt4 import QtCore
import basicParmSetDialog
import dynamicParmSetDialog
import time

class SA(QtGui.QMainWindow):
    def __init__(self):
        super(SA,self).__init__()
        self.initUI()
    def filtDataDialog(self):
        srcPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                  'D:/crambData/')
        fileDir, fileName, fileType = self.parseFilePath(str(srcPath))
        dstDir='D:/ReviewHelpfulnessPrediction/BulletData/'
        dstPath=dstDir+fileName+'.txt'
        udptl.filt_objective_sentence(srcPath,'lines',dstPath)
        self.statusMessage.setText(u'过滤后数据保存在：'+dstPath)

    def removeDupDataDialog(self):
        srcPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                    'D:/ReviewHelpfulnessPrediction/BulletData/')
        fileDir,fileName,fileType=self.parseFilePath(str(srcPath))
        dstDir = 'D:/ReviewHelpfulnessPrediction/LabelingData/'
        dstPath = dstDir + fileName + '.xls'
        #udptl.filt_objective_sentence(srcPath, 'lines', dstPath)
        udptl.remove_duplicate_comment(srcPath,'lines',dstPath)
        self.statusMessage.setText(u'去重后数据保存在：' + dstPath)

    def saveTxtToExcelDialog(self):
        srcPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                    'D:/crambData/')
        fileDir, fileName, fileType = self.parseFilePath(str(srcPath))
        dstDir = 'D:/ReviewHelpfulnessPrediction/LabelingData/'
        dstPath = dstDir + fileName + '.xls'
        udptl.change_txt_to_excel(srcPath,'lines',dstPath)
        self.statusMessage.setText(u'转化后数据保存在：'+dstPath)

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
        self.statusMessage.setText(u'标记数据保存目录：' + dstDir+' '+fileName)
        errorStr=''
        for x in errorRow:
            for y in x:
                errorStr+=str(y)+' '
            errorStr+='\n'
        self.textOutput.setText(errorStr)

    def unionLabelData(self):
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
        udptl.unionFewLabelData(speNameLabelDataDir,nameSet,labeledDataDir)
        udptl.unionKeyWords(keyWordDir,nameSet)
        self.textOutput.setText(nameStr)
        self.statusMessage.setText(u'关键词所在目录：'+keyWordDir+'\n'+u'合并后标记数据所在目录：'+labeledDataDir)

    def parseFilePath(self,path):
        strs=path.split('/')
        nameType=strs[len(strs)-1].split('.')
        strs.pop(len(strs)-1)
        fileDir='/'.join(strs)
        fileName=nameType[0]
        fileType='.'+nameType[1]
        return fileDir,fileName,fileType

    def changeRawPathDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                  'D:/ReviewHelpfulnessPrediction/BulletData/')
        self.rawDataPath=fname
        self.statusMessage.setText(u'原始数据路径更改为：'+fname)

    def changeLabelDataPathDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                  'D:/ReviewHelpfulnessPrediction/LabelReviewData')
        f=open('D:/ReviewHelpfulnessPrediction/LabelDataPath.txt','w')
        f.write(str(fname))
        f.close()
        self.statusMessage.setText(u'标记数据路径更改为：'+fname)

    def removePastDataDialog(self):
        curTime = time.strftime('%Y.%m.%d.%H.%M.%S', time.localtime(time.time()))
        pass
    def selectBestClfDialog(self):
        message,clfNameAcc=sbc.handleSelectClfWork()
        processResStr=''
        for x in clfNameAcc:
            processResStr+=(x+'\n')
        self.textOutput.setText(processResStr)
        self.statusMessage.setText(message)

    def mlHandleStaticDialog(self):
        #windowSize,posBounder,negBounder,sentScoreBounder
        windowSize, sentBounder, posBounder, negBounder, ok = basicParmSetDialog.getParmValue()
        if ok:
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

    def timerEvent(self,e):
        if self.timeRun>=self.timeSize:
            self.timeRun=0
            self.test()
            return
        self.timeRun+=1
        print self.timeRun

    def test(self):
        self.lastPos, self.oldPosProbility, self.oldRawReview, curTime, strangeWordPath, sentLinePath, clfResPath = pdpnp.sentiAnalyzeBaseUIMLFromPos(
            self.oldPosProbility, self.oldRawReview, self.lastPos, self.fileDir, self.fileName, self.fileType,
            self.windowSize, self.posBounder, self.negBounder,
            self.sentBounder)
        print self.lastPos
        strangeTimeSet=[]
        if os.path.exists(strangeWordPath) == True:
            curStrangeWordNum = int(tp.get_txt_data(strangeWordPath, 'line'))
            if curStrangeWordNum > self.lastStrangeWordNum:
                strangeTimeSet.append(curTime)
                self.lastStrangeWordNum = curStrangeWordNum
            strangeWords = tp.get_txt_str_data(strangeWordPath, 'lines')
            self.textOutput.setText(strangeWords)
        else:
            self.textOutput.setText(u'未发现不良内容')
        if os.path.exists(sentLinePath) == True:
            sentLinePng = QtGui.QPixmap(sentLinePath)
            self.pngOutput.setPixmap(sentLinePng)
        else:
            self.pngOutput.setText(u'窗口设置过大或抓取消息数过少')
        strangeTimeStr = ''
        for x in strangeTimeSet:
            strangeTimeStr += (x + '\n')
        self.statusMessage.setText(
            u'主播房间号:' + self.fileName + '\n' + u'时间段:\n' + strangeTimeStr + '\n' + u'分类结果所在路径:' + clfResPath)

    def mlHandleOneDynamicDialog(self):
        windowSize, sentBounder, posBounder, negBounder,timeSize,ok = dynamicParmSetDialog.getParmValue()
        if ok:
            self.timer.start(1000,self)
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            fileDir, fileName, fileType = self.parseFilePath(str(self.rawDataPath))
            lastPos=0
            oldPosProbility=[]
            oldRawReview=[]
            lastStrangeWordNum=0
            strangeTimeSet=[]
            while True:
                if self.timer.isActive()==False:
                    self.timer.start(1000,self)
                lastPos,oldPosProbility,oldRawReview,curTime,strangeWordPath,sentLinePath,clfResPath=pdpnp.sentiAnalyzeBaseUIMLFromPos(oldPosProbility,oldRawReview,lastPos,fileDir,fileName,fileType,windowSize,posBounder,negBounder,sentBounder)
                if os.path.exists(strangeWordPath) == True:
                    curStrangeWordNum=int(tp.get_txt_data(strangeWordPath,'line'))
                    if curStrangeWordNum>lastStrangeWordNum:
                        strangeTimeSet.append(curTime)
                        lastStrangeWordNum=curStrangeWordNum
                    strangeWords = tp.get_txt_str_data(strangeWordPath, 'lines')
                    self.textOutput.setText(strangeWords)
                else:
                    self.textOutput.setText(u'未发现不良内容')
                if os.path.exists(sentLinePath) == True:
                    sentLinePng = QtGui.QPixmap(sentLinePath)
                    self.pngOutput.setPixmap(sentLinePng)
                else:
                    self.pngOutput.setText(u'窗口设置过大或抓取消息数过少')
                strangeTimeStr=''
                for x in strangeTimeSet:
                    strangeTimeStr+=(x+'\n')
                self.statusMessage.setText(u'主播房间号:' + fileName + '\n'+u'时间段:\n'+strangeTimeStr+'\n'+ u'分类结果所在路径:' + clfResPath)
    '''返回上次处理的windowSize-1个数据 以便于绘制连续曲线'''
    '''存在问题：窗口长时间得不到响应 需要多线程编程'''
    def mlSaveStrangeFromDynamicTxtDialog(self):
        windowSize, sentBounder, posBounder, negBounder,timeSize,ok = dynamicParmSetDialog.getParmValue()
        if ok:
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            fileDir, fileName, fileType = self.parseFilePath(str(self.rawDataPath))
            lastPos=0
            oldPosProbility=[]
            oldRawReview=[]
            lastStrangeWordNum=0
            strangeTimeSet=[]
            while True:
                begin = time.clock()
                lastPos,oldPosProbility,oldRawReview,curTime,strangeFlag,strangeWordPath,sentLinePath,clfResPath=pdpnp.sentiAnalyzeBaseUIMLFromLastPos(oldPosProbility,oldRawReview,lastPos,fileDir,fileName,fileType,windowSize,posBounder,negBounder,sentBounder)
                # if len(oldPosProbility)>windowSize-1:
                #     oldPosProbility=oldPosProbility[len(oldPosProbility)-windowSize+1:len(oldPosProbility)]
                #     oldRawReview=oldRawReview[len(oldRawReview)-windowSize+1:len(oldRawReview)]
                while time.clock()-begin<timeSize:
                    pass

    def mlShowStrangeFromDynamicTxtDialog(self):
        windowSize, sentBounder, posBounder, negBounder,timeSize,ok = dynamicParmSetDialog.getParmValue()
        if ok:
            if self.timer.isActive() == False:
                self.timer.start(1000, self)
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            self.timeSize=timeSize
            self.fileDir, self.fileName, self.fileType = self.parseFilePath(str(self.rawDataPath))
            self.timeRun=0
            self.test()


    def mlDrawDynamicLineDlg(self):
        windowSize, sentBounder, posBounder, negBounder, ok = basicParmSetDialog.getParmValue()
        if ok:
            self.windowSize = windowSize
            self.sentBounder = sentBounder
            self.posBounder = posBounder
            self.negBounder = negBounder
            fileDir, fileName, fileType = self.parseFilePath(str(self.rawDataPath))
            lastPos = 0
            oldPosProbility = []
            oldRawReview = []
            lastStrangeWordNum = 0
            strangeTimeSet = []
            while True:
                begin = time.clock()
                lastPos, oldPosProbility, oldRawReview, curTime, strangeWordPath, sentLinePath, clfResPath = pdpnp.sentiAnalyzeBaseUIMLFromPos(
                    oldPosProbility, oldRawReview, lastPos, fileDir, fileName, fileType, windowSize, posBounder,
                    negBounder, sentBounder)

    def initUI(self):
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

        self.statusMessage=QtGui.QLabel(self)
        self.statusMessage.setFrameShape(QtGui.QFrame.StyledPanel)
        self.statusMessage.setText(u'当前原始数据路径:'+self.rawDataPath)

        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.textOutput)
        splitter1.addWidget(self.pngOutput)

        splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.statusMessage)

        hbox.addWidget(splitter2)
        #self.setLayout(hbox)
        #self.setCentralWidget(hbox)
        widget.setLayout(hbox)
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), u'退出', self)
        exitAction.setShortcut('Ctrl+Q')
        #exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        changeRawDataPathAction=QtGui.QAction(QtGui.QIcon('changeRawDataPath.png'), u'更改原始数据路径', self)
        changeRawDataPathAction.setShortcut('Ctrl+R')
        #exitAction.setStatusTip('Exit application')
        changeRawDataPathAction.triggered.connect(self.changeRawPathDialog)

        changeLabelDataPathAction = QtGui.QAction(QtGui.QIcon('changeLabelDataPath.png'), u'更改标记数据路径', self)
        changeLabelDataPathAction.setShortcut('Ctrl+L')
        # exitAction.setStatusTip('Exit application')
        changeLabelDataPathAction.triggered.connect(self.changeLabelDataPathDialog)

        selectBestClfAction=QtGui.QAction(QtGui.QIcon('selectBestClfAction.png'), u'训练分类器', self)
        selectBestClfAction.setShortcut('Ctrl+B')
        #exitAction.setStatusTip('Exit application')
        selectBestClfAction.triggered.connect(self.selectBestClfDialog)

        filtObjDataAction=QtGui.QAction(QtGui.QIcon('filtObjData.png'),u'过滤',self)
        filtObjDataAction.setShortcut('Ctrl+F')
        #filtObjDataAction.setStatusTip(u'过滤数据')
        filtObjDataAction.triggered.connect(self.filtDataDialog)

        removeDupDataAction=QtGui.QAction(QtGui.QIcon('removeDupData.png'),u'删重',self)
        removeDupDataAction.setShortcut('Ctrl+D')
        removeDupDataAction.triggered.connect(self.removeDupDataDialog)

        changeTxtToExcelAction=QtGui.QAction(QtGui.QIcon('changeTxtToExcel.png'),u'格式转化',self)
        changeTxtToExcelAction.setShortcut('Ctrl+E')
        changeTxtToExcelAction.triggered.connect(self.saveTxtToExcelDialog)

        saveLabelToSpeNameAction=QtGui.QAction(QtGui.QIcon('saveLabelToSpeName.png'),u'保存标记数据',self)
        saveLabelToSpeNameAction.setShortcut('Ctrl+T')
        saveLabelToSpeNameAction.triggered.connect(self.saveLabelAndKeyWordToSpeNameDialog)

        unoinLabelKeyWordAction=QtGui.QAction(QtGui.QIcon('unoinLabelKeyWord.png'),u'合并标记数据',self)
        unoinLabelKeyWordAction.setShortcut('Ctrl+U')
        unoinLabelKeyWordAction.triggered.connect(self.unionLabelData)

        mlHandleStaticTxtAction=QtGui.QAction(QtGui.QIcon('mlHandleStaticTxt.png'),u'静态分类',self)
        mlHandleStaticTxtAction.setShortcut('Ctrl+M+S')
        mlHandleStaticTxtAction.triggered.connect(self.mlHandleStaticDialog)

        mlHandleDynamicTxtAction=QtGui.QAction(QtGui.QIcon('mlHandleDynamicTxt.png'),u'动态分类之静态图',self)
        mlHandleDynamicTxtAction.setShortcut('Ctrl+M+D')
        mlHandleDynamicTxtAction.triggered.connect(self.mlShowStrangeFromDynamicTxtDialog)
        #self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu(u'设置')
        fileMenu.addAction(changeRawDataPathAction)
        fileMenu.addAction(changeLabelDataPathAction)
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
        machineLearnMenu.addAction(mlHandleStaticTxtAction)
        machineLearnMenu.addAction(mlHandleDynamicTxtAction)
        basedDictMenu=menubar.addMenu(u'字典')

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