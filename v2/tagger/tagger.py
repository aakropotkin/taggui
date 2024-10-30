import sys
import json
from typing import Generator, Iterable
from tagger.interrogator import Interrogator
from PIL import Image
from pathlib import Path

from tagger.interrogators import interrogators

def escape_tag(tag: str) -> str:
    return tag.replace(' ', '_').replace('\(', '(').replace('\)', ')')

def add_escaped_tags(tags: Iterable[str]) -> set[str]:
    reverse_escaped_tags = []
    for tag in tags:
        reverse_escaped_tags.append(escape_tag(tag))
    return set([*tags, *reverse_escaped_tags])

class Tagger():
    def __init__(
            self,
            interrogator: str = 'wd14-convnextv2.v1',
            use_cpu: bool = False
    ):
        self.interrogator = interrogators[interrogator]
        if use_cpu:
            self.interrogator.use_cpu()

    def tag_image(
            self,
            image_path: Path,
            threshold: float = 0.35,
            tag_escape: bool = True,
            exclude_tags: Iterable[str] = []
    ) -> dict[str, float]:
        """
        Predictions from a image path
        """
        im = Image.open(image_path)
        result = self.interrogator.interrogate(im)

        excludes = []
        if tag_escape:
            excludes = add_escaped_tags(exclude_tags)
        else:
            excludes = exclude_tags

        return Interrogator.postprocess_tags(
            result[1],
            threshold=threshold,
            escape_tag=tag_escape,
            replace_underscore=tag_escape,
            exclude_tags=excludes
        )

if __name__ == "__main__":
    tagger = Tagger()
    tags = tagger.tag_image(Path(sys.argv[1]))
    print(json.dumps(tags, indent=2))
