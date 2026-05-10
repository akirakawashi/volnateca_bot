import re
from dataclasses import dataclass
from functools import cache
from re import Pattern


@dataclass(slots=True, frozen=True, kw_only=True)
class VKPostTaskMarkerRules:
    marker: str = "#volnateca"
    default_repost_points: int = 20
    default_like_points: int = 10
    max_description_length: int = 500


@dataclass(slots=True, frozen=True, kw_only=True)
class ParsedVKPostMarker:
    repost_points: int
    like_points: int
    week_number: int | None


@dataclass(slots=True, frozen=True, kw_only=True)
class VKPostTaskMarkerPatterns:
    marker: Pattern[str]
    repost_points: Pattern[str]
    like_points: Pattern[str]
    week: Pattern[str]


@dataclass(slots=True, frozen=True, kw_only=True)
class VKPostTaskMarkerParser:
    rules: VKPostTaskMarkerRules
    patterns: VKPostTaskMarkerPatterns

    @classmethod
    def from_rules(cls, rules: VKPostTaskMarkerRules) -> "VKPostTaskMarkerParser":
        escaped_marker = re.escape(rules.marker)
        return cls(
            rules=rules,
            patterns=VKPostTaskMarkerPatterns(
                marker=re.compile(rf"{escaped_marker}(?!_\w)", re.IGNORECASE),
                repost_points=re.compile(
                    rf"{escaped_marker}_repost_points_(?P<points>\d+)",
                    re.IGNORECASE,
                ),
                like_points=re.compile(
                    rf"{escaped_marker}_like_points_(?P<points>\d+)",
                    re.IGNORECASE,
                ),
                week=re.compile(rf"{escaped_marker}_week_(?P<week>\d+)", re.IGNORECASE),
            ),
        )

    def parse(self, *, text: str) -> ParsedVKPostMarker | None:
        if not self.patterns.marker.search(text):
            return None

        repost_points = self.rules.default_repost_points
        repost_match = self.patterns.repost_points.search(text)
        if repost_match is not None:
            repost_points = int(repost_match.group("points"))

        like_points = self.rules.default_like_points
        like_match = self.patterns.like_points.search(text)
        if like_match is not None:
            like_points = int(like_match.group("points"))

        week_number = None
        week_match = self.patterns.week.search(text)
        if week_match is not None:
            week_number = int(week_match.group("week"))

        return ParsedVKPostMarker(
            repost_points=repost_points,
            like_points=like_points,
            week_number=week_number,
        )

    def build_description(
        self,
        *,
        post_external_id: str,
        text: str,
    ) -> str:
        normalized_marker = self.rules.marker.casefold()
        cleaned_text = "\n".join(
            line for line in text.splitlines() if not line.strip().casefold().startswith(normalized_marker)
        ).strip()
        description = f"Автоматически создано из VK-поста {post_external_id}."
        if cleaned_text:
            description = f"{description}\n\n{cleaned_text}"
        return description[: self.rules.max_description_length]


def parse_vk_post_task_marker(
    *,
    text: str,
    rules: VKPostTaskMarkerRules | None = None,
) -> ParsedVKPostMarker | None:
    return _get_parser(rules=rules).parse(text=text)


def build_vk_post_task_description(
    *,
    post_external_id: str,
    text: str,
    rules: VKPostTaskMarkerRules | None = None,
) -> str:
    return _get_parser(rules=rules).build_description(
        post_external_id=post_external_id,
        text=text,
    )


def _get_parser(*, rules: VKPostTaskMarkerRules | None) -> VKPostTaskMarkerParser:
    return _build_parser(rules=rules if rules is not None else VKPostTaskMarkerRules())


@cache
def _build_parser(*, rules: VKPostTaskMarkerRules) -> VKPostTaskMarkerParser:
    return VKPostTaskMarkerParser.from_rules(rules=rules)
