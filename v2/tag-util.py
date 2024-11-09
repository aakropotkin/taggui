# ============================================================================ #
#
# Provides utilities for filtering out redundant tags from recommendations.
# For example if the user has already tagged an image with "blue eyes", the
# recommendation widget should not suggest "green eyes" as a tag.
#
#
# ---------------------------------------------------------------------------- #

hair_lengths = {
    "very short hair",
    "short hair",
    "medium hair",
    "long hair",
    "very long hair",
    "absurdly long hair",
    "big hair",
    "bald"
}

def has_hair_length(tags: list[str]) -> bool:
    return bool(hair_lengths & set(tags))

def filter_redundant_hair_lengths(
        tags: list[str],
        recommendations: set[str]
) -> set[str]:
    if has_hair_length(tags):
        return recommendations - hair_lengths
    return recommendations


# NOTE: If `multicolored hair' is present we allow multiple hair colors.
hair_colors = {
    "aqua hair",
    "black hair",
    "blonde hair",
    "blue hair",
    "light blue hair",
    "dark blue hair",
    "brown hair",
    "light brown hair",
    "green hair",
    "dark green hair",
    "grey hair",
    "orange hair",
    "pink hair",
    "purple hair",
    "light purple hair",
    "red hair",
    "white hair"
}

def has_hair_color(tags: list[str]) -> bool:
    return bool(hair_colors & set(tags))

def filter_redundant_hair_colors(
        tags: list[str],
        recommendations: set[str]
) -> set[str]:
    if has_hair_color(tags):
        if "multicolored hair" in tags:
            return recommendations
        return recommendations - hair_colors
    return recommendations


hair_styles = {
    "bob cut",
    "inverted bob",
    "bowl cut",
    "buzz cut",
    "chonmage",
    "crew cut",
    "flattop",
    "okappa",
    "pixie cut",
    "undercut",
    "flipped hair",
    "wolf cut",
    "hime cut",
    "mullet",
    "bantu knots",
    "bow-shaped hair",
    "shuangyaji",
    "braid",
    "braided bangs",
    "front braid",
    "side braid",
    "french braid",
    "cornrows",
    "crown braid",
    "dreadlocks",
    "single braid",
    "multiple braids",
    "twin braids",
    "low twin braids",
    "tri braids",
    "quad braids",
    "flower-shaped hair",
    "hair bun",
    "braided bun",
    "single hair bun",
    "double bun",
    "cone hair bun",
    "doughnut hair bun",
    "heart hair bun",
    "triple bun",
    "cone hair bun",
    "hair rings",
    "feixianji",
    "katsuyamamage",
    "single hair ring",
    "half updo",
    "half up braid",
    "half up half down braid",
    "one side up",
    "two side up",
    "low-braided long hair",
    "low-tied long hair",
    "mizura",
    "multi-tied hair",
    "nihongami",
    "ponytail",
    "folded ponytail",
    "front ponytail",
    "high ponytail",
    "short ponytail",
    "side ponytail",
    "split ponytail",
    "star-shaped hair",
    "topknot",
    "twintails",
    "low twintails",
    "short twintails",
    "uneven twintails",
    "tri tails",
    "quad tails",
    "quin tails",
    "twisted hair",
    "afro",
    "huge afro",
    "beehive hairdo",
    "crested hair",
    "liangbatou",
    "pompadour",
    "quiff"
}

def has_hair_style(tags: list[str]) -> bool:
    return bool(hair_styles & set(tags))

def filter_redundant_hair_styles(
        tags: list[str],
        recommendations: set[str]
) -> set[str]:
    if has_hair_style(tags):
        return recommendations - hair_styles
    return recommendations


# ---------------------------------------------------------------------------- #

eye_colors = {
    "aqua eyes",
    "black eyes",
    "blue eyes",
    "brown eyes",
    "green eyes",
    "grey eyes",
    "orange eyes",
    "purple eyes",
    "pink eyes",
    "red eyes",
    "white eyes",
    "yellow eyes",
    "amber eyes",
    "heterochromia",
    "multicolored eyes"
}

def has_eye_color(tags: list[str]) -> bool:
    return bool(eye_colors & set(tags))

# NOTE: If `multicolored eyes' is present we allow multiple eye colors.
def filter_redundant_eye_colors(
        tags: list[str],
        recommendations: set[str]
) -> set[str]:
    if has_eye_color(tags):
        if "multicolored eyes" in tags:
            return recommendations
        return recommendations - eye_colors
    return recommendations


# ---------------------------------------------------------------------------- #

breast_sizes = {
    "flat chest",
    "small breasts",
    "medium breasts",
    "large breasts",
    "huge breasts",
    "gigantic breasts"
}

def has_breast_size(tags: list[str]) -> bool:
    return bool(breast_sizes & set(tags))

def filter_redundant_breast_sizes(
        tags: list[str],
        recommendations: set[str]
) -> set[str]:
    if has_breast_size(tags):
        return recommendations - breast_sizes
    return recommendations


# ---------------------------------------------------------------------------- #

background_colors = {
    "aqua background",
    "black background",
    "blue background",
    "brown background",
    "green background",
    "grey background",
    "light brown background",
    "orange background",
    "pink background",
    "purple background",
    "red background",
    "white background",
    "yellow background"
}

backgrounds = background_colors | {
    "simple background",
    "gradient background"
}

def has_background(tags: list[str]) -> bool:
    return bool(backgrounds & set(tags))

# NOTE: If `gradient' is present we allow multiple background colors.
# NOTE: If any colors are present in recommendations we don't allow
#       "simple background".
def filter_redundant_backgrounds(
        tags: list[str],
        recommendations: set[str]
) -> set[str]:
    if background_colors & recommendations:
        recommendations = recommendations - { "simple background" }
    if has_background(tags):
        if "gradient background" in tags:
            return recommendations
        return recommendations - backgrounds
    return recommendations


# ---------------------------------------------------------------------------- #

def filter_redundant_recommendations(
        tags: list[str],
        recommendations: set[str]
) -> set[str]:
    recommendations = recommendations - set(tags)
    recommendations = filter_redundant_hair_lengths(tags, recommendations)
    recommendations = filter_redundant_hair_colors(tags, recommendations)
    recommendations = filter_redundant_hair_styles(tags, recommendations)
    recommendations = filter_redundant_eye_colors(tags, recommendations)
    recommendations = filter_redundant_breast_sizes(tags, recommendations)
    recommendations = filter_redundant_backgrounds(tags, recommendations)
    return recommendations


# ---------------------------------------------------------------------------- #
#
#
#
# ============================================================================ #
