from __future__ import annotations

from config.constants import DEFAULT_WIDGET_HEIGHT, DEFAULT_WIDGET_WIDTH
from config.widget_specs import WidgetSpec, widget_default_size, widget_spec


class WidgetSpecMixin:
    """Resolve shared widget title, size, and accent metadata."""

    widget_spec: WidgetSpec
    widget_key: str
    widget_title: str
    size_category: str
    accent_key: str

    def _resolve_widget_spec_defaults(
        self,
        title: str | None,
        widget_key: str,
        size_category: str | None,
    ) -> tuple[str, str, str]:
        spec = widget_spec(widget_key)
        resolved_title = title if title is not None else spec.title
        resolved_key = widget_key or spec.key
        resolved_category = size_category or spec.size_category

        self.widget_spec = spec
        self.widget_key = resolved_key
        self.widget_title = resolved_title
        self.size_category = resolved_category
        self.accent_key = spec.accent_key
        return resolved_title, resolved_key, resolved_category

    def _resolve_widget_dimensions(
        self,
        width: int | None,
        height: int | None,
    ) -> tuple[int, int]:
        size = widget_default_size(getattr(self, "widget_key", ""), getattr(self, "size_category", "default"))
        return (
            int(width if width is not None else size.get("width", DEFAULT_WIDGET_WIDTH)),
            int(height if height is not None else size.get("height", DEFAULT_WIDGET_HEIGHT)),
        )

    def widget_accent_color(self, fallback: str | None = None) -> str:
        theme = getattr(self, "theme", {}) or {}
        return theme.get(getattr(self, "accent_key", "accent"), fallback or theme.get("accent", "#4f9cff"))
