#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTreeView,
    QFileSystemModel,
    QHBoxLayout,
    QMessageBox,
)
from PySide6.QtGui import QKeyEvent, QImageReader, QPixmap
from PySide6.QtCore import Qt, QModelIndex
from PIL import Image
from PIL.ImageQt import ImageQt

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

        # Layouts
        self.main_layout = QHBoxLayout(self.central_widget)
        self.center_widget = QWidget(self.central_widget)
        self.center_layout = QVBoxLayout(self.center_widget)

        # Directory tree view
        self.tree_view = QTreeView(self)
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.tree_view.setModel(self.model)

        # Add tree navigator then the main panel
        self.main_layout.addWidget(self.tree_view)
        self.main_layout.addWidget(self.center_widget)

        # Add image viewer
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.center_layout.addWidget(self.image_label)

        # Tag editor
        self.tag_line_edit = QLineEdit(self)
        self.tag_line_edit.setPlaceholderText("Tags (comma separated)")
        self.center_layout.addWidget(self.tag_line_edit)

        # Description editor
        self.description_line_edit = QLineEdit(self)
        self.description_line_edit.setPlaceholderText("Description")
        self.center_layout.addWidget(self.description_line_edit)

        # self.load_button = QPushButton("Load Tags & Description", self)
        # self.load_button.clicked.connect(self.load_tags_and_description)
        # self.main_layout.addWidget(self.load_button)

        # Save button
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_tags_and_description)
        self.center_layout.addWidget(self.save_button)

        # Start from home directory
        self.tree_view.setRootIndex(self.model.index(os.path.expanduser("~")))
        self.tree_view.clicked.connect(self.on_tree_view_clicked)
        self.tree_view.hideColumn(1)  # Hide size
        self.tree_view.hideColumn(2)  # Hide type
        self.tree_view.hideColumn(3)  # Hide date modified

        self.load_images_in_directory()

    def load_images_in_directory(self):
        # Get image files from the current directory
        if self.current_directory:
            self.image_paths = [
                f for f in os.listdir(self.current_directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
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
                self.tag_line_edit.setText(tags)

        # Load description
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                description = f.read()
                self.description_line_edit.setText(description)

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
            f.write(self.tag_line_edit.text())

        # Save description
        with open(description_file, 'w') as f:
            f.write(self.description_line_edit.text())

        QMessageBox.information(
            self,
            "Success",
            "Tags and description saved successfully!"
        )

    def on_tree_view_clicked(self, index: QModelIndex):
        self.current_directory = self.model.filePath(index)
        self.load_images_in_directory()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Right:
            if self.current_image_index < len(self.image_paths) - 1:
                self.load_image(self.current_image_index + 1)
        elif event.key() == Qt.Key_Left:
            if self.current_image_index > 0:
                self.load_image(self.current_image_index - 1)

    def resizeEvent(self, event):
        # Resize the image widget
        if not self.image_paths:
            return
        self.load_image(self.current_image_index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageTagManager()
    window.show()
    sys.exit(app.exec())
