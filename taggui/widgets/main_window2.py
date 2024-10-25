import sys
from PySide6.QtCore import QRect, QCoreApplication, QMetaObject
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenuBar
from PySide6.QtWidgets import QListWidgetItem

from tag_list import TagList
from tag_list_item import TagListItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        if not self.objectName():
            self.setObjectName(u"MainWindow")
        self.resize(250, 600)

        self.tagList = TagList(self)
        self.setCentralWidget(self.tagList)

        self.menubar = QMenuBar(self)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 250, 22))
        self.setMenuBar(self.menubar)

        for i in range(5):
            item = QListWidgetItem()
            widget = TagListItem(self)
            widget.setText(f"{i}")
            item.setSizeHint(widget.sizeHint())
            self.tagList.addItem(item)
            self.tagList.setItemWidget(item, widget)

        self.setWindowTitle(
            QCoreApplication.translate("MainWindow", u"MainWindow", None)
        )

        QMetaObject.connectSlotsByName(self)

    def removeItem(self, text):
        for row in range(self.tagList.count()):
            item = self.tagList.item(row)
            widget = self.tagList.itemWidget(item)
            if widget.getText() == text:
                self.tagList.takeItem(row)
                return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
