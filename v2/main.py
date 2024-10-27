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
    QSplitter
)
from PySide6.QtGui import QKeyEvent, QImageReader, QPixmap
from PySide6.QtCore import Qt, QModelIndex, QSize

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
