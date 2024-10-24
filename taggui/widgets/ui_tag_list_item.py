# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tag_list_item.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QToolButton, QWidget)

class Ui_TagListItem(object):
    def setupUi(self, Tag):
        if not Tag.objectName():
            Tag.setObjectName(u"Tag")
        Tag.resize(250, 60)
        self.horizontalLayout = QHBoxLayout(Tag)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Tag)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.closeButton = QToolButton(Tag)
        self.closeButton.setObjectName(u"closeButton")

        self.horizontalLayout.addWidget(self.closeButton)


        self.retranslateUi(Tag)

        QMetaObject.connectSlotsByName(Tag)
    # setupUi

    def retranslateUi(self, Tag):
        Tag.setWindowTitle(QCoreApplication.translate("TagListItem", u"Form", None))
        self.label.setText(QCoreApplication.translate("TagListItem", u"TextLabel", None))
        self.closeButton.setText(QCoreApplication.translate("TagListItem", u"x", None))
    # retranslateUi

