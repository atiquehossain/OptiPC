# Widget Size Standardization & Responsive Design

## Overview
All widgets in OptiPC now use standardized dimensions and responsive typography for consistency and better visual layout across different widget sizes.

## Standard Widget Sizes

### Small Widgets (200x200)
Used for compact system monitoring widgets:
- CPU Widget
- RAM Widget  
- GPU Widget
- Clock Widget
- Uptime Widget

### Medium Widgets (320x220)
Used for widgets that need more horizontal space:
- Network Speed Widget

### Large Widgets (400x220)
Used for widgets that display lists or detailed information:
- Storage Widget
- Partitions Widget

### Extra Large Widgets (400x420)
Used for complex widgets with extensive content:
- Calendar Widget

## Responsive Typography

### Font Size Categories
- **tiny**: Smallest text for compact elements
- **small**: Secondary information and details
- **body**: Main content text
- **label**: Form labels and headers
- **title**: Section titles
- **metric**: Large numbers and percentages
- **hero**: Largest display text

### Responsive Font Scaling
Font sizes automatically scale based on widget dimensions:

| Size Category | tiny | small | body | label | title | metric | hero |
|---------------|------|-------|------|-------|-------|--------|------|
| Small (200x200) | 9px | 11px | 12px | 13px | 15px | 18px | 20px |
| Medium (320x220) | 10px | 12px | 13px | 14px | 16px | 22px | 24px |
| Large (400x220) | 11px | 13px | 14px | 15px | 18px | 26px | 28px |
| Extra Large (400x420) | 12px | 14px | 15px | 16px | 20px | 30px | 32px |

## Implementation Details

### Constants Added
```python
WIDGET_SIZES = {
    "small": {"width": 200, "height": 200},
    "medium": {"width": 320, "height": 220}, 
    "large": {"width": 400, "height": 220},
    "extra_large": {"width": 400, "height": 420},
    "default": {"width": 200, "height": 200},
}

RESPONSIVE_FONT_SIZES = {
    "small": {"tiny": 9, "small": 11, "body": 12, ...},
    "medium": {"tiny": 10, "small": 12, "body": 13, ...},
    # ... other size categories
}
```

### Widget Base Classes Updated
- `BaseMiniWidget` - Added responsive font support
- `ModernMiniWidget` - Added responsive font support  
- `LiquidGlassWidget` - Added responsive font support

### Responsive Helper Methods
- `get_responsive_font_size(size_key)` - Get scaled font size
- `create_responsive_label()` - Create labels with responsive fonts
- Updated all widget creation methods to use responsive sizing

### Usage Example
```python
# Using standard size with responsive fonts
class MyWidget(BaseMiniWidget):
    def __init__(self, parent):
        super().__init__(parent, "My Widget", size_category="small")
        self.label = self.create_responsive_label(self.body, "Text", "title")

# Using custom size (overrides standard)
class MyCustomWidget(BaseMiniWidget):
    def __init__(self, parent):
        super().__init__(parent, "My Widget", width=250, height=180)
```

## Responsive Elements

### Text Elements
- All text scales proportionally with widget size
- Calendar dates, button text, and labels all responsive
- Metric displays (CPU %, RAM usage) scale appropriately

### Calendar Widget
- Day headers scale with widget size
- Calendar buttons use responsive fonts
- Month/year title adjusts to widget dimensions
- Date/time display scales properly

### Progress Bars and UI Elements
- Progress bar widths adjust to widget size
- Button dimensions scale appropriately
- Padding and margins are proportional

## Benefits
1. **Consistency** - Uniform dimensions and text scaling across widget types
2. **Readability** - Text remains readable at all widget sizes
3. **Maintainability** - Easy to adjust sizes globally via constants
4. **Flexibility** - Custom sizes still supported when needed
5. **Visual Harmony** - Better overall application layout with proportional scaling
6. **Responsive Design** - All elements adapt to widget dimensions automatically

## Migration Notes
- All existing widgets migrated to 200x200 small size (up from 170x170)
- Responsive typography automatically applied to all text elements
- Calendar and complex widgets properly scale their interactive elements
- Backward compatibility maintained for existing saved widget geometries
