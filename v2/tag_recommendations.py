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
    QTextEdit,
    QSizePolicy
)

from flow_layout import FlowLayout
from tagger.tagger import Tagger


class TagRecommendation(QWidget):
    def __init__(
            self,
            tag: str,
            parent: QWidget,
            weight: float = 0.5
    ) -> None:
        super().__init__(parent)
        self.tag = tag
        self.weight = weight

        self.setStyleSheet("""
            background-color: gray;
            color:            black;
            border-radius:    10px;
            padding:          5px;
        """)
        self.setFixedHeight(50)

        self.layout = QHBoxLayout(self)

        self.label = QLabel(tag)
        self.layout.addWidget(self.label)

        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(20, 20)
        self.add_button.clicked.connect(
            lambda _, t=tag: self.parent().move_tag(t)
        )
        self.add_button.setStyleSheet("""
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
        self.layout.addWidget(self.add_button)

class TagRecommendationsWidget(QWidget):
    def __init__(self, manager: QWidget, parent=None) -> None:
        super().__init__(parent)
        self.tagger = Tagger()
        self.tags = []
        self.manager = manager

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.label = QLabel("Recommended Tags")
        self.main_layout.addWidget(self.label)
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
            tag_container = TagRecommendation(tag, self)
            self.scroll_layout.addWidget(tag_container)

    def remove_tag(self, tag) -> None:
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_tags()

    def move_tag(self, tag) -> None:
        self.remove_tag(tag)
        self.manager.tag_viewer.add_tag(tag)
