#!/usr/bin/env python3
"""
Debug script to identify resize issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_resize_issue():
    """Debug the resize logic to find the real problem"""
    print("Debugging Widget Resize Issue")
    print("=" * 50)
    
    # Check the actual resize logic in the source
    try:
        from widgets.base_mini_widget import BaseMiniWidget
        import inspect
        
        # Get the resize methods
        on_mouse_down = inspect.getsource(BaseMiniWidget.on_mouse_down)
        on_mouse_drag = inspect.getsource(BaseMiniWidget.on_mouse_drag)
        get_resize_direction = inspect.getsource(BaseMiniWidget.get_resize_direction)
        
        print("1. Checking on_mouse_down method:")
        if "widget_x = event.x_root - self.winfo_rootx()" in on_mouse_down:
            print("   ✓ Uses window-relative coordinates")
        else:
            print("   ✗ May have coordinate issues")
            
        print("\n2. Checking on_mouse_drag method:")
        if 'direction == "e"' in on_mouse_drag:
            print("   ✓ Uses separate direction handling")
        else:
            print("   ✗ Still uses old logic")
            
        print("\n3. Checking get_resize_direction method:")
        if "width = self.winfo_width()" in get_resize_direction:
            print("   ✓ Uses widget dimensions")
        else:
            print("   ✗ May have dimension issues")
            
        # Check for potential issues
        print("\n4. Looking for potential issues:")
        
        # Check if dx/dy calculation is correct
        if "dx = event.x_root - self._resize_start_x" in on_mouse_drag:
            print("   ✓ dx calculation looks correct")
        else:
            print("   ✗ dx calculation may be wrong")
            
        # Check if geometry update is correct
        if "self.geometry(f" in on_mouse_drag:
            print("   ✓ Uses geometry update")
        else:
            print("   ✗ Geometry update issue")
            
        # Print the actual resize logic
        print("\n5. Current resize logic snippet:")
        lines = on_mouse_drag.split('\n')
        for i, line in enumerate(lines):
            if 'direction ==' in line or 'elif direction ==' in line:
                print(f"   {line.strip()}")
                
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_simple_resize():
    """Test a simple resize scenario"""
    print("\n" + "=" * 50)
    print("Testing Simple Resize Scenario")
    print("=" * 50)
    
    # Simulate what happens during resize
    print("Simulating resize from right edge:")
    print("- Start position: x=100, y=100, w=200, h=200")
    print("- Drag right edge by +50 pixels")
    print("- Expected: x=100, y=100, w=250, h=200")
    
    # Test the calculation
    start_x = 100
    start_w = 200
    dx = 50  # Drag right by 50
    
    new_w = max(160, start_w + dx)  # MIN_WIDTH = 160
    
    print(f"- Calculated new_w: {new_w}")
    print(f"- Expected new_w: 250")
    
    if new_w == 250:
        print("✓ Calculation is correct")
    else:
        print("✗ Calculation is wrong")
        
    # Test left edge resize
    print("\nSimulating resize from left edge:")
    print("- Start position: x=100, y=100, w=200, h=200")
    print("- Drag left edge by +50 pixels (move left)")
    print("- Expected: x=150, y=100, w=150, h=200")
    
    start_x = 100
    start_w = 200
    dx = 50  # Drag left by 50
    
    proposed_w = start_w - dx
    if proposed_w >= 160:
        new_w = proposed_w
        new_x = start_x + dx
    
    print(f"- Calculated: new_x={new_x}, new_w={new_w}")
    print(f"- Expected: new_x=150, new_w=150")
    
    if new_x == 150 and new_w == 150:
        print("✓ Left edge calculation is correct")
    else:
        print("✗ Left edge calculation is wrong")

if __name__ == "__main__":
    if debug_resize_issue():
        test_simple_resize()
    
    print("\n" + "=" * 50)
    print("Debug Complete")
    print("If calculations are correct, the issue might be:")
    print("1. Event binding conflicts")
    print("2. Coordinate system issues")
    print("3. Widget hierarchy problems")
    print("4. Multiple resize handlers firing")
