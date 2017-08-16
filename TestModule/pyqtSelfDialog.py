#!/usr/bin/env python
# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class FontPropertiesDlg(QDialog):
    def __init__(self, format, parent=None):
        super(FontPropertiesDlg, self).__init__(parent)
        self.format = format
        FontStyleLabel = QLabel(u"中文字体:")
        self.FontstyleComboBox = QComboBox()
        self.FontstyleComboBox.addItems([u"宋体", u"黑体", u"仿宋",
                                         u"隶书", u"楷体"])
        self.FontEffectCheckBox = QCheckBox(u"使用特效")
        FontSizeLabel = QLabel(u"字体大小")
        self.FontSizeSpinBox = QSpinBox()
        self.FontSizeSpinBox.setRange(1, 90)
        applyButton = QPushButton(u"应用")
        cancelButton = QPushButton(u"取消")

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(applyButton)
        buttonLayout.addWidget(cancelButton)
        layout = QGridLayout()
        layout.addWidget(FontStyleLabel, 0, 0)
        layout.addWidget(self.FontstyleComboBox, 0, 1)
        layout.addWidget(FontSizeLabel, 1, 0)
        layout.addWidget(self.FontSizeSpinBox, 1, 1)
        layout.addWidget(self.FontEffectCheckBox, 1, 2)
        layout.addLayout(buttonLayout, 2, 0)
        self.setLayout(layout)

        self.connect(applyButton, SIGNAL("clicked()"), self.apply)
        self.connect(cancelButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        self.setWindowTitle(u"字体")

    def apply(self):
        self.format["fontstyle"] = unicode(self.FontstyleComboBox.currentText())
        self.format["fontsize"] = self.FontSizeSpinBox.value()
        self.format["fonteffect"] = self.FontEffectCheckBox.isChecked()
        self.emit(SIGNAL("changed"))


