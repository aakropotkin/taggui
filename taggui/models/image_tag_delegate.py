from PySide6.QtCore import QEvent, QItemSelectionModel, Qt
from PySide6.QtWidgets import QFrame, QPlainTextEdit, QStyledItemDelegate

class ImageTagDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        tag = index.data()
        self.textRect = option.rect.adjusted(
            0,
            0,
            (option.rect.width() / 5) * 4,
            0
        )
        self.buttonRect = option.rect.adjusted(
            (option.rect.width() / 5) * 4,
            0,
            0,
            0
        )
        painter.drawText(self.textRect, Qt.AlignLeft, tag)
        painter.fillRect(self.buttonRect, Qt.lightGray)
        painter.drawText(self.buttonRect, Qt.AlignCenter, u"X")

    def createEditor(self, parent, option, index):
        editor = QPlainTextEdit(parent)
        editor.setFrameStyle(QFrame.Shape.NoFrame)
        editor.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        editor.setStyleSheet('padding-left: 3px;')
        editor.index = index
        return editor

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(size.height() + 8)
        return size

    def eventFilter(self, editor, event: QEvent):
        if (event.type() == QEvent.KeyPress
                and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)):
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)
            self.parent().setCurrentIndex(
                self.parent().model().index(editor.index.row(), 0))
            self.parent().selectionModel().select(
                self.parent().model().index(editor.index.row(), 0),
                QItemSelectionModel.SelectionFlag.ClearAndSelect)
            self.parent().setFocus()
            return True
        # This is required to prevent crashing when the user clicks on another
        # tag in the All Tags list.
        if event.type() == QEvent.FocusOut:
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)
            return True
        return False
