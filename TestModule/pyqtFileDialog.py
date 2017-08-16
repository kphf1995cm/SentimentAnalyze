#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial

In this example, we select a file with a
QtGui.QFileDialog and display its contents
in a QtGui.QTextEdit.

author: Jan Bodnar
website: zetcode.com
last edited: October 2011
"""

import sys
from PyQt4 import QtGui



class Example(QtGui.QMainWindow):
    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):
        #self.textEdit = QtGui.QTextEdit()
        #self.textEdit = QtGui.QLabel(self)
        self.textEdit = QtGui.QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('File dialog')
        self.show()

    def get_txt_data(self,filepath, para):
        if para == 'lines':
            txt_file1 = open(filepath, 'r')
            txt_tmp1 = txt_file1.readlines()
            txt_tmp2 = ''.join(txt_tmp1)
            txt_data1 = txt_tmp2.decode('utf-8')
            txt_file1.close()
            return txt_data1
        elif para == 'line':
            txt_file2 = open(filepath, 'r')
            txt_tmp = txt_file2.readline()
            txt_data2 = txt_tmp.decode('utf-8')
            txt_file2.close()
            return txt_data2

    def showDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                  'D:/ReviewHelpfulnessPrediction\StrangeWords/')
        data=self.get_txt_data(fname,'lines')
        self.textEdit.setText(data)


def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()