#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTreeView,
    QFileSystemModel,
    QHBoxLayout,
    QMessageBox,
    QSizePolicy,
    QSplitter,
    QScrollArea,
    QLayout
)
from PySide6.QtGui import QKeyEvent, QImageReader, QPixmap
from PySide6.QtCore import Qt, QModelIndex, QSize, QMargins, QRect, QPoint

class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_list = []
        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QSize(2 * self.contentsMargins().top(),
                      2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QSizePolicy.PushButton,
                QSizePolicy.PushButton,
                Qt.Orientation.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


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
            tag_layout.addWidget(delete_button)

            # Add to the scroll layout
            tag_container = QWidget()
            tag_container.setLayout(tag_layout)
            self.scroll_layout.addWidget(tag_container)

    def add_tag(self, tag):
        if not tag in self.tags:
            self.tags.add(tag)
            self.update_tags()

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_tags()


class ImageTagManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Tag Manager")
        self.setGeometry(100, 100, 800, 600)

        self.current_image_index = 0
        self.image_paths = []
        self.current_directory = ""

        # Central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setSizePolicy(QSizePolicy.Policy.Expanding,
                                          QSizePolicy.Policy.Expanding)

        # Layouts
        self.main_layout = QHBoxLayout(self.central_widget)
        self.center_widget = QWidget(self.central_widget)
        self.center_layout = QVBoxLayout(self.center_widget)
        self.image_nav_widget = QWidget(self.center_widget)
        self.image_nav_layout = QHBoxLayout(self.image_nav_widget)

        # Directory tree view
        self.tree_view = QTreeView(self)
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.tree_view.setModel(self.model)
        # Start from home directory
        self.tree_view.setRootIndex(self.model.index(os.path.expanduser("~")))
        self.tree_view.clicked.connect(self.on_tree_view_clicked)
        self.tree_view.hideColumn(1)  # Hide size
        self.tree_view.hideColumn(2)  # Hide type
        self.tree_view.hideColumn(3)  # Hide date modified
        self.tree_view.setMinimumSize(QSize(50, 50))

        # Add a split between directory tree and center panel
        self.horizontal_split = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.horizontal_split)
        # Add tree navigator then the center panel
        self.horizontal_split.addWidget(self.tree_view)
        self.horizontal_split.setStretchFactor(0, 3)
        self.horizontal_split.addWidget(self.center_widget)
        self.horizontal_split.setStretchFactor(1, 7)

        # Add split between tag editors and image navigation
        self.vertical_split = QSplitter(Qt.Vertical)
        self.center_layout.addWidget(self.vertical_split)

        # Add image viewer
        self.vertical_split.addWidget(self.image_nav_widget)
        self.vertical_split.setStretchFactor(0, 7)
        self.image_nav_widget.setSizePolicy(QSizePolicy.Policy.Expanding,
                                            QSizePolicy.Policy.Expanding)
        self.image_left_button = QPushButton("<", self)
        self.image_left_button.clicked.connect(self.prev_image)
        self.image_left_button.setSizePolicy(QSizePolicy.Minimum,
                                             QSizePolicy.Minimum)
        self.image_right_button = QPushButton(">", self)
        self.image_right_button.clicked.connect(self.next_image)
        self.image_right_button.setSizePolicy(QSizePolicy.Minimum,
                                              QSizePolicy.Minimum)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding,
                                       QSizePolicy.Policy.Expanding)
        self.image_label.setMinimumSize(QSize(100, 100))
        self.image_nav_layout.addWidget(self.image_left_button)
        self.image_nav_layout.addWidget(self.image_label)
        self.image_nav_layout.addWidget(self.image_right_button)

        # Editors panel
        self.editors_widget = QWidget(self)
        self.editors_layout = QVBoxLayout(self.editors_widget)
        self.vertical_split.addWidget(self.editors_widget)

        # Tag editor
        self.tag_edit_label = QLabel(self)
        self.tag_edit_label.setText("Tags")
        self.editors_layout.addWidget(self.tag_edit_label)
        self.tag_edit = QTextEdit(self)
        self.tag_edit.setPlaceholderText("Tags (comma separated)")
        self.tag_edit.setSizePolicy(QSizePolicy.Expanding,
                                    QSizePolicy.Expanding)
        self.editors_layout.addWidget(self.tag_edit)

        # Tag viewer
        self.tag_viewer = TagAreaWidget()
        self.editors_layout.addWidget(self.tag_viewer)


        # Description editor
        self.description_edit_label = QLabel(self)
        self.description_edit_label.setText("Description")
        self.editors_layout.addWidget(self.description_edit_label)
        self.description_edit = QTextEdit(self)
        self.description_edit.setPlaceholderText(
            "A brief paragraph or sentence"
        )
        self.description_edit.setSizePolicy(QSizePolicy.Expanding,
                                            QSizePolicy.Expanding)
        self.editors_layout.addWidget(self.description_edit)

        # Save button
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_tags_and_description)
        self.editors_layout.addWidget(self.save_button)

        self.load_images_in_directory()

    def load_images_in_directory(self):
        # Get image files from the current directory
        if self.current_directory:
            self.image_paths = [
                f for f in os.listdir(
                    self.current_directory
                ) if f.lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
                )
            ]
            self.image_paths.sort()  # Sort images
            if self.image_paths:
                self.load_image(0)

    def load_image(self, index):
        if self.image_paths:
            image_path = os.path.join(
                self.current_directory, self.image_paths[index]
            )
            image_reader = QImageReader(str(image_path))
            image_reader.setAutoTransform(True)
            pixmap = QPixmap.fromImageReader(image_reader)
            pixmap.setDevicePixelRatio(self.devicePixelRatio())
            pixmap = pixmap.scaled(
                self.image_label.size() * pixmap.devicePixelRatio(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
            self.current_image_index = index
            self.load_tags_and_description()

    def load_tags_and_description(self):
        if not self.image_paths:
            return
        current_image_name = self.image_paths[self.current_image_index]
        tags_file = os.path.join(
            self.current_directory,
            f"{os.path.splitext(current_image_name)[0]}.txt"
        )
        description_file = os.path.join(
            self.current_directory,
            f"{os.path.splitext(current_image_name)[0]}.caption"
        )

        # Load tags
        if os.path.exists(tags_file):
            with open(tags_file, 'r') as f:
                tags = f.read()
                self.tag_edit.setText(tags)
                self.tag_viewer.tags = [s for s in tags.split(", ") if s]
                self.tag_viewer.update_tags()

        # Load description
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                description = f.read()
                self.description_edit.setText(description)

    def save_tags_and_description(self):
        if not self.image_paths:
            return
        current_image_name = self.image_paths[self.current_image_index]
        tags_file = os.path.join(
            self.current_directory,
            f"{os.path.splitext(current_image_name)[0]}.txt"
        )
        description_file = os.path.join(
            self.current_directory,
            f"{os.path.splitext(current_image_name)[0]}.caption"
        )

        # Save tags
        with open(tags_file, 'w') as f:
            f.write(self.tag_edit.text())

        # Save description
        with open(description_file, 'w') as f:
            f.write(self.description_edit.text())

        #QMessageBox.information(
        #    self,
        #    "Success",
        #    "Tags and description saved successfully!"
        #)

    def on_tree_view_clicked(self, index: QModelIndex):
        self.current_directory = self.model.filePath(index)
        if not os.path.isdir(self.current_directory):
            self.current_directory = os.path.dirname(self.current_directory)
        self.load_images_in_directory()

    def next_image(self):
        if self.current_image_index < len(self.image_paths) - 1:
            self.load_image(self.current_image_index + 1)

    def prev_image(self):
        if self.current_image_index > 0:
            self.load_image(self.current_image_index - 1)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Right:
            self.next_image()
        elif event.key() == Qt.Key_Left:
            self.prev_image()

    # TODO: This needs to be pushed down into the image nav widget.
    # Currently resizing panels won't trigger image resizing.
    def resizeEvent(self, event):
        # Resize the image widget
        if not self.image_paths:
            return
        self.load_image(self.current_image_index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Get active screen
    screen = app.primaryScreen()
    window = ImageTagManager()
    # Move window to active screen
    geom = screen.geometry()
    x = geom.x() + geom.width() // 2 - window.width() // 2
    y = geom.y() + geom.height() // 2 - window.height() // 2
    window.move(x, y)

    window.show()
    sys.exit(app.exec())
