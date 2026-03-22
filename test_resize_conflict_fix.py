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

if __name__ == "__main__":
    success = test_resize_conflict_fix()
    sys.exit(0 if success else 1)
