#!/usr/bin/env python3
import sys
import os
from pathlib import Path
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
    QEvent,
    QDir,
    QObject
)
from tag_area_widget import TagAreaWidget
from recommendations import TagRecommendationsWidget

class MainImageLabel(QLabel):
    def __init__(self, manager: QWidget, parent=None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.setMinimumSize(QSize(100, 100))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self.manager.image_paths:
            return
        self.manager.load_image(self.manager.current_image_index)


class IndexLabel(QWidget):
    # TODO: use this instead of passing in `manager'
    #indexChanged = Signal(int)

    def __init__(self, manager: QWidget, parent=None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)

        self.label = QLabel(self)
        self.layout.addWidget(self.label)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setMaximumSize(100, 25)
        self.delete_button.clicked.connect(self.delete_image)
        self.layout.addWidget(self.delete_button)

        self.jump_button = QPushButton("Jump To")
        self.jump_button.setMaximumSize(100, 25)
        self.jump_button.clicked.connect(self.prompt_for_index)
        self.layout.addWidget(self.jump_button)

        self.update_text()

    def index(self) -> int:
        if not self.manager.image_paths:
            return None
        return self.manager.current_image_index + 1

    def count(self) -> int:
        if not self.manager.image_paths:
            return 0
        return len(self.manager.image_paths)

    def update_text(self) -> None:
        if self.index() == None:
            self.label.setText("")
        else:
            self.label.setText(f"{self.index()}/{self.count()}")

    def delete_image(self) -> None:
        if self.index() == None:
            return

        current_image_name = self.manager.image_paths[
            self.manager.current_image_index
        ]
        img_path = Path(self.manager.current_directory) / current_image_name
        if img_path.is_file():
            img_path.unlink()

        base_path = os.path.join(
            self.manager.current_directory,
            os.path.splitext(current_image_name)[0]
        )
        tag_path = Path( base_path + ".txt" )
        if tag_path.is_file():
            tag_path.unlink()

        caption_path = Path( base_path + ".caption" )
        if caption_path.is_file():
            caption_path.unlink()

        del self.manager.image_paths[self.index() - 1]
        self.manager.load_image(self.index() - 1)
        self.update_text()  # Refresh `count'

    def prompt_for_index(self) -> None:
        if self.index() == None:
            return
        # Open an input dialog to get a new index from the user
        new_index, ok = QInputDialog.getInt(
            self,
            "Jump to Index",
            f"Enter a number between 1 and {self.count()}",
            value=self.index(),
            minValue=1,
            maxValue=self.count()
        )
        if ok and ( 0 < new_index <= self.count() ):
            self.manager.load_image(new_index - 1)
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
        #self.image_index.setAlignment(Qt.AlignRight)

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


class ImageFileSystemModel(QFileSystemModel):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)
        self.setNameFilters(["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp"])
        self.setNameFilterDisables(False)  # Enable filtering


class ImageTagManager(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Image Tag Manager")
        self.setGeometry(100, 100, 1800, 1000)

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
        self.tree_view.setSortingEnabled(False)
        self.model = ImageFileSystemModel(self)
        self.model.setRootPath("")
        self.tree_view.setModel(self.model)
        # Start from home directory
        self.tree_view.setRootIndex(self.model.index(os.path.expanduser("~")))
        self.tree_view.selectionModel().currentChanged.connect(
            self.on_tree_view_changed
        )
        self.tree_view.hideColumn(1)  # Hide size
        self.tree_view.hideColumn(2)  # Hide type
        self.tree_view.hideColumn(3)  # Hide date modified
        self.tree_view.setMinimumSize(QSize(50, 50))

        # Add a split between directory tree and center panel
        self.horizontal_split = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.horizontal_split)
        # Add tree navigator then the center panel
        self.horizontal_split.addWidget(self.tree_view)
        self.horizontal_split.addWidget(self.center_widget)

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
        self.vertical_split.setStretchFactor(0, 6)  # Image
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

        # Tag Recommendations
        self.recommendations = TagRecommendationsWidget(self, self)
        self.recommendations.setMinimumSize(QSize(300, 50))
        self.horizontal_split.addWidget(self.recommendations)

        # Set Horizontal stretch
        self.horizontal_split.setStretchFactor(0, 2)
        self.horizontal_split.setStretchFactor(1, 6)
        self.horizontal_split.setStretchFactor(2, 2)

        self.load_images_in_directory()

    def load_images_in_directory(self) -> None:
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

    def load_image(self, index: int) -> None:
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

    def load_tags_and_description(self) -> None:
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
                tags = f.read().replace("\n", " ").strip()
                self.tag_viewer.setText(tags)

        # Load description
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                description = f.read().replace("\n", " ").strip()
                self.description_edit.setText(description)

        # Set image title and index
        self.image_nav.image_title.setText(current_image_name)
        self.image_nav.image_index.update_text()

        # Load recommendations
        self.recommendations.set_image(
            os.path.join(self.current_directory, current_image_name)
        )

    def is_dirty(self) -> bool:
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

    def prompt_for_save_if_dirty(self) -> bool:
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

    def save_tags_and_description(self) -> None:
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
            f.write(
                self.description_edit.toPlainText().replace('\n', ' ').strip()
            )

    def on_tree_view_changed(self, index: QModelIndex) -> None:
        cancel = self.prompt_for_save_if_dirty()
        if cancel:
            return
        f = self.model.filePath(index)
        if os.path.isdir(f):
            self.current_directory = f
            self.load_images_in_directory()
        else:
            if str(f).lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
            ):
                self.current_directory = os.path.dirname(f)
                self.load_images_in_directory()
                # Set index accordingly
                idx = 0
                for img in self.image_paths:
                    if os.path.basename(img) == os.path.basename(f):
                        self.load_image(idx)
                        break
                    idx = idx + 1

    def next_image(self) -> None:
        cancel = self.prompt_for_save_if_dirty()
        if cancel:
            return
        if self.current_image_index < len(self.image_paths) - 1:
            self.load_image(self.current_image_index + 1)

    def prev_image(self) -> None:
        cancel = self.prompt_for_save_if_dirty()
        if cancel:
            return
        if self.current_image_index > 0:
            self.load_image(self.current_image_index - 1)

    def keyPressEvent(self, event: QKeyEvent) -> None:
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
