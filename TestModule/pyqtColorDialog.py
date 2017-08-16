#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial

In this example, we select a colour value
from the QtGui.QColorDialog and change the background
colour of a QtGui.QFrame widget.

author: Jan Bodnar
website: zetcode.com
last edited: October 2011
"""

import sys
from PyQt4 import QtGui


class Example(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):
        col = QtGui.QColor(0, 0, 0)

        self.btn = QtGui.QPushButton('Dialog', self)
        self.btn.move(20, 20)

        self.btn.clicked.connect(self.showDialog)

        self.frm = QtGui.QFrame(self)
        self.frm.setStyleSheet("QWidget { background-color: %s }"
                               % col.name())
        self.frm.setGeometry(130, 22, 100, 100)

        self.setGeometry(300, 300, 250, 180)
        self.setWindowTitle('Color dialog')
        self.show()

    def showDialog(self):
        col = QtGui.QColorDialog.getColor()

        if col.isValid():
            self.frm.setStyleSheet("QWidget { background-color: %s }"
                                   % col.name())


def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()