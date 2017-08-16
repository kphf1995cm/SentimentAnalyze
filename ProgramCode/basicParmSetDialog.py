#!/usr/bin/env python
# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

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
        verticalLayout.addLayout(hLayout1,0)
        verticalLayout.addLayout(hLayout2, 1)
        verticalLayout.addLayout(hLayout3, 2)
        verticalLayout.addLayout(hLayout4, 3)

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


def checkParmValueValid():
    pass
def getParmValue(parent=None):
    dialog=BasicParmSetDlg(parent)
    result=dialog.exec_()
    windowSize = float(dialog.edit1.text())
    sentBounder = float(dialog.edit2.text())
    posBounder = float(dialog.edit3.text())
    negBounder = float(dialog.edit4.text())
    return (windowSize,sentBounder,posBounder,negBounder,result == QDialog.Accepted)
