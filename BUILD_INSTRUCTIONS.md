# OptiPC Multi-Architecture Build Instructions

This guide explains how to create executables for different Windows architectures.

## Quick Start

### Option 1: Build for Current Architecture
```bash
python build_multi_arch.py
```

### Option 2: Build for All Architectures
```bash
python build_multi_arch.py --all
```

### Option 3: Build for Specific Architecture
```bash
python build_multi_arch.py --x64    # 64-bit systems
python build_multi_arch.py --x86    # 32-bit systems  
python build_multi_arch.py --arm64  # ARM64 devices
```

### Option 4: Use Batch File (Windows)
Double-click `build_all.bat` to build all architectures

## Architecture Support

| Architecture | Target | Description | File Size |
|-------------|----------|-------------|------------|
| x64 | x86_64 | Modern 64-bit Windows systems | ~20MB |
| x86 | x86 | Older 32-bit Windows systems | ~18MB |
| ARM64 | arm64 | Windows on ARM devices (Surface Pro X, etc.) | ~19MB |

## Output Files

After building, you'll find release packages in the `builds/` folder:

```
builds/
├── OptiPC_x64_Release.zip      # 64-bit version
├── OptiPC_x86_Release.zip      # 32-bit version
└── OptiPC_arm64_Release.zip    # ARM64 version
```

Each ZIP file contains:
- `OptiPC_[arch].exe` - The executable
- `README.md` - Main documentation
- `README_FRIEND.md` - User-friendly guide
- `TROUBLESHOOTING_FRIEND.md` - Troubleshooting help
- `INSTALL.txt` - Installation instructions

## Distribution Instructions

### For Users:
1. **Choose the right architecture:**
   - Most modern PCs: Use `OptiPC_x64_Release.zip`
   - Very old PCs: Use `OptiPC_x86_Release.zip`
   - ARM devices: Use `OptiPC_arm64_Release.zip`

2. **Installation:**
   - Extract the ZIP file to any folder
   - Run `OptiPC_[arch].exe`
   - No installation required - fully portable!

3. **If Antivirus Blocks:**
   - Add the executable to antivirus exceptions
   - The app is safe, but some AVs flag Python apps

### For Developers:
1. **Share the ZIP files** - not just the EXE
2. **Include documentation** - helps users understand features
3. **Test on each architecture** before distribution
4. **Consider code signing** for professional distribution

## Build Requirements

- Python 3.8 or higher
- PyInstaller (automatically installed)
- All requirements from `requirements.txt`

## Troubleshooting

### Build Issues:
- **"PyInstaller not found"**: Run the script twice (first installs it)
- **"Permission denied"**: Run as administrator
- **"Module not found"**: Ensure all requirements are installed

### Runtime Issues:
- **"DLL not found"**: Install Microsoft Visual C++ Redistributable
- **"App won't start"**: Run as administrator
- **"Missing assets"**: Ensure all files are extracted together

## Advanced Options

### Custom Build Configuration:
Edit `build_multi_arch.py` to modify:
- Hidden imports
- Icon paths
- Compression settings
- Architecture targets

### Manual PyInstaller:
```bash
python -m PyInstaller --name OptiPC_x64 --onefile --windowed --target-architecture=x86_64 main.py
```

## File Sizes (Approximate)

| Component | Size |
|-----------|-------|
| Base executable | 15-20MB |
| Assets folder | 2-5MB |
| Documentation | 50KB |
| Total ZIP | 20-30MB |

## Security Notes

- The executable includes all dependencies
- No network access required for basic functionality
- All data is stored locally
- Optional: Code sign executables for enterprise distribution

## Support

For build issues:
1. Check Python version (3.8+ required)
2. Update PyInstaller: `pip install --upgrade pyinstaller`
3. Clean build folders: Delete `build/` and `dist/`
4. Check system architecture with `python -c "import platform; print(platform.machine())"`

For user issues:
- Direct users to `TROUBLESHOOTING_FRIEND.md`
- Ensure correct architecture is selected
- Verify Windows version compatibility
