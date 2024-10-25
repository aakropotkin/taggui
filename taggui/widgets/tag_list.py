from PySide6.QtCore import QMetaObject
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtWidgets import QSpacerItem, QToolButton, QListWidget

class TagList(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"TagList")
        self.resize(250, 400)

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.listWidget = QListWidget(self)
        self.listWidget.setObjectName(u"listWidget")
        self.horizontalLayout.addWidget(self.listWidget)

        QMetaObject.connectSlotsByName(self)

    def addItem(self, item):
        self.listWidget.addItem(item)

    def setItemWidget(self, item, widget):
        self.listWidget.setItemWidget(item, widget)

    def count(self):
        return self.listWidget.count()

    def item(self, row):
        return self.listWidget.item(row)

    def itemWidget(self, item):
        return self.listWidget.itemWidget(item)

    def takeItem(self, row):
        self.listWidget.takeItem(row)
