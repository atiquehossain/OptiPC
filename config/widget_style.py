from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class WidgetTextRole:
    size_key: str
    weight: str = "normal"
    color_key: str = "text"


_WIDGET_TEXT_ROLES: dict[str, WidgetTextRole] = {
    "hero": WidgetTextRole("hero", "bold", "text"),
    "metric": WidgetTextRole("metric", "bold", "text"),
    "title": WidgetTextRole("title", "bold", "text"),
    "body": WidgetTextRole("body", "normal", "text"),
    "body_bold": WidgetTextRole("body", "bold", "text"),
    "caption": WidgetTextRole("small", "normal", "muted"),
    "caption_bold": WidgetTextRole("small", "bold", "muted"),
    "tiny": WidgetTextRole("tiny", "normal", "muted"),
}

WIDGET_TEXT_ROLES = MappingProxyType(_WIDGET_TEXT_ROLES)


def widget_text_role(role: str | None = None) -> WidgetTextRole:
    return WIDGET_TEXT_ROLES.get(str(role or "body"), WIDGET_TEXT_ROLES["body"])
