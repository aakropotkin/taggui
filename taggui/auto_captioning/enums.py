from enum import Enum, auto


# `StrEnum` is a Python 3.11 feature that can be used here.
class CaptionPosition(str, Enum):
    BEFORE_FIRST_TAG = 'Insert before first tag'
    AFTER_LAST_TAG = 'Insert after last tag'
    OVERWRITE_FIRST_TAG = 'Overwrite first tag'
    OVERWRITE_ALL_TAGS = 'Overwrite all tags'
    DO_NOT_ADD = 'Do not add to tags'


class Device(str, Enum):
    GPU = 'GPU if available'
    CPU = 'CPU'


class ModelType(Enum):
    COGAGENT = auto()
    COGVLM = auto()
    KOSMOS = auto()
    LLAVA = auto()
    MOONDREAM = auto()
    WD_TAGGER = auto()
    XCOMPOSER2 = auto()
    OTHER = auto()
