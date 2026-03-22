# Double-Click Close and Reset Feature

## Overview
All widgets now support **double-click to close and reset** functionality. When you double-click on either the **title bar** or the **close button (×)** of any widget, it will:
1. Close the widget
2. Reset its position and size to default values
3. Stop all running operations
4. Clear saved geometry data

## Implementation Details

### Features Added

#### 1. Double-Click Detection
- **Detection Window**: 300 milliseconds between clicks
- **Target Areas**: 
  - Title bar and title label
  - Close button (×)
- **Single Click**: 
  - Title bar → Drag widget (unchanged behavior)
  - Close button → Close widget (unchanged behavior)
- **Double Click**: Close and reset widget (both areas)

#### 2. Reset Functionality
- **Geometry Reset**: Removes saved position/size from state file
- **Default Position**: Widget will reopen at default coordinates
- **Default Size**: Widget will reopen with standard dimensions
- **State Preservation**: Visibility state is maintained

#### 3. Widget Types Supported
- ✅ **BaseMiniWidget** - Original widget style
- ✅ **ModernMiniWidget** - Modern Apple-style widgets
- ✅ **LiquidGlassWidget** - Liquid glass style widgets

### Technical Implementation

#### Base Widget Classes Updated
```python
# Added to all widget base classes
self._last_click_time = 0
self._double_click_delay = 300  # milliseconds

# Event binding for title bar
self.topbar.bind("<ButtonPress-1>", self.on_title_click)
self.title_label.bind("<ButtonPress-1>", self.on_title_click)

# Event binding for close button
self.close_button.bind("<ButtonPress-1>", self.on_close_button_click)

# Key methods
def on_title_click(self, event) -> None:
    """Handle title bar clicks with double-click detection"""
    
def on_close_button_click(self, event) -> None:
    """Handle close button clicks with double-click detection"""
    
def reset_and_close(self) -> None:
    """Close widget and reset to default position/size"""
```

#### Widget State Service Enhanced
```python
def reset_widget_geometry(self, key: str) -> None:
    """Remove saved geometry for a widget, forcing it to use defaults"""
```

#### Main Application Integration
```python
def reset_widget_geometry(self, key: str) -> None:
    """Reset widget geometry to default values"""
    self.widget_state_service.reset_widget_geometry(key)
```

## User Experience

### How to Use

#### Option 1: Double-Click Title Bar
1. **Double click** on widget title bar → Close and reset widget
2. **Single click** on title bar → Drag widget (unchanged)

#### Option 2: Double-Click Close Button
1. **Double click** on close button (×) → Close and reset widget
2. **Single click** on close button (×) → Close widget (unchanged)

### What Happens on Double-Click
1. Widget immediately closes
2. Saved position/size is cleared from configuration
3. Next time widget opens, it appears at default position with default size
4. All widget operations are properly stopped

### Benefits
- **Flexible Options**: Double-click works on both title bar and close button
- **Quick Reset**: Easy way to reset mispositioned widgets
- **Clean State**: Removes corrupted geometry data
- **User Friendly**: Intuitive double-click gesture
- **Consistent**: Works across all widget styles
- **Backward Compatible**: Single-click behavior unchanged

## Files Modified

### Core Files
- `widgets/base_mini_widget.py` - Added double-click logic for title bar and close button
- `widgets/modern_widget_base.py` - Added double-click logic for title bar and close button  
- `widgets/liquid_glass_widget.py` - Added double-click logic for title bar and close button

### Service Files
- `services/widget_state_service.py` - Added reset method
- `app.py` - Added reset method integration

### Test Files
- `test_double_click.py` - Title bar double-click verification
- `test_close_button_double_click.py` - Close button double-click verification

## Default Widget Positions

When widgets are reset, they will appear at these default positions:

| Widget | Default X | Default Y | Default Size |
|--------|------------|------------|--------------|
| CPU | 40 | 40 | 200x200 |
| RAM | 360 | 40 | 200x200 |
| GPU | 680 | 40 | 200x200 |
| Clock | 400 | 40 | 200x200 |
| Uptime | 720 | 40 | 200x200 |
| Partitions | 40 | 250 | 400x220 |
| Storage | 540 | 250 | 400x220 |
| Calendar | 40 | 570 | 400x420 |
| Network Speed | 1020 | 40 | 320x220 |

## Troubleshooting

### Double-Click Not Working
- Ensure clicking on title bar OR close button (×)
- Clicks must be within 300ms of each other
- Check that widget isn't being resized (resize takes priority)

### Widget Not Resetting
- Check if widget has a widget_key assigned
- Verify widget state service is accessible
- Ensure no errors in widget state file

### Still Issues
- Restart the application to clear any state conflicts
- Delete widget state file: `~/OptiPCConfig/widget_state.json`
- Reopen widgets to establish fresh state

## Implementation Status
✅ **Complete** - All double-click close and reset functionality implemented for both title bar and close button.
