@echo off
echo OptiPC Multi-Architecture Builder
echo ================================
echo.
echo This will create executables for all architectures:
echo - 64-bit (x64) - Modern Windows systems
echo - 32-bit (x86) - Older Windows systems  
echo - ARM64 - Windows on ARM devices
echo.

pause
python build_multi_arch.py --all

echo.
echo Build process completed!
echo Check the 'builds' folder for release packages.
echo.
pause
