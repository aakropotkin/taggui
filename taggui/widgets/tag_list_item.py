from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtWidgets import QSpacerItem, QToolButton

class TagListItem(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        if not self.objectName():
            self.setObjectName(u"Tag")
        self.resize(250, 60)

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.label = QLabel(self)
        self.label.setObjectName(u"label")
        self.horizontalLayout.addWidget(self.label)
        self.label.setText(
            QCoreApplication.translate("TagListItem", u"TextLabel", None)
        )

        self.horizontalSpacer = QSpacerItem(
            40, 20,
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.deleteButton = QToolButton(self)
        self.deleteButton.setObjectName(u"deleteButton")
        self.horizontalLayout.addWidget(self.deleteButton)
        self.deleteButton.setText(
            QCoreApplication.translate("TagListItem", u"x", None)
        )
        self.deleteButton.clicked.connect(self.deleteButtonClicked)

        self.setWindowTitle(
            QCoreApplication.translate("TagListItem", u"Form", None)
        )

        QMetaObject.connectSlotsByName(self)

    def setText(self, text):
        self.label.setText(text)

    def getText(self):
        return self.label.text()

    def deleteButtonClicked(self):
        self.parent.removeItem(self.getText())
