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


def test_widget_specs():
    """Test shared widget specs centralize size and accent defaults."""
    try:
        from config.constants import WIDGET_SIZES
        from config.widget_specs import KNOWN_WIDGET_KEYS, widget_accent_key, widget_default_size, widget_size_category

        required_keys = {
            "cpu",
            "ram",
            "gpu",
            "clock",
            "world_clock",
            "calendar",
            "storage",
            "bluetooth",
            "top_processes",
            "network_speed",
        }
        missing = required_keys - set(KNOWN_WIDGET_KEYS)
        if missing:
            print(f"FAIL: Missing widget specs: {sorted(missing)}")
            return False
        if widget_size_category("clock") != "small":
            print("FAIL: Clock is not using the standard small size class")
            return False
        if widget_accent_key("clock") != "clock_accent":
            print("FAIL: Clock accent is not centralized")
            return False
        if widget_accent_key("world_clock") != "clock_accent":
            print("FAIL: World clock accent is not centralized")
            return False
        if widget_accent_key("bluetooth") != "bluetooth_accent":
            print("FAIL: Bluetooth accent is not centralized")
            return False
        for key in KNOWN_WIDGET_KEYS:
            if widget_size_category(key) != "small":
                print(f"FAIL: {key} is not using the standard small default size class")
                return False
            if widget_default_size(key) != WIDGET_SIZES["small"]:
                print(f"FAIL: {key} default size does not match the small preset")
                return False

        if widget_size_category("calendar") != "small":
            print("FAIL: Calendar should default to the same small size as other widgets")
            return False

        print("OK: Widget specs centralize default size and accent rules")
        return True
    except Exception as exc:
        print(f"FAIL: Widget spec test error: {exc}")
        return False


def test_widget_text_roles():
    """Test shared widget text roles cover the common desktop widget hierarchy."""
    try:
        from config.widget_style import WIDGET_TEXT_ROLES, widget_text_role

        required_roles = ["hero", "metric", "title", "body", "body_bold", "caption", "caption_bold", "tiny"]
        for role in required_roles:
            if role not in WIDGET_TEXT_ROLES:
                print(f"FAIL: Missing widget text role: {role}")
                return False
        if widget_text_role("hero").size_key != "hero":
            print("FAIL: Hero role does not map to the hero responsive size")
            return False
        if widget_text_role("caption").color_key != "muted":
            print("FAIL: Caption role does not use muted color")
            return False
        if widget_text_role("unknown").size_key != "body":
            print("FAIL: Unknown text role should fall back to body")
            return False

        print("OK: Widget text roles centralize typography and color hierarchy")
        return True
    except Exception as exc:
        print(f"FAIL: Widget text role test error: {exc}")
        return False


def test_analog_clock_widgets():
    """Test clock widgets share analog rendering and city selection models."""
    try:
        from datetime import datetime
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from services.widget_state_service import WidgetStateService
        from widgets.smart_widgets import AnalogClockRenderer, AnalogClockWidget, WorldClockWidget

        if not hasattr(AnalogClockWidget, "_draw_clock"):
            print("FAIL: Normal clock is not backed by the analog canvas widget")
            return False
        day = AnalogClockRenderer._palette({}, datetime(2026, 5, 7, 12, 0), face_mode="auto")
        night = AnalogClockRenderer._palette({}, datetime(2026, 5, 7, 23, 0), face_mode="auto")
        if day["face"] == night["face"]:
            print("FAIL: Analog clock face does not react to day/night time")
            return False
        names = WorldClockWidget._normalize_city_names(["Tokyo", "London", "Missing", "Tokyo"])
        if len(names) != 4 or names[0] != "Tokyo" or names[1] != "London":
            print(f"FAIL: World clock city normalization failed: {names}")
            return False
        with TemporaryDirectory() as tmp_dir:
            service = WidgetStateService(Path(tmp_dir) / "widget_state.json")
            service.set_widget_option("world_clock", "cities", ["Tokyo", "London"])
            if service.get_widget_state("world_clock").get("cities") != ["Tokyo", "London"]:
                print("FAIL: Widget state service did not persist custom widget options")
                return False

        print("OK: Analog clock widgets share rendering and city selection state")
        return True
    except Exception as exc:
        print(f"FAIL: Analog clock widget test error: {exc}")
        return False


def test_cpu_usage_helpers():
    """Test CPU usage formatting keeps low activity visible."""
    try:
        from collections import namedtuple

        from widgets.cpu_usage import cpu_percent_from_times, format_cpu_percent

        Times = namedtuple("Times", "user system idle")
        percent = cpu_percent_from_times(Times(1.0, 1.0, 8.0), Times(1.2, 1.1, 8.7))
        if round(percent, 1) != 30.0:
            print(f"FAIL: CPU sampler percent expected 30.0, got {percent:.1f}")
            return False
        if format_cpu_percent(0.4) != "0.4%":
            print("FAIL: Low non-zero CPU activity rounded away")
            return False
        if format_cpu_percent(2.0) != "2.0%":
            print("FAIL: Low CPU activity should show one decimal")
            return False
        if format_cpu_percent(35.4) != "35%":
            print("FAIL: Normal CPU activity should keep compact integer formatting")
            return False

        print("OK: CPU helper keeps low activity visible")
        return True
    except Exception as exc:
        print(f"FAIL: CPU helper test error: {exc}")
        return False


def test_bluetooth_widget_connection_summary():
    """Test Bluetooth widget does not mark paired-only devices as connected."""
    try:
        from widgets.smart_widgets import BluetoothWidget

        widget = BluetoothWidget.__new__(BluetoothWidget)
        paired_entries = [
            {
                "FriendlyName": "Md's JBL Go 4",
                "Status": "OK",
                "InstanceId": r"BTHENUM\DEV_20185BF24911\7&TEST&0&BLUETOOTHDEVICE_20185BF24911",
            },
            {
                "FriendlyName": "Md's JBL Go 4 Avrcp Transport",
                "Status": "OK",
                "InstanceId": r"BTHENUM\{0000110C-0000-1000-8000-00805F9B34FB}\7&TEST",
            },
        ]
        radio_entries = [{"FriendlyName": "Bluetooth", "Status": "OK", "InstanceId": r"SWD\RADIO\BLUETOOTH_TEST"}]
        disconnected_endpoints = [{"Name": "Headphones (Md's JBL Go 4)", "Status": "Unknown"}]

        paired_only = widget._summarize_bluetooth_entries(paired_entries, "running", radio_entries, disconnected_endpoints)
        if paired_only["connected_count"] != 0 or paired_only["audio_active"]:
            print("FAIL: Paired Bluetooth devices were counted as connected")
            return False
        if paired_only["summary"] != "Bluetooth on | no devices connected":
            print(f"FAIL: Paired-only summary was wrong: {paired_only['summary']}")
            return False
        widget._bluetooth_snapshot = paired_only
        paired_only_rings = widget._ring_model()
        if any(ring["progress"] for ring in paired_only_rings) or any(ring["icon"] for ring in paired_only_rings):
            print("FAIL: Paired-only Bluetooth state rendered active rings or icons")
            return False

        connected = widget._summarize_bluetooth_entries(
            paired_entries,
            "running",
            radio_entries,
            [{"Name": "Headphones (Md's JBL Go 4)", "Status": "OK"}],
        )
        if connected["connected_count"] != 1 or not connected["audio_active"]:
            print("FAIL: Active Bluetooth audio endpoint was not counted")
            return False
        widget._bluetooth_snapshot = connected
        connected_rings = widget._ring_model()
        if connected_rings[0]["progress"] != 0 or connected_rings[0]["active"]:
            print("FAIL: Connected device without battery telemetry rendered as charged")
            return False

        print("OK: Bluetooth widget distinguishes paired devices from live connections")
        return True
    except Exception as exc:
        print(f"FAIL: Bluetooth widget connection test error: {exc}")
        return False


def test_widget_subprocesses_run_hidden():
    """Test widget background probes use the hidden subprocess wrapper."""
    try:
        import inspect

        import widgets.smart_widgets as smart_widgets

        source = inspect.getsource(smart_widgets)
        if "def run_hidden_subprocess" not in source:
            print("FAIL: Missing hidden subprocess wrapper")
            return False
        if source.count("subprocess.run(") != 1:
            print("FAIL: Widget probes call subprocess.run directly")
            return False
        if source.count("run_hidden_subprocess(") < 8:
            print("FAIL: Widget background probes are not routed through the hidden runner")
            return False

        print("OK: Widget background subprocesses run hidden")
        return True
    except Exception as exc:
        print(f"FAIL: Hidden subprocess test error: {exc}")
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
                    '"calendar":{"visible":true,"width":364,"height":376},'
                    '"storage":{"visible":true,"width":316,"height":213},'
                    '"custom":{"visible":true,"width":333,"height":211}},'
                    '"main_window":{}}'
                ),
                encoding="utf-8",
            )
            service = WidgetStateService(path)
            cpu = service.get_widget_state("cpu")
            network_speed = service.get_widget_state("network_speed")
            calendar = service.get_widget_state("calendar")
            storage = service.get_widget_state("storage")
            custom = service.get_widget_state("custom")

        if cpu.get("width") != WIDGET_SIZES["small"]["width"] or cpu.get("height") != WIDGET_SIZES["small"]["height"]:
            print("FAIL: Legacy small default size was not normalized")
            return False
        if (
            network_speed.get("width") != WIDGET_SIZES["small"]["width"]
            or network_speed.get("height") != WIDGET_SIZES["small"]["height"]
        ):
            print("FAIL: Legacy medium default size was not normalized to small")
            return False
        if (
            calendar.get("width") != WIDGET_SIZES["small"]["width"]
            or calendar.get("height") != WIDGET_SIZES["small"]["height"]
        ):
            print("FAIL: Legacy calendar default size was not normalized to small")
            return False
        if storage.get("width") != WIDGET_SIZES["small"]["width"] or storage.get("height") != WIDGET_SIZES["small"]["height"]:
            print("FAIL: Known custom-sized widget was not normalized to small")
            return False
        if custom.get("width") != 333 or custom.get("height") != 211:
            print("FAIL: Custom widget size was changed during migration")
            return False

        print("OK: Legacy default sizes migrate to the uniform small default without touching custom sizes")
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
        from widgets.calendar_responsive import (
            CALENDAR_WEEKDAY_LABELS,
            calendar_canvas_nav_action_at_point,
            calendar_month_dates,
            calendar_size_class,
            calendar_uses_month_grid,
            widget_content_margin,
        )

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

        class FakeCanvas:
            def __init__(self, width, height):
                self.width = width
                self.height = height

            def winfo_width(self):
                return self.width

            def winfo_height(self):
                return self.height

        cases = [
            (170, 170, "small", True, 10),
            (364, 170, "medium", True, 12),
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

        if CALENDAR_WEEKDAY_LABELS != ("M", "T", "W", "T", "F", "S", "S"):
            print("FAIL: Calendar weekdays are not Monday-first")
            return False
        may_2026 = calendar_month_dates(2026, 5)
        first_row = [day.day for day in may_2026[0]]
        if first_row != [27, 28, 29, 30, 1, 2, 3]:
            print(f"FAIL: Calendar leading dates mismatch: {first_row}")
            return False
        if len(may_2026) != 6 or any(len(week) != 7 for week in may_2026):
            print("FAIL: Calendar does not return a fixed 6x7 grid")
            return False
        fake_widget = FakeCalendar(170, 170)
        fake_canvas = FakeCanvas(170, 170)
        if calendar_canvas_nav_action_at_point(fake_canvas, fake_widget, 10, 14) != "previous":
            print("FAIL: Calendar previous-month hit zone is missing")
            return False
        if calendar_canvas_nav_action_at_point(fake_canvas, fake_widget, 160, 14) != "next":
            print("FAIL: Calendar next-month hit zone is missing")
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
        if full_color["bluetooth_accent"] == full_color["cpu_accent"]:
            print("FAIL: Bluetooth full color accent was not preserved")
            return False
        if monochrome["cpu_accent"] != monochrome["ram_accent"] or monochrome["bluetooth_accent"] != monochrome["cpu_accent"]:
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


def test_app_theme_change_refreshes_widgets():
    """Test app Light/Dark changes also refresh already-open floating widgets."""
    try:
        import app as app_module

        class FakeSettings:
            def __init__(self):
                self.mode = ""

            def set_appearance_mode(self, mode):
                self.mode = mode

        class FakeSwitch:
            def __init__(self):
                self.value = ""

            def set(self, value):
                self.value = value

        class FakeTopbar:
            def __init__(self):
                self.theme_switch = FakeSwitch()

        class FakeSidebar:
            def __init__(self):
                self.mode = ""

            def update_theme(self, mode):
                self.mode = mode

        class FakeStatus:
            def success(self, *_args, **_kwargs):
                pass

        class FakeApp:
            def __init__(self):
                self.app_settings = FakeSettings()
                self.topbar = FakeTopbar()
                self.sidebar = FakeSidebar()
                self.status_service = FakeStatus()
                self.refresh_count = 0

            def apply_widget_theme_to_open_widgets(self):
                self.refresh_count += 1

        fake_app = FakeApp()
        original_set_appearance_mode = app_module.ctk.set_appearance_mode
        app_module.ctk.set_appearance_mode = lambda _mode: None
        try:
            app_module.OptiPCApp.change_theme(fake_app, "Light")
        finally:
            app_module.ctk.set_appearance_mode = original_set_appearance_mode

        if fake_app.app_settings.mode != "Light":
            print("FAIL: App theme did not store Light mode")
            return False
        if fake_app.refresh_count != 1:
            print("FAIL: App theme change did not refresh open widgets")
            return False

        print("OK: App theme changes refresh floating widgets")
        return True
    except Exception as exc:
        print(f"FAIL: App theme refresh test error: {exc}")
        return False


def test_main_geometry_skips_hidden_smoke_window():
    """Test hidden smoke-test windows cannot overwrite normal main geometry."""
    try:
        import inspect

        from app import OptiPCApp

        configure_source = inspect.getsource(OptiPCApp._on_main_configure)
        save_source = inspect.getsource(OptiPCApp._save_main_geometry)
        if 'self.state() == "withdrawn"' not in configure_source:
            print("FAIL: Main configure does not skip withdrawn windows")
            return False
        if 'self.state() == "withdrawn"' not in save_source:
            print("FAIL: Main geometry save does not skip withdrawn windows")
            return False
        if "width < 800 or height < 500" not in save_source:
            print("FAIL: Main geometry save does not reject tiny smoke-test geometry")
            return False

        print("OK: Main geometry save ignores hidden smoke-test windows")
        return True
    except Exception as exc:
        print(f"FAIL: Main geometry save guard test error: {exc}")
        return False


def test_smoke_test_restores_user_config():
    """Test smoke tests restore user config files after launching hidden UI."""
    try:
        import inspect

        import main as main_module

        source = inspect.getsource(main_module.run_smoke_test)
        if "_snapshot_config_files" not in source or "_restore_config_files" not in source:
            print("FAIL: Smoke test does not snapshot and restore user config")
            return False

        print("OK: Smoke test restores user config files")
        return True
    except Exception as exc:
        print(f"FAIL: Smoke config restore test error: {exc}")
        return False


def main():
    print("Testing OptiPC Widget Responsive Design Implementation")
    print("=" * 60)

    tests = [
        ("Import Tests", test_imports),
        ("Widget Size Tests", test_widget_sizes),
        ("Widget Spec Tests", test_widget_specs),
        ("Widget Text Role Tests", test_widget_text_roles),
        ("Analog Clock Widget Tests", test_analog_clock_widgets),
        ("CPU Usage Helper Tests", test_cpu_usage_helpers),
        ("Bluetooth Connection Tests", test_bluetooth_widget_connection_summary),
        ("Hidden Subprocess Tests", test_widget_subprocesses_run_hidden),
        ("Responsive Font Tests", test_responsive_fonts),
        ("Widget Size Limit Tests", test_widget_size_limits),
        ("Legacy Default Size Migration Tests", test_legacy_default_size_migration),
        ("Live Responsive Helper Tests", test_live_responsive_helper),
        ("Widget Overlap Placement Tests", test_widget_overlap_placement),
        ("Scaled Screen Edge Placement Tests", test_scaled_screen_edge_uses_logical_size),
        ("App Right Column Placement Tests", test_app_overlap_placement_keeps_right_column),
        ("Calendar Size Class Tests", test_calendar_size_classes),
        ("Widget Material Mode Tests", test_widget_material_modes),
        ("App Theme Widget Refresh Tests", test_app_theme_change_refreshes_widgets),
        ("Main Geometry Smoke Guard Tests", test_main_geometry_skips_hidden_smoke_window),
        ("Smoke Config Restore Tests", test_smoke_test_restores_user_config),
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
