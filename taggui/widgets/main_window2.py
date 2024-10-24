import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtWidgets import QListWidgetItem

from ui_main_window import Ui_MainWindow
from tag_list_item import TagListItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        for i in range(5):
            item = QListWidgetItem()
            widget = TagListItem(self)
            widget.setText(f"{i}")
            item.setSizeHint(widget.sizeHint())
            self.ui.listWidget.addItem(item)
            self.ui.listWidget.setItemWidget(item, widget)

    def removeItem(self, text):
        for row in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(row)
            widget = self.ui.listWidget.itemWidget(item)
            if widget.getText() == text:
                self.ui.listWidget.takeItem(row)
                return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
