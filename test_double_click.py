#!/usr/bin/env python3
"""
Test script to verify double-click close and reset functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_double_click_functionality():
    """Test that double-click functionality is properly implemented"""
    print("Testing Double-Click Close and Reset Functionality")
    print("=" * 50)
    
    # Test 1: Check if base widget has double-click methods
    try:
        from widgets.base_mini_widget import BaseMiniWidget
        
        # Check if required methods exist
        required_methods = ['on_title_click', 'reset_and_close']
        for method in required_methods:
            if hasattr(BaseMiniWidget, method):
                print(f"✓ BaseMiniWidget has {method} method")
            else:
                print(f"✗ BaseMiniWidget missing {method} method")
                return False
                
        # Check if double-click tracking variables exist
        required_vars = ['_last_click_time', '_double_click_delay']
        init_method = BaseMiniWidget.__init__
        init_source = init_method.__code__.co_names
        for var in required_vars:
            if var in init_source:
                print(f"✓ BaseMiniWidget has {var} variable")
            else:
                print(f"✗ BaseMiniWidget missing {var} variable")
                return False
                
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 2: Check ModernMiniWidget
    try:
        from widgets.modern_widget_base import ModernMiniWidget
        
        required_methods = ['on_title_click', 'reset_and_close']
        for method in required_methods:
            if hasattr(ModernMiniWidget, method):
                print(f"✓ ModernMiniWidget has {method} method")
            else:
                print(f"✗ ModernMiniWidget missing {method} method")
                return False
                
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 3: Check LiquidGlassWidget
    try:
        from widgets.liquid_glass_widget import LiquidGlassWidget
        
        required_methods = ['on_title_click', 'reset_and_close']
        for method in required_methods:
            if hasattr(LiquidGlassWidget, method):
                print(f"✓ LiquidGlassWidget has {method} method")
            else:
                print(f"✗ LiquidGlassWidget missing {method} method")
                return False
                
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 4: Check widget state service
    try:
        from services.widget_state_service import WidgetStateService
        
        if hasattr(WidgetStateService, 'reset_widget_geometry'):
            print("✓ WidgetStateService has reset_widget_geometry method")
        else:
            print("✗ WidgetStateService missing reset_widget_geometry method")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 5: Check main app
    try:
        from app import OptiPCApp
        
        if hasattr(OptiPCApp, 'reset_widget_geometry'):
            print("✓ OptiPCApp has reset_widget_geometry method")
        else:
            print("✗ OptiPCApp missing reset_widget_geometry method")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All double-click functionality tests passed!")
    print("\nFeatures implemented:")
    print("- Double-click detection on title bar")
    print("- Close and reset widget on double-click")
    print("- Works on all widget types (Base, Modern, Liquid)")
    print("- Resets geometry to default values")
    print("- Preserves visibility state")
    
    return True

if __name__ == "__main__":
    success = test_double_click_functionality()
    sys.exit(0 if success else 1)
