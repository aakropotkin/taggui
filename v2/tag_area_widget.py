import sys

from PySide6.QtCore import QObject
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
    def __init__(self, tags: list[str] = [], parent: QObject = None) -> None:
        super().__init__(parent)
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

        self.update_tags()

    def update_tags(self) -> None:
        """Refreshes tag display in tag view mode"""
        # Clear existing tags
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
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
        """Adds a single tag if it doesn't already exist."""
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.update_tags()
            self._update_text_edit()

    def remove_tag(self, tag) -> None:
        """Removes a tag if it exists."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_tags()
            self._update_text_edit()

    def toggle_edit_mode(self) -> None:
        """Toggles between tag display and text edit modes."""
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
        """Return a comma-separated string of tags."""
        if self.text_edit.isVisible():
            return self.text_edit.toPlainText()
        else:
            return ', '.join(self.tags)

    def setTags(self, tags: list[str]) -> None:
        """Set tags directly from a list."""
        self.tags = deduplicate_list(tags)
        self.update_tags()
        self._update_text_edit()

    def setText(self, tag_string: str) -> None:
        """Set tags from a comma-separated string, handling duplicates."""
        new_tags = [tag.strip() for tag in tag_string.split(',') if tag.strip()]
        self.tags = deduplicate_list(new_tags)
        self.update_tags()
        self._update_text_edit()

    def _update_text_edit(self) -> None:
        """Update the text edit widget with the current tags."""
        self.text_edit.setPlainText(', '.join(self.tags))
