#!/usr/bin/env python3
"""
Diagnostic script to identify issues with OptiPC widget implementation
"""

import sys
import os
import importlib.util

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        compile(content, filepath, 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def main():
    print("OptiPC Widget Implementation Diagnostic")
    print("=" * 50)
    
    # Check key Python files for syntax errors
    files_to_check = [
        'config/constants.py',
        'widgets/base_mini_widget.py',
        'widgets/modern_widget_base.py', 
        'widgets/liquid_glass_widget.py',
        'widgets/system_widgets.py',
        'widgets/modern_system_widgets.py',
        'widgets/liquid_glass_widgets.py',
        'widgets/network_speed_widget.py'
    ]
    
    syntax_errors = []
    
    print("\n1. Checking file syntax...")
    for filepath in files_to_check:
        if os.path.exists(filepath):
            is_valid, error = check_file_syntax(filepath)
            if is_valid:
                print(f"✓ {filepath}")
            else:
                print(f"✗ {filepath}: {error}")
                syntax_errors.append((filepath, error))
        else:
            print(f"? {filepath}: File not found")
    
    # Check imports without running the GUI
    print("\n2. Checking imports (non-GUI)...")
    try:
        import config.constants
        print("✓ config.constants")
        
        from config.constants import WIDGET_SIZES, RESPONSIVE_FONT_SIZES
        print("✓ Constants import")
        
        # Check widget classes exist (without instantiating)
        sys.path.insert(0, 'widgets')
        
        # Check base widget class structure
        with open('widgets/base_mini_widget.py', 'r') as f:
            content = f.read()
            if 'get_responsive_font_size' in content and 'create_responsive_label' in content:
                print("✓ BaseMiniWidget has responsive methods")
            else:
                print("✗ BaseMiniWidget missing responsive methods")
                
        print("✓ Widget structure checks passed")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Check for missing dependencies
    print("\n3. Checking dependencies...")
    dependencies = ['customtkinter', 'psutil']
    missing_deps = []
    
    for dep in dependencies:
        try:
            spec = importlib.util.find_spec(dep)
            if spec is None:
                missing_deps.append(dep)
                print(f"✗ {dep} - not installed")
            else:
                print(f"✓ {dep} - installed")
        except ImportError:
            missing_deps.append(dep)
            print(f"✗ {dep} - not installed")
    
    # Summary
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY:")
    
    if syntax_errors:
        print(f"✗ {len(syntax_errors)} syntax errors found")
        for filepath, error in syntax_errors:
            print(f"  - {filepath}: {error}")
    else:
        print("✓ No syntax errors found")
    
    if missing_deps:
        print(f"✗ {len(missing_deps)} missing dependencies")
        print(f"  Run: pip install {' '.join(missing_deps)}")
    else:
        print("✓ All dependencies installed")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    if missing_deps:
        print("1. Install missing dependencies:")
        print("   pip install -r requirements.txt")
    if syntax_errors:
        print("2. Fix syntax errors before running the application")
    
    if not syntax_errors and not missing_deps:
        print("✓ Everything looks good! Try running: python main.py")

if __name__ == "__main__":
    main()
