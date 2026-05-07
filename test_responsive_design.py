#!/usr/bin/env python3
"""Validate widget responsive design defaults."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all imports work correctly."""
    try:
        from config.constants import RESPONSIVE_FONT_SIZES, WIDGET_SIZES

        required_sizes = ["default", "small", "medium", "large", "extra_large"]
        for size in required_sizes:
            if size not in WIDGET_SIZES:
                print(f"FAIL: Missing size category: {size}")
                return False
            if size not in RESPONSIVE_FONT_SIZES:
                print(f"FAIL: Missing font size category: {size}")
                return False

        required_fonts = ["tiny", "small", "body", "label", "title", "metric", "hero"]
        for size in required_sizes:
            for font in required_fonts:
                if font not in RESPONSIVE_FONT_SIZES[size]:
                    print(f"FAIL: Missing font key {font} in size {size}")
                    return False

        print("OK: Constants import and required keys are present")
        return True
    except ImportError as exc:
        print(f"FAIL: Import error: {exc}")
        return False
    except Exception as exc:
        print(f"FAIL: Unexpected error: {exc}")
        return False


def test_widget_sizes():
    """Test widget categories use the configured default dimensions."""
    try:
        from config.constants import DEFAULT_WIDGET_HEIGHT, DEFAULT_WIDGET_WIDTH, WIDGET_SIZES

        expected_sizes = {
            "small": {"width": 170, "height": 170},
            "medium": {"width": 364, "height": 170},
            "large": {"width": 364, "height": 376},
            "extra_large": {"width": 745, "height": 376},
            "default": {"width": DEFAULT_WIDGET_WIDTH, "height": DEFAULT_WIDGET_HEIGHT},
        }

        for size_name, expected in expected_sizes.items():
            actual = WIDGET_SIZES[size_name]
            if actual != expected:
                print(
                    f"FAIL: Size {size_name}: expected {expected['width']}x{expected['height']}, "
                    f"got {actual['width']}x{actual['height']}"
                )
                return False

        print("OK: Widget default sizes match the configured presets")
        return True
    except Exception as exc:
        print(f"FAIL: Size test error: {exc}")
        return False


def test_responsive_fonts():
    """Test responsive font scaling."""
    try:
        from config.constants import RESPONSIVE_FONT_SIZES

        base_metric = RESPONSIVE_FONT_SIZES["small"]["metric"]
        for size in ["medium", "large", "extra_large"]:
            metric = RESPONSIVE_FONT_SIZES[size]["metric"]
            if metric <= base_metric:
                print(f"FAIL: Font size does not scale up: {size} metric {metric} <= small {base_metric}")
                return False

        print("OK: Font scaling works correctly")
        return True
    except Exception as exc:
        print(f"FAIL: Font test error: {exc}")
        return False


def test_widget_size_limits():
    """Test resize limits contain each category's default dimensions."""
    try:
        from config.constants import WIDGET_SIZE_LIMITS, WIDGET_SIZES

        for size_name, limits in WIDGET_SIZE_LIMITS.items():
            default_size = WIDGET_SIZES[size_name]
            if limits["min_width"] > default_size["width"] or limits["min_height"] > default_size["height"]:
                print(f"FAIL: {size_name} minimum exceeds its default size")
                return False
            if limits["max_width"] < default_size["width"] or limits["max_height"] < default_size["height"]:
                print(f"FAIL: {size_name} maximum is below its default size")
                return False

        print("OK: Widget resize limits contain every default size")
        return True
    except Exception as exc:
        print(f"FAIL: Size limit test error: {exc}")
        return False


def test_legacy_default_size_migration():
    """Test saved legacy default widget sizes normalize to their category defaults."""
    try:
        import tempfile
        from pathlib import Path

        from config.constants import WIDGET_SIZES
        from services.widget_state_service import WidgetStateService

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "widget_state.json"
            path.write_text(
                (
                    '{"widgets":{"cpu":{"visible":true,"width":200,"height":200},'
                    '"network_speed":{"visible":true,"width":280,"height":210},'
                    '"calendar":{"visible":true,"width":320,"height":240},'
                    '"custom":{"visible":true,"width":333,"height":211}},'
                    '"main_window":{}}'
                ),
                encoding="utf-8",
            )
            service = WidgetStateService(path)
            cpu = service.get_widget_state("cpu")
            network_speed = service.get_widget_state("network_speed")
            calendar = service.get_widget_state("calendar")
            custom = service.get_widget_state("custom")

        if cpu.get("width") != WIDGET_SIZES["small"]["width"] or cpu.get("height") != WIDGET_SIZES["small"]["height"]:
            print("FAIL: Legacy small default size was not normalized")
            return False
        if (
            network_speed.get("width") != WIDGET_SIZES["medium"]["width"]
            or network_speed.get("height") != WIDGET_SIZES["medium"]["height"]
        ):
            print("FAIL: Legacy medium default size was not normalized")
            return False
        if (
            calendar.get("width") != WIDGET_SIZES["extra_large"]["width"]
            or calendar.get("height") != WIDGET_SIZES["extra_large"]["height"]
        ):
            print("FAIL: Legacy extra large default size was not normalized")
            return False
        if custom.get("width") != 333 or custom.get("height") != 211:
            print("FAIL: Custom widget size was changed during migration")
            return False

        print("OK: Legacy default sizes migrate by category without touching custom sizes")
        return True
    except Exception as exc:
        print(f"FAIL: Legacy default size migration test error: {exc}")
        return False


def test_live_responsive_helper():
    """Test live font scaling uses current widget geometry."""
    try:
        from widgets.responsive_layout import content_wraplength, responsive_font_size

        class FakeWindow:
            size_category = "small"
            _default_width = 170
            _default_height = 170
            PADDING_HORIZONTAL = 20

            def __init__(self, width, height):
                self.width = width
                self.height = height

            def winfo_width(self):
                return self.width

            def winfo_height(self):
                return self.height

        compact = FakeWindow(150, 150)
        roomy = FakeWindow(170, 170)

        if responsive_font_size(compact, "body") > responsive_font_size(roomy, "body"):
            print("FAIL: Compact font is larger than roomy font")
            return False
        if content_wraplength(compact) >= content_wraplength(roomy):
            print("FAIL: Wrap length does not adapt to widget width")
            return False

        print("OK: Live responsive helper adapts to geometry")
        return True
    except Exception as exc:
        print(f"FAIL: Live responsive helper test error: {exc}")
        return False


def test_widget_overlap_placement():
    """Test widget placement keeps a readable gap from existing widgets."""
    try:
        from widgets import window_interactions

        original_bounds = window_interactions.get_virtual_screen_bounds
        window_interactions.get_virtual_screen_bounds = lambda: (0, 0, 1200, 800)
        try:
            x, y = window_interactions.find_non_overlapping_position(
                100,
                100,
                280,
                210,
                [(100, 100, 280, 210)],
                gap=18,
                margin=12,
            )
        finally:
            window_interactions.get_virtual_screen_bounds = original_bounds

        if window_interactions.rectangles_overlap((x, y, 280, 210), (100, 100, 280, 210), gap=18):
            print("FAIL: Placement still overlaps an existing widget")
            return False

        print("OK: Widget placement avoids overlap with a gap")
        return True
    except Exception as exc:
        print(f"FAIL: Widget overlap placement test error: {exc}")
        return False


def test_scaled_screen_edge_uses_logical_size():
    """Test right-edge placement is not pulled toward the middle on scaled displays."""
    try:
        from widgets import window_interactions

        class FakeWindow:
            def _get_window_scaling(self):
                return 1.5

        original_bounds = window_interactions.get_virtual_screen_bounds
        window_interactions.get_virtual_screen_bounds = lambda _window=None: (0, 0, 1920, 1200)
        try:
            x, y = window_interactions.clamp_widget_position(
                FakeWindow(),
                1640,
                80,
                170,
                170,
            )
        finally:
            window_interactions.get_virtual_screen_bounds = original_bounds

        if x != 1640 or y != 80:
            print(f"FAIL: Right-edge logical placement was clamped to {(x, y)}")
            return False

        print("OK: Scaled display edge placement uses logical widget size")
        return True
    except Exception as exc:
        print(f"FAIL: Scaled screen edge placement test error: {exc}")
        return False


def test_app_overlap_placement_keeps_right_column():
    """Test opening a second widget does not pull a free right-column drop inward."""
    try:
        import app as app_module

        class FakeApp:
            def _get_window_scaling(self):
                return 1.5

            def _effective_widget_size(self, width, height):
                return app_module.effective_window_size(self, width, height)

            def _visible_widget_rects(self, exclude_key=None):
                return [(1640, 80, 255, 255)]

        original_bounds = app_module.get_virtual_screen_bounds
        app_module.get_virtual_screen_bounds = lambda _window=None: (0, 0, 1920, 1200)
        try:
            x, y = app_module.OptiPCApp._non_overlapping_widget_position(
                FakeApp(),
                "ram",
                1640,
                420,
                170,
                170,
            )
        finally:
            app_module.get_virtual_screen_bounds = original_bounds

        if (x, y) != (1640, 420):
            print(f"FAIL: Free right-column widget was moved to {(x, y)}")
            return False

        print("OK: App overlap placement keeps free right-column drops")
        return True
    except Exception as exc:
        print(f"FAIL: App right-column placement test error: {exc}")
        return False


def test_calendar_size_classes():
    """Test calendar content modes follow Mac-style widget size classes."""
    try:
        from widgets.calendar_responsive import calendar_size_class, calendar_uses_month_grid, widget_content_margin

        class FakeCalendar:
            def __init__(self, width, height):
                self.width = width
                self.height = height

            def geometry(self):
                return f"{self.width}x{self.height}+0+0"

            def winfo_width(self):
                return self.width

            def winfo_height(self):
                return self.height

        cases = [
            (170, 170, "small", False, 10),
            (364, 170, "medium", False, 12),
            (364, 376, "large", True, 16),
            (745, 376, "extra_large", True, 16),
        ]
        for width, height, expected_class, expected_grid, expected_margin in cases:
            widget = FakeCalendar(width, height)
            if calendar_size_class(widget) != expected_class:
                print(f"FAIL: Calendar {width}x{height} was classified as {calendar_size_class(widget)}")
                return False
            if calendar_uses_month_grid(widget) != expected_grid:
                print(f"FAIL: Calendar {width}x{height} grid mode mismatch")
                return False
            if widget_content_margin(widget) != expected_margin:
                print(f"FAIL: Calendar {width}x{height} margin mismatch")
                return False

        print("OK: Calendar size classes switch content modes correctly")
        return True
    except Exception as exc:
        print(f"FAIL: Calendar size class test error: {exc}")
        return False


def test_widget_material_modes():
    """Test Liquid Glass color modes resolve to readable Mac-style palettes."""
    try:
        from config.constants import WIDGET_THEMES
        from services.widget_material_service import resolve_widget_material_theme

        base = WIDGET_THEMES["modern_dark"]
        full_color = resolve_widget_material_theme(base, mode="full_color", appearance="Dark", wallpaper_path="")
        monochrome = resolve_widget_material_theme(base, mode="monochrome", appearance="Dark", wallpaper_path="")
        tinted = resolve_widget_material_theme(base, mode="tinted", appearance="Dark", wallpaper_path="")
        automatic_idle = resolve_widget_material_theme(base, mode="automatic", appearance="Dark", wallpaper_path="", active=False)

        if full_color["cpu_accent"] == full_color["ram_accent"]:
            print("FAIL: Full color mode flattened widget accent colors")
            return False
        if monochrome["cpu_accent"] != monochrome["ram_accent"]:
            print("FAIL: Monochrome mode did not flatten accent colors")
            return False
        if automatic_idle["material_mode"] != "monochrome":
            print("FAIL: Automatic idle mode did not resolve to monochrome")
            return False
        if not tinted.get("wallpaper_tint") or tinted["material_mode"] != "tinted":
            print("FAIL: Tinted mode did not expose wallpaper tint state")
            return False
        if not all(theme.get("native_blur") for theme in (full_color, monochrome, tinted)):
            print("FAIL: Material modes did not request native blur")
            return False

        print("OK: Widget material modes resolve correctly")
        return True
    except Exception as exc:
        print(f"FAIL: Widget material mode test error: {exc}")
        return False


def main():
    print("Testing OptiPC Widget Responsive Design Implementation")
    print("=" * 60)

    tests = [
        ("Import Tests", test_imports),
        ("Widget Size Tests", test_widget_sizes),
        ("Responsive Font Tests", test_responsive_fonts),
        ("Widget Size Limit Tests", test_widget_size_limits),
        ("Legacy Default Size Migration Tests", test_legacy_default_size_migration),
        ("Live Responsive Helper Tests", test_live_responsive_helper),
        ("Widget Overlap Placement Tests", test_widget_overlap_placement),
        ("Scaled Screen Edge Placement Tests", test_scaled_screen_edge_uses_logical_size),
        ("App Right Column Placement Tests", test_app_overlap_placement_keeps_right_column),
        ("Calendar Size Class Tests", test_calendar_size_classes),
        ("Widget Material Mode Tests", test_widget_material_modes),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"FAIL: {test_name} failed")

    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("OK: All tests passed. Implementation is correct.")
        return True
    print("FAIL: Some tests failed. Please check the issues above.")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
