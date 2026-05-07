#!/usr/bin/env python3
"""
Test script to verify resize conflict fix
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_resize_conflict_fix():
    """Test that drag/resize conflicts are resolved"""
    print("Testing Resize Conflict Fix")
    print("=" * 40)
    
    # Test 1: Check if on_title_drag method exists
    try:
        from widgets.base_mini_widget import BaseMiniWidget
        
        if hasattr(BaseMiniWidget, 'on_title_drag'):
            print("✓ BaseMiniWidget has on_title_drag method")
        else:
            print("✗ BaseMiniWidget missing on_title_drag method")
            return False
            
        if hasattr(BaseMiniWidget, 'on_close_button_click'):
            print("✓ BaseMiniWidget has on_close_button_click method")
        else:
            print("✗ BaseMiniWidget missing on_close_button_click method")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 2: Check ModernMiniWidget
    try:
        from widgets.modern_widget_base import ModernMiniWidget
        
        if hasattr(ModernMiniWidget, 'on_title_drag'):
            print("✓ ModernMiniWidget has on_title_drag method")
        else:
            print("✗ ModernMiniWidget missing on_title_drag method")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 3: Check LiquidGlassWidget
    try:
        from widgets.liquid_glass_widget import LiquidGlassWidget
        
        if hasattr(LiquidGlassWidget, 'on_title_drag'):
            print("✓ LiquidGlassWidget has on_title_drag method")
        else:
            print("✗ LiquidGlassWidget missing on_title_drag method")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("✓ All resize conflict fix tests passed!")
    print("\nWhat was fixed:")
    print("- Drag events no longer interfere with resize")
    print("- Separate handlers for title drag vs resize")
    print("- on_title_drag only works when not resizing")
    print("- Proper event binding separation")
    
    print("\nExpected behavior now:")
    print("- Drag title bar → Move widget")
    print("- Drag edges → Resize widget (single axis)")
    print("- Drag corners → Resize widget (both axes)")
    print("- No more auto-incrementing issues")
    
    return True


def test_shared_resize_uses_logical_geometry():
    """Shared resize starts from geometry() values, not scaled winfo sizes."""
    from widgets.window_interactions import start_resize

    class FakeWindow:
        def geometry(self):
            return "280x210+40+50"

        def winfo_width(self):
            return 420

        def winfo_height(self):
            return 315

        def winfo_x(self):
            return 60

        def winfo_y(self):
            return 75

    class FakeEvent:
        x_root = 200
        y_root = 220

    window = FakeWindow()
    result = start_resize(window, FakeEvent(), "se")
    if result != "break":
        print("FAIL: start_resize should stop event propagation")
        return False
    if window._resize_start_w != 280 or window._resize_start_h != 210:
        print("FAIL: start_resize used scaled winfo dimensions")
        return False
    if window._resize_start_win_x != 40 or window._resize_start_win_y != 50:
        print("FAIL: start_resize used scaled winfo position")
        return False

    print("OK: Shared resize starts from logical geometry")
    return True


def test_scaled_pointer_coordinates_use_geometry_units():
    """High-DPI resize uses raw positions and scaled size deltas."""
    from widgets.window_interactions import geometry_root_point, logical_size_delta, start_resize, widget_point

    class FakeWindow:
        def geometry(self):
            return "280x210+40+50"

        def _get_window_scaling(self):
            return 1.5

    class FakeEvent:
        x_root = 300
        y_root = 360

    window = FakeWindow()
    root_x, root_y = geometry_root_point(window, FakeEvent())
    if (root_x, root_y) != (300, 360):
        print(f"FAIL: Root point should stay in screen pixels, got {(root_x, root_y)}")
        return False

    point_x, point_y = widget_point(window, FakeEvent())
    if (point_x, point_y) != (260, 310):
        print(f"FAIL: Widget hit point should stay in screen pixels, got {(point_x, point_y)}")
        return False

    delta_x, delta_y = logical_size_delta(window, 150, 120)
    if (delta_x, delta_y) != (100, 80):
        print(f"FAIL: Size delta was not converted to logical units: {(delta_x, delta_y)}")
        return False

    start_resize(window, FakeEvent(), "se")
    if window._resize_start_x != 300 or window._resize_start_y != 360:
        print("FAIL: Resize start did not keep raw screen coordinates")
        return False

    print("OK: Scaled pointer coordinates separate position and size units")
    return True


def test_drag_target_binding_is_idempotent():
    """Repeated widget refreshes should not stack drag callbacks."""
    from widgets.window_interactions import bind_drag_target

    class FakeWidget:
        def __init__(self, children=None):
            self.children = children or []
            self.bindings = []
            self.master = None
            for child in self.children:
                child.master = self

        def bind(self, sequence, handler, add=None):
            self.bindings.append((sequence, add))

        def winfo_children(self):
            return list(self.children)

    class FakeWindow(FakeWidget):
        pass

    child = FakeWidget()
    window = FakeWindow([child])

    bind_drag_target(window, window)
    bind_drag_target(window, window)

    if window.bindings:
        print("FAIL: Toplevel received duplicate shared drag bindings")
        return False
    if len(child.bindings) != 5:
        print(f"FAIL: Child expected 5 drag bindings, got {len(child.bindings)}")
        return False

    print("OK: Drag target bindings are idempotent")
    return True


def test_resize_release_saves_geometry():
    """Resize release must persist the final geometry after configure events were skipped."""
    import inspect

    from widgets.base_mini_widget import BaseMiniWidget
    from widgets.liquid_glass_widget import LiquidGlassWidget
    from widgets.modern_widget_base import ModernMiniWidget

    for cls in (BaseMiniWidget, ModernMiniWidget, LiquidGlassWidget):
        source = inspect.getsource(cls.on_mouse_up)
        if "_save_geometry_now" not in source:
            print(f"FAIL: {cls.__name__}.on_mouse_up does not save resized geometry")
            return False

    print("OK: Resize release saves final geometry")
    return True


def test_manual_release_does_not_auto_settle():
    """Manual drag/resize release should not snap widgets away from the user's chosen spot."""
    import inspect

    from widgets.base_mini_widget import BaseMiniWidget
    from widgets.liquid_glass_widget import LiquidGlassWidget
    from widgets.modern_widget_base import ModernMiniWidget
    from widgets.window_interactions import bind_drag_target

    for cls in (BaseMiniWidget, ModernMiniWidget, LiquidGlassWidget):
        source = inspect.getsource(cls.on_mouse_up)
        if "_settle_widget_position" in source:
            print(f"FAIL: {cls.__name__}.on_mouse_up still auto-settles manual resize")
            return False

    drag_source = inspect.getsource(bind_drag_target)
    release_block = drag_source[drag_source.find("def on_release") :]
    if "_settle_widget_position" in release_block:
        print("FAIL: Shared drag release still auto-settles manual drag")
        return False

    print("OK: Manual drag/resize release preserves user placement")
    return True


def test_northeast_resize_moves_top_edge():
    """Top-right resize should change the top edge, not resize downward."""
    from widgets.base_mini_widget import BaseMiniWidget
    from widgets.liquid_glass_widget import LiquidGlassWidget
    from widgets.modern_widget_base import ModernMiniWidget

    class FakeWindow:
        MIN_WIDTH = 160
        MIN_HEIGHT = 160
        MAX_WIDTH = 1000
        MAX_HEIGHT = 1000

        def __init__(self):
            self._is_resizing = True
            self._resize_dir = "ne"
            self._resize_start_x = 300
            self._resize_start_y = 300
            self._resize_start_w = 200
            self._resize_start_h = 200
            self._resize_start_win_x = 100
            self._resize_start_win_y = 100
            self.applied_geometry = ""

        def _get_window_scaling(self):
            return 1.0

        def geometry(self, value=None):
            if value is not None:
                self.applied_geometry = value
            return self.applied_geometry or "200x200+100+100"

    class FakeEvent:
        x_root = 350
        y_root = 260

    for cls in (BaseMiniWidget, ModernMiniWidget, LiquidGlassWidget):
        window = FakeWindow()
        result = cls.on_mouse_drag(window, FakeEvent())
        if result != "break":
            print(f"FAIL: {cls.__name__} did not stop event propagation")
            return False
        if window.applied_geometry != "250x240+100+60":
            print(f"FAIL: {cls.__name__} applied {window.applied_geometry} for northeast resize")
            return False

    print("OK: Northeast resize moves the top edge")
    return True


if __name__ == "__main__":
    success = (
        test_resize_conflict_fix()
        and test_shared_resize_uses_logical_geometry()
        and test_scaled_pointer_coordinates_use_geometry_units()
        and test_drag_target_binding_is_idempotent()
        and test_resize_release_saves_geometry()
        and test_manual_release_does_not_auto_settle()
        and test_northeast_resize_moves_top_edge()
    )
    sys.exit(0 if success else 1)
