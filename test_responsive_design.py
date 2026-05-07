#!/usr/bin/env python3
"""
Test script to validate widget responsive design implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly"""
    try:
        from config.constants import WIDGET_SIZES, RESPONSIVE_FONT_SIZES
        print("✓ Constants import successful")
        
        # Test that all required size categories exist
        required_sizes = ["default", "small", "medium", "large", "extra_large"]
        for size in required_sizes:
            if size not in WIDGET_SIZES:
                print(f"✗ Missing size category: {size}")
                return False
            if size not in RESPONSIVE_FONT_SIZES:
                print(f"✗ Missing font size category: {size}")
                return False
        print("✓ All size categories present")
        
        # Test that required font keys exist
        required_fonts = ["tiny", "small", "body", "label", "title", "metric", "hero"]
        for size in required_sizes:
            for font in required_fonts:
                if font not in RESPONSIVE_FONT_SIZES[size]:
                    print(f"✗ Missing font key {font} in size {size}")
                    return False
        print("✓ All font keys present")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_widget_sizes():
    """Test widget size dimensions"""
    try:
        from config.constants import WIDGET_SIZES
        
        expected_sizes = {
            "default": (200, 200),
            "small": (200, 200),
            "medium": (320, 220),
            "large": (400, 220),
            "extra_large": (400, 420)
        }
        
        for size_name, (width, height) in expected_sizes.items():
            actual = WIDGET_SIZES[size_name]
            if actual["width"] != width or actual["height"] != height:
                print(f"✗ Size {size_name}: expected {width}x{height}, got {actual['width']}x{actual['height']}")
                return False
        
        print("✓ All widget sizes correct")
        return True
    except Exception as e:
        print(f"✗ Size test error: {e}")
        return False

def test_responsive_fonts():
    """Test responsive font scaling"""
    try:
        from config.constants import RESPONSIVE_FONT_SIZES
        
        # Test that fonts scale up with widget size
        base_metric = RESPONSIVE_FONT_SIZES["small"]["metric"]
        for size in ["medium", "large", "extra_large"]:
            metric = RESPONSIVE_FONT_SIZES[size]["metric"]
            if metric <= base_metric:
                print(f"✗ Font size doesn't scale up: {size} metric {metric} <= small {base_metric}")
                return False
        
        print("✓ Font scaling works correctly")
        return True
    except Exception as e:
        print(f"✗ Font test error: {e}")
        return False

def test_widget_size_limits():
    """Test compact widgets cannot shrink below readable dimensions"""
    try:
        from config.constants import WIDGET_SIZE_LIMITS

        for size_name in ("small", "default"):
            limits = WIDGET_SIZE_LIMITS[size_name]
            if limits["min_width"] < 190 or limits["min_height"] < 190:
                print(f"FAIL: {size_name} minimum is too small for readable compact widgets")
                return False

        print("OK: Compact widget minimums stay readable")
        return True
    except Exception as e:
        print(f"FAIL: Size limit test error: {e}")
        return False

def test_live_responsive_helper():
    """Test live font scaling uses current widget geometry"""
    try:
        from widgets.responsive_layout import content_wraplength, responsive_font_size

        class FakeWindow:
            size_category = "small"
            _default_width = 200
            _default_height = 200
            PADDING_HORIZONTAL = 20

            def __init__(self, width, height):
                self.width = width
                self.height = height

            def winfo_width(self):
                return self.width

            def winfo_height(self):
                return self.height

        compact = FakeWindow(190, 190)
        roomy = FakeWindow(260, 240)

        if responsive_font_size(compact, "body") > responsive_font_size(roomy, "body"):
            print("FAIL: Compact font is larger than roomy font")
            return False
        if content_wraplength(compact) >= content_wraplength(roomy):
            print("FAIL: Wrap length does not adapt to widget width")
            return False

        print("OK: Live responsive helper adapts to geometry")
        return True
    except Exception as e:
        print(f"FAIL: Live responsive helper test error: {e}")
        return False

def main():
    print("Testing OptiPC Widget Responsive Design Implementation")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Widget Size Tests", test_widget_sizes),
        ("Responsive Font Tests", test_responsive_fonts),
        ("Widget Size Limit Tests", test_widget_size_limits),
        ("Live Responsive Helper Tests", test_live_responsive_helper),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"✗ {test_name} failed")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Implementation is correct.")
        return True
    else:
        print("✗ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
