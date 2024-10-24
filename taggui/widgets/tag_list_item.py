from PySide6.QtWidgets import QWidget

from ui_tag_list_item import Ui_TagListItem

class TagListItem(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_TagListItem()
        self.ui.setupUi(self)
        self.ui.closeButton.clicked.connect(self.closeButtonClicked)

    def setText(self, text):
        self.ui.label.setText(text)

    def getText(self):
        return self.ui.label.text()

    def closeButtonClicked(self):
        self.parent.removeItem(self.getText())
