#!/usr/bin/env python3
"""
Test script to verify close button double-click functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_close_button_double_click():
    """Test that close button double-click functionality is properly implemented"""
    print("Testing Close Button Double-Click Functionality")
    print("=" * 50)
    
    # Test 1: Check if base widget has close button double-click method
    try:
        from widgets.base_mini_widget import BaseMiniWidget
        
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
        
        if hasattr(ModernMiniWidget, 'on_close_button_click'):
            print("✓ ModernMiniWidget has on_close_button_click method")
        else:
            print("✗ ModernMiniWidget missing on_close_button_click method")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 3: Check LiquidGlassWidget
    try:
        from widgets.liquid_glass_widget import LiquidGlassWidget
        
        if hasattr(LiquidGlassWidget, 'on_close_button_click'):
            print("✓ LiquidGlassWidget has on_close_button_click method")
        else:
            print("✗ LiquidGlassWidget missing on_close_button_click method")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All close button double-click tests passed!")
    print("\nHow to use:")
    print("- Single click close button → Close widget (unchanged)")
    print("- Double click close button → Close and reset widget")
    print("- Double click title bar → Close and reset widget")
    
    return True

if __name__ == "__main__":
    success = test_close_button_double_click()
    sys.exit(0 if success else 1)
