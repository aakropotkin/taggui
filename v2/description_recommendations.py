import sys
from pathlib import Path

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

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

class Describer():
    def __init__(self) -> None:
        self.processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        self.model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )

    def describe_image(self, image_path: str|Path) -> str:
        if not isinstance(image_path, Path):
            image_path = Path(image_path)
        image = Image.open(image_path)
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=512)
        caption = self.processor.decode(outputs[0], skip_special_tokens=True)
        return caption


class DescriptionRecommendationWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.describer = Describer()
        self.description = ""

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.label = QLabel("Recommended Description")
        self.main_layout.addWidget(self.label)
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.main_layout.addWidget(self.description_text)

    def set_image(self, path: str|Path) -> None:
        if not isinstance(path, Path):
            path = Path(path)
        self.description = self.describer.describe_image(path)
        self.update_description()

    def update_description(self) -> None:
        self.description_text.setPlainText(self.description)
