#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial

In the example, we draw randomly 1000 red points
on the window.

author: Jan Bodnar
website: zetcode.com
last edited: September 2011
"""

import sys, random
from PyQt4 import QtGui, QtCore


class Example(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Points')
        self.show()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()

    def drawPoints(self, qp):
        qp.setPen(QtCore.Qt.red)
        size = self.size()
        x=range(100)
        y=[]
        for i in range(100):
            y.append(random.randint(0,100))
        path=QtGui.QPainterPath(self)

        qp.drawPath(x,y)

        for x in range(100):
            qp.drawPoint(x,100)
        qp.drawLine(50,0,80,100)



def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()