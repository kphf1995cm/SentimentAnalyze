#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial

This example shows three labels on a window
using absolute positioning.

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
        lbl1 = QtGui.QLabel('ZetCode', self)
        lbl1.move(15, 10)

        lbl2 = QtGui.QLabel('tutorials', self)
        lbl2.move(35, 40)

        lbl3 = QtGui.QLabel('for programmers', self)
        lbl3.move(55, 70)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Absolute')
        self.show()


def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()