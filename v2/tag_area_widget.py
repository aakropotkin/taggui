import sys
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QWidget,
    QLabel,
    QPushButton
)

from flow_layout import FlowLayout

class TagAreaWidget(QWidget):
    def __init__(self, tags=[]):
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

    def update_tags(self):
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
            tag_container.setStyleSheet(
                "background-color: gray; color: black; border-radius: 10px;"
            )
            self.scroll_layout.addWidget(tag_container)

    def add_tag(self, tag):
        if not tag in self.tags:
            self.tags.add(tag)
            self.update_tags()

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_tags()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Get active screen
    screen = app.primaryScreen()
    window = TagAreaWidget()
    window.tags = ["foo", "bar", "baz"]
    window.update_tags()
    # Move window to active screen
    geom = screen.geometry()
    x = geom.x() + geom.width() // 2 - window.width() // 2
    y = geom.y() + geom.height() // 2 - window.height() // 2
    window.move(x, y)

    window.show()
    sys.exit(app.exec())
