import sys

from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit
)

from flow_layout import FlowLayout
from util import deduplicate_list

class TagAreaWidget(QWidget):
    def __init__(self, tags=[]) -> None:
        super().__init__()
        self.tags = tags

        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Scroll area to hold tags
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget(self)
        self.scroll_layout = FlowLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)

        # Text edit for editing tags as text
        self.text_edit = QTextEdit()
        self.text_edit.setVisible(False) # Initially hidden
        self.main_layout.addWidget(self.text_edit)

        # Mode toggle button
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        self.main_layout.addWidget(self.edit_button)

    def update_tags(self) -> None:
        # Clear existing tags
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Add tags with delete button
        for tag in self.tags:
            tag_layout = QHBoxLayout()

            # Tag label
            tag_label = QLabel(tag)
            tag_layout.addWidget(tag_label)

            # "X" button to delete tag
            delete_button = QPushButton("X")
            delete_button.setFixedSize(20, 20)
            delete_button.clicked.connect(lambda _, t=tag: self.remove_tag(t))
            delete_button.setStyleSheet("""
              QPushButton {
                border: 1px solid black;
                border-radius: 5px;
              }
              QPushButton:hover {
                background-color: dimgray
              }
              QPushButton:pressed {
                background-color: white
              }
            """)
            tag_layout.addWidget(delete_button)

            # Add to the scroll layout
            tag_container = QWidget()
            tag_container.setLayout(tag_layout)
            tag_container.setStyleSheet("""
                background-color: gray;
                color:            black;
                border-radius:    10px;
            """)
            self.scroll_layout.addWidget(tag_container)

    def add_tag(self, tag) -> None:
        if not tag in self.tags:
            self.tags.add(tag)
            self.update_tags()

    def remove_tag(self, tag) -> None:
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_tags()

    def toggle_edit_mode(self) -> None:
        if self.text_edit.isVisible():
            # Save changes and switch back to tag view
            new_tags = self.text_edit.toPlainText().split(', ')
            new_tags = [tag.strip() for tag in new_tags if tag.strip()]
            self.tags = deduplicate_list(new_tags)
            self.update_tags()
            self.text_edit.setVisible(False)
            self.scroll_area.setVisible(True)
            self.edit_button.setText("Edit")
        else:
            # Switch to text edit mode
            tag_string = ', '.join(self.tags)
            self.text_edit.setPlainText(tag_string)
            self.text_edit.setVisible(True)
            self.scroll_area.setVisible(False)
            self.edit_button.setText("Done")

    def toPlainText(self) -> str:
        if self.text_edit.isVisible():
            return self.text_edit.toPlainText()
        else:
            return ', '.join(self.tags)

    def setTags(self, tags) -> None:
        self.tags = tags
        self.update_tags()
        self.text_edit.setPlainText(', '.join(self.tags))

    def setText(self, tag_string) -> None:
        new_tags = tag_string.split(', ')
        new_tags = [tag.strip() for tag in new_tags if tag.strip()]
        self.tags = deduplicate_list(new_tags)
        self.update_tags()
        self.text_edit.setPlainText(tag_string)
