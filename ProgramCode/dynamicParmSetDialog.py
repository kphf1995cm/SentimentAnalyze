#!/usr/bin/env python
# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import re

class BasicParmSetDlg(QDialog):
    def __init__(self, format, parent=None):
        super(BasicParmSetDlg, self).__init__(parent)
        self.format = format
        verticalLayout=QVBoxLayout()
        hLayout1=QHBoxLayout()
        label1=QLabel(u'窗口大小')
        self.edit1=QLineEdit()
        windowSize=30
        self.edit1.setText(str(windowSize))
        hLayout1.addWidget(label1)
        hLayout1.addWidget(self.edit1)

        hLayout2 = QHBoxLayout()
        label2 = QLabel(u'情感得分边界')
        self.edit2 = QLineEdit()
        self.edit2.setText(str(-0.4*windowSize))
        hLayout2.addWidget(label2)
        hLayout2.addWidget(self.edit2)

        hLayout3 = QHBoxLayout()
        label3 = QLabel(u'积极分值边界')
        self.edit3 = QLineEdit()
        self.edit3.setText('0.6')
        hLayout3.addWidget(label3)
        hLayout3.addWidget(self.edit3)

        hLayout4 = QHBoxLayout()
        label4 = QLabel(u'消极分值边界')
        self.edit4 = QLineEdit()
        self.edit4.setText('0.4')
        hLayout4.addWidget(label4)
        hLayout4.addWidget(self.edit4)

        hLayout5 = QHBoxLayout()
        label5 = QLabel(u'更新时间间隔')
        self.edit5 = QLineEdit()
        self.edit5.setText('300')
        hLayout5.addWidget(label5)
        hLayout5.addWidget(self.edit5)

        verticalLayout.addLayout(hLayout1,0)
        verticalLayout.addLayout(hLayout2, 1)
        verticalLayout.addLayout(hLayout3, 2)
        verticalLayout.addLayout(hLayout4, 3)
        verticalLayout.addLayout(hLayout5, 4)


        # self.applyButton = QPushButton(u"确定")
        # self.cancelButton = QPushButton(u"取消")
        #
        # buttonLayout = QHBoxLayout()
        # buttonLayout.addStretch()
        # buttonLayout.addWidget(self.applyButton)
        # buttonLayout.addWidget(self.cancelButton)
        #
        # verticalLayout.addLayout(buttonLayout,4)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        verticalLayout.addWidget(buttons)
        self.setLayout(verticalLayout)

        # self.connect(applyButton, SIGNAL("clicked()"), self.apply)
        # self.connect(cancelButton, SIGNAL("clicked()"), self, SLOT("reject()"))

        self.setWindowTitle(u"设置基本参数")

    # def apply(self):
    #     return self.edit1.text(),self.edit2.text(),self.edit3.text(),self.edit4.text()

def checkParmValueValid(parmStrList):
    #print parmStrList
    parmValue=[]
    successFlag=True
    for parm in parmStrList:
        #print parm
        m=re.match('-?\d+\.?\d*', str(parm))
        if m:
            parmValue.append(re.sub('\.$','',m.group()))
        else:
            successFlag=False
            break
    #print parmValue
    return successFlag,parmValue
def getParmValue(parent=None):
    dialog=BasicParmSetDlg(parent)
    result=dialog.exec_()
    successFlag, parmValue = checkParmValueValid(
        [dialog.edit1.text(), dialog.edit2.text(), dialog.edit3.text(), dialog.edit4.text(), dialog.edit5.text()])
    if successFlag:
        windowSize = int(parmValue[0])
        sentBounder = float(parmValue[1])
        posBounder = float(parmValue[2])
        negBounder = float(parmValue[3])
        timeSize = float(parmValue[4])
        return windowSize, sentBounder, posBounder, negBounder, timeSize, result == QDialog.Accepted
    else:
        return 0, 0, 0, 0, 0,False
    # windowSize = int(dialog.edit1.text())
    # sentBounder = float(dialog.edit2.text())
    # posBounder = float(dialog.edit3.text())
    # negBounder = float(dialog.edit4.text())
    # timeSize=float(dialog.edit5.text())
    # return (windowSize,sentBounder,posBounder,negBounder,timeSize,result == QDialog.Accepted)
