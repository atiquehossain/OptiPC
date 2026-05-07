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
    """Test all widget categories share the same default dimensions."""
    try:
        from config.constants import DEFAULT_WIDGET_HEIGHT, DEFAULT_WIDGET_WIDTH, WIDGET_SIZES

        for size_name in ("default", "small", "medium", "large", "extra_large"):
            actual = WIDGET_SIZES[size_name]
            if actual["width"] != DEFAULT_WIDGET_WIDTH or actual["height"] != DEFAULT_WIDGET_HEIGHT:
                print(
                    f"FAIL: Size {size_name}: expected {DEFAULT_WIDGET_WIDTH}x{DEFAULT_WIDGET_HEIGHT}, "
                    f"got {actual['width']}x{actual['height']}"
                )
                return False

        print("OK: All widget default sizes are uniform")
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
    """Test compact widgets cannot shrink below readable dimensions."""
    try:
        from config.constants import DEFAULT_WIDGET_HEIGHT, DEFAULT_WIDGET_WIDTH, WIDGET_SIZE_LIMITS

        for size_name, limits in WIDGET_SIZE_LIMITS.items():
            if limits["min_width"] > DEFAULT_WIDGET_WIDTH or limits["min_height"] > DEFAULT_WIDGET_HEIGHT:
                print(f"FAIL: {size_name} minimum exceeds the uniform default size")
                return False

        for size_name in ("small", "default"):
            limits = WIDGET_SIZE_LIMITS[size_name]
            if limits["min_width"] < 190 or limits["min_height"] < 190:
                print(f"FAIL: {size_name} minimum is too small for readable compact widgets")
                return False

        print("OK: Widget minimums fit inside the uniform default size")
        return True
    except Exception as exc:
        print(f"FAIL: Size limit test error: {exc}")
        return False


def test_legacy_default_size_migration():
    """Test saved legacy default widget sizes normalize to the common default."""
    try:
        import tempfile
        from pathlib import Path

        from config.constants import DEFAULT_WIDGET_HEIGHT, DEFAULT_WIDGET_WIDTH
        from services.widget_state_service import WidgetStateService

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "widget_state.json"
            path.write_text(
                (
                    '{"widgets":{"cpu":{"visible":true,"width":200,"height":200},'
                    '"custom":{"visible":true,"width":333,"height":211}},'
                    '"main_window":{}}'
                ),
                encoding="utf-8",
            )
            service = WidgetStateService(path)
            cpu = service.get_widget_state("cpu")
            custom = service.get_widget_state("custom")

        if cpu.get("width") != DEFAULT_WIDGET_WIDTH or cpu.get("height") != DEFAULT_WIDGET_HEIGHT:
            print("FAIL: Legacy default size was not normalized")
            return False
        if custom.get("width") != 333 or custom.get("height") != 211:
            print("FAIL: Custom widget size was changed during migration")
            return False

        print("OK: Legacy default sizes migrate without touching custom sizes")
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
            _default_width = 320
            _default_height = 240
            PADDING_HORIZONTAL = 20

            def __init__(self, width, height):
                self.width = width
                self.height = height

            def winfo_width(self):
                return self.width

            def winfo_height(self):
                return self.height

        compact = FakeWindow(190, 190)
        roomy = FakeWindow(320, 240)

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
