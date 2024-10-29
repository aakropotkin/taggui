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
    QInputDialog
)
from PySide6.QtGui import QKeyEvent, QImageReader, QPixmap
from PySide6.QtCore import (
    Qt,
    QModelIndex,
    QSize,
    QMargins,
    QRect,
    QPoint,
    QEvent
)
from tag_area_widget import TagAreaWidget

class MainImageLabel(QLabel):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.setMinimumSize(QSize(100, 100))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.manager.image_paths:
            return
        self.manager.load_image(self.manager.current_image_index)


class IndexLabel(QLabel):
    # TODO: use this instead of passing in `manager'
    #indexChanged = Signal(int)

    def __init__(self, manager, parent=None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.update_text()

    def index(self) -> int:
        if not self.manager.image_paths:
            return None
        return self.manager.current_image_index

    def count(self) -> int:
        if not self.manager.image_paths:
            return 0
        return len(self.manager.image_paths)

    def update_text(self) -> None:
        if self.index() == None:
            self.setText("")
        else:
            self.setText(f"{self.index()}/{self.count()}")

    def mousePressEvent(self, event: QEvent) -> None:
        if ( self.index() != None ) and ( event.button() == Qt.LeftButton ):
            self.prompt_for_index()

    def prompt_for_index(self) -> None:
        # Open an input dialog to get a new index from the user
        new_index, ok = QInputDialog.getInt(
            self,
            "Jump to Index",
            f"Enter a number between 0 and {self.count() - 1}",
            value=self.index(),
            minValue=0,
            maxValue=self.count() - 1
        )
        if ok and ( 0 <= new_index < self.count() ):
            self.manager.load_image(new_index)
            self.update_text()
            # TODO: User this instead of using `manager'
            #self.indexChanged.emit(self.current_index)  # Emit the new index


class ImageNavigationWidget(QWidget):
    def __init__(self, manager, parent=None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.vertical_layout = QVBoxLayout(self)
        self.image_title = QLabel(self)
        self.image_title.setAlignment(Qt.AlignCenter)
        self.image_index = IndexLabel(manager, self)
        self.image_index.setAlignment(Qt.AlignRight)

        self.vertical_layout.addWidget(self.image_title)
        self.vertical_layout.addWidget(self.image_index)

        self.image_nav_widget = QWidget(self)
        self.image_nav_widget.setSizePolicy(QSizePolicy.Policy.Expanding,
                                            QSizePolicy.Policy.Expanding)
        self.image_nav_layout = QHBoxLayout(self.image_nav_widget)
        self.vertical_layout.addWidget(self.image_nav_widget)

        self.image_left_button = QPushButton("<", self)
        self.image_left_button.clicked.connect(manager.prev_image)
        self.image_left_button.setSizePolicy(QSizePolicy.Minimum,
                                             QSizePolicy.Minimum)

        self.image_right_button = QPushButton(">", self)
        self.image_right_button.clicked.connect(manager.next_image)
        self.image_right_button.setSizePolicy(QSizePolicy.Minimum,
                                              QSizePolicy.Minimum)

        self.image_label = MainImageLabel(self.manager, self)
        self.image_nav_layout.addWidget(self.image_left_button)
        self.image_nav_layout.addWidget(self.image_label)
        self.image_nav_layout.addWidget(self.image_right_button)


class ImageTagManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Tag Manager")
        self.setGeometry(100, 100, 1500, 1000)

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
        self.horizontal_split.setStretchFactor(0, 1.5)
        self.horizontal_split.addWidget(self.center_widget)
        self.horizontal_split.setStretchFactor(1, 8.5)

        # Add split between tag editors and image navigation
        self.vertical_split = QSplitter(Qt.Vertical)
        self.center_layout.addWidget(self.vertical_split)

        # Add image viewer
        self.image_nav = ImageNavigationWidget(self, self)
        self.vertical_split.addWidget(self.image_nav)

        # Editors panel
        self.editors_widget = QWidget(self)
        self.editors_layout = QVBoxLayout(self.editors_widget)
        self.vertical_split.addWidget(self.editors_widget)
        self.vertical_split.setStretchFactor(0, 8)  # Image
        self.vertical_split.setStretchFactor(1, 2)  # Editors

        # Tag viewer
        self.tag_edit_label = QLabel(self)
        self.tag_edit_label.setText("Tags")
        self.editors_layout.addWidget(self.tag_edit_label)
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
        cancel = self.prompt_for_save_if_dirty()
        if cancel:
            return
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
                self.image_nav.image_label.size() * pixmap.devicePixelRatio(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_nav.image_label.setPixmap(pixmap)
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
                tags = f.replace("\n", " ").read().strip()
                self.tag_viewer.setText(tags)

        # Load description
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                description = f.read().replace("\n", " ").strip()
                self.description_edit.setText(description)

        # Set image title and index
        self.image_nav.image_title.setText(current_image_name)
        self.image_nav.image_index.update_text()

    def is_dirty(self):
        if not self.image_paths:
            return False

        current_image_name = self.image_paths[self.current_image_index]
        tags_file = os.path.join(
            self.current_directory,
            f"{os.path.splitext(current_image_name)[0]}.txt"
        )
        if os.path.exists(tags_file):
            with open(tags_file, 'r') as f:
                tags = f.read().strip()
                have_tags = self.tag_viewer.toPlainText().replace("\n", " ")
                have_tags = have_tags.strip()
                if tags != have_tags:
                    return True
        elif self.tag_viewer.toPlainText().replace("\n", " ").strip() != "":
            return True

        description_file = os.path.join(
            self.current_directory,
            f"{os.path.splitext(current_image_name)[0]}.caption"
        )
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                description = f.read().strip()
                have_description = self.description_edit.toPlainText()
                have_description = have_description.replace("\n", " ").strip()
                return have_description != description
        else:
            have_description = self.description_edit.toPlainText()
            have_description = have_description.replace("\n", " ").strip()
            return have_description != ""

    def prompt_for_save_if_dirty(self):
        "Returns True if the user wants to cancel an action"
        if not self.is_dirty():
            return False
        reply = QMessageBox.question(
            self,
            "Save",
            "You have unsaved edits, would you like to save them?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Cancel  # Default
        )
        if reply == QMessageBox.Cancel:
            return True
        if reply == QMessageBox.Yes:
            self.save_tags_and_description()
        return False


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
            f.write(self.tag_viewer.toPlainText())
        # Save description
        with open(description_file, 'w') as f:
            f.write(self.description_edit.toPlainText())

    def on_tree_view_clicked(self, index: QModelIndex):
        cancel = self.prompt_for_save_if_dirty()
        if cancel:
            return
        self.current_directory = self.model.filePath(index)
        if not os.path.isdir(self.current_directory):
            self.current_directory = os.path.dirname(self.current_directory)
        self.load_images_in_directory()

    def next_image(self):
        cancel = self.prompt_for_save_if_dirty()
        if cancel:
            return
        if self.current_image_index < len(self.image_paths) - 1:
            self.load_image(self.current_image_index + 1)

    def prev_image(self):
        cancel = self.prompt_for_save_if_dirty()
        if cancel:
            return
        if self.current_image_index > 0:
            self.load_image(self.current_image_index - 1)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Right:
            self.next_image()
        elif event.key() == Qt.Key_Left:
            self.prev_image()
        elif event.key == Qt.Key_S and (
                event.modifiers() == Qt.ControlModifier
        ):
            self.save_tags_and_description


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
