import sys
from pathlib import Path

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
from tagger.tagger import Tagger

class TagRecommendationsWidget(QWidget):
    def __init__(self, manager: QWidget, parent=None) -> None:
        super().__init__(parent)
        self.tagger = Tagger()
        self.tags = []
        self.manager = manager

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        # Scroll area to hold tags
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget(self)
        self.scroll_layout = FlowLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)

    def set_image(self, path: str|Path) -> None:
        if not isinstance(path, Path):
            path = Path(path)
        self.tags = set(self.tagger.tag_image(
            path,
            exclude_tags=self.manager.tag_viewer.tags
        ).keys())
        self.update_tags()

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

            # "+" button to add tag
            add_button = QPushButton("+")
            add_button.setFixedSize(20, 20)
            add_button.clicked.connect(lambda _, t=tag: self.move_tag(t))
            # TODO: You need to signal the manager
            add_button.setStyleSheet("""
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
            tag_layout.addWidget(add_button)

            # Add to the scroll layout
            tag_container = QWidget()
            tag_container.setLayout(tag_layout)
            tag_container.setStyleSheet("""
                background-color: gray;
                color:            black;
                border-radius:    10px;
            """)
            self.scroll_layout.addWidget(tag_container)

    def remove_tag(self, tag) -> None:
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_tags()

    def move_tag(self, tag) -> None:
        self.remove_tag(tag)
        self.manager.tag_viewer.add_tag(tag)
