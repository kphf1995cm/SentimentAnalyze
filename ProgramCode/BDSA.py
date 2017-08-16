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

class SA(QtGui.QMainWindow):
    def __init__(self):
        super(SA,self).__init__()
        self.initUI()
    def filtDataDialog(self):
        srcPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                  'D:/crambData/')
        dstDir='D:/ReviewHelpfulnessPrediction/BulletData/'
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
                                              'Enter file name:')

        if ok:
            dstPath=dstDir+text+'.txt'
            udptl.filt_objective_sentence(srcPath,'lines',dstPath)
            self.statusMessage.setText(u'过滤后数据保存在：'+dstPath)

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
            if os.path.exists(sentLinePath)==True:
                sentLinePng=QtGui.QPixmap(sentLinePath)
                self.pngOutput.setPixmap(sentLinePng)

            self.statusMessage.setText(u'分类结果所在路径:'+clfResPath)
    def selectBestClfDialog(self):
        message=sbc.handleSelectClfWork()
        self.statusMessage.setText(message)
    def initUI(self):
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

        changeRawDataPathAction=QtGui.QAction(QtGui.QIcon('changeRawDataPath.png'), u'更改数据路径', self)
        changeRawDataPathAction.setShortcut('Ctrl+R')
        #exitAction.setStatusTip('Exit application')
        changeRawDataPathAction.triggered.connect(self.changeRawPathDialog)

        selectBestClfAction=QtGui.QAction(QtGui.QIcon('selectBestClfAction.png'), u'训练分类器', self)
        selectBestClfAction.setShortcut('Ctrl+B')
        #exitAction.setStatusTip('Exit application')
        selectBestClfAction.triggered.connect(self.selectBestClfDialog)

        filtObjDataAction=QtGui.QAction(QtGui.QIcon('filtObjData.png'),u'过滤',self)
        filtObjDataAction.setShortcut('Ctrl+F')
        #filtObjDataAction.setStatusTip(u'过滤数据')
        filtObjDataAction.triggered.connect(self.filtDataDialog)

        mlHandleStaticTxtAction=QtGui.QAction(QtGui.QIcon('mlHandleStatic.png'),u'静态分类',self)
        mlHandleStaticTxtAction.setShortcut('Ctrl+M+S')
        mlHandleStaticTxtAction.triggered.connect(self.mlHandleStaticDialog)
        #self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu(u'设置')
        fileMenu.addAction(changeRawDataPathAction)
        fileMenu.addAction(exitAction)
        #预处理菜单项
        preProcessMenu=menubar.addMenu(u'预处理')
        preProcessMenu.addAction(filtObjDataAction)
        #机器学习
        machineLearnMenu=menubar.addMenu(u'机器学习')
        machineLearnMenu.addAction(changeRawDataPathAction)
        machineLearnMenu.addAction(selectBestClfAction)
        machineLearnMenu.addAction(mlHandleStaticTxtAction)
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