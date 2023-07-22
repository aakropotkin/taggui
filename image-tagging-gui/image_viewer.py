from pathlib import Path

from PySide6.QtCore import QModelIndex, QSize, Qt, Slot
from PySide6.QtGui import QPixmap, QResizeEvent
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from image import Image
from image_list_model import ImageListModel


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # This allows the label to shrink.
        self.setMinimumSize(QSize(1, 1))

    def resizeEvent(self, event: QResizeEvent):
        """Reload the image whenever the label is resized."""
        if self.image_path:
            self.load_image(self.image_path)

    def load_image(self, image_path: Path):
        self.image_path = image_path
        # `SmoothTransformation` is higher quality than the default
        # `FastTransformation`.
        pixmap = QPixmap(str(image_path)).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)


class ImageViewer(QWidget):
    def __init__(self, image_list_model: ImageListModel):
        super().__init__()
        self.image_list_model = image_list_model
        self.image_label = ImageLabel()
        QVBoxLayout(self).addWidget(self.image_label)

    @Slot()
    def load_image(self, index: QModelIndex):
        image: Image = self.image_list_model.data(index, Qt.UserRole)
        self.image_label.load_image(image.path)