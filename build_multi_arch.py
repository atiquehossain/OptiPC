"""
Multi-Architecture Build Script for OptiPC
Creates executables for different Windows architectures (x86, x64, ARM64)
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import zipfile
import datetime

class MultiArchBuilder:
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.build_dir = self.current_dir / "builds"
        self.build_dir.mkdir(exist_ok=True)
        
        # Architecture configurations
        self.architectures = {
            "x64": {
                "name": "64-bit (x64)",
                "target": "x86_64",
                "description": "For modern 64-bit Windows systems"
            },
            "x86": {
                "name": "32-bit (x86)", 
                "target": "x86",
                "description": "For older 32-bit Windows systems"
            },
            "arm64": {
                "name": "ARM64",
                "target": "arm64", 
                "description": "For Windows on ARM devices (Surface Pro X, etc.)"
            }
        }
    
    def install_pyinstaller(self):
        """Install PyInstaller if not already installed"""
        try:
            import PyInstaller
            print("✓ PyInstaller already installed")
            return True
        except ImportError:
            print("Installing PyInstaller...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
                print("✓ PyInstaller installed successfully")
                return True
            except subprocess.CalledProcessError:
                print("✗ Failed to install PyInstaller")
                return False
    
    def clean_build_dirs(self):
        """Clean previous build directories"""
        dirs_to_clean = ["build", "dist", "__pycache__"]
        for dir_name in dirs_to_clean:
            dir_path = self.current_dir / dir_name
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    print(f"✓ Cleaned {dir_name} directory")
                except PermissionError:
                    print(f"⚠ Could not clean {dir_name} directory - files may be in use")
                    print(f"  Please close any running OptiPC instances and try again")
    
    def build_for_architecture(self, arch_key):
        """Build executable for specific architecture"""
        arch_config = self.architectures[arch_key]
        print(f"\n🔨 Building for {arch_config['name']} ({arch_config['description']})")
        
        # Architecture-specific PyInstaller command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            f"--name=OptiPC_{arch_key}",
            "--onefile",
            "--windowed", 
            f"--target-architecture={arch_config['target']}",
            "--clean",
            "--distpath=dist",
            "--workpath=build",
            "--icon=assets/optipc_icon.ico" if Path("assets/optipc_icon.ico").exists() else "",
            "--add-data=assets;assets",
            "--hidden-import=customtkinter",
            "--hidden-import=psutil", 
            "--hidden-import=GPUtil",
            "--hidden-import=pystray",
            "--hidden-import=PIL",
            "--hidden-import=PIL.Image",
            "--hidden-import=threading",
            "--hidden-import=json",
            "--hidden-import=os",
            "--hidden-import=sys",
            "--hidden-import=subprocess",
            "--hidden-import=shutil",
            "--hidden-import=pathlib",
            "--hidden-import=datetime",
            "--uac-admin",  # Require administrator privileges
            "main.py"
        ]
        
        # Remove empty icon parameter
        cmd = [arg for arg in cmd if arg]
        
        try:
            subprocess.check_call(cmd, cwd=self.current_dir)
            print(f"✓ Successfully built {arch_key} executable")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to build {arch_key}: {e}")
            return False
    
    def create_release_package(self, arch_key):
        """Create a release package with executable and documentation"""
        arch_config = self.architectures[arch_key]
        exe_name = f"OptiPC_{arch_key}.exe"
        source_exe = self.current_dir / "dist" / exe_name
        
        if not source_exe.exists():
            print(f"✗ Executable not found: {source_exe}")
            return False
        
        # Create architecture-specific release directory
        release_dir = self.build_dir / f"OptiPC_{arch_key}_Release"
        release_dir.mkdir(exist_ok=True)
        
        # Copy executable
        dest_exe = release_dir / exe_name
        shutil.copy2(source_exe, dest_exe)
        
        # Copy documentation
        docs_to_copy = ["README.md", "README_FRIEND.md", "TROUBLESHOOTING_FRIEND.md"]
        for doc in docs_to_copy:
            doc_path = self.current_dir / doc
            if doc_path.exists():
                shutil.copy2(doc_path, release_dir)
        
        # Create installation instructions
        install_instructions = f"""OptiPC - {arch_config['name']} Release
{arch_config['description']}

Installation:
1. Extract all files to a folder
2. Run OptiPC_{arch_key}.exe
3. No installation required - portable application

System Requirements:
- Windows 10 or higher
- {arch_config['description']}

File Information:
- Executable: {exe_name}
- Size: {dest_exe.stat().st_size / (1024*1024):.1f} MB
- Built: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Troubleshooting:
- If antivirus blocks the executable, add it to exceptions
- If the app doesn't start, run as administrator
- For more help, see TROUBLESHOOTING_FRIEND.md

© 2024 OptiPC
"""
        
        with open(release_dir / "INSTALL.txt", "w", encoding="utf-8") as f:
            f.write(install_instructions)
        
        # Create ZIP archive
        zip_name = f"OptiPC_{arch_key}_Release.zip"
        zip_path = self.build_dir / zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in release_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(release_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✓ Created release package: {zip_name}")
        return True
    
    def build_all_architectures(self):
        """Build executables for all architectures"""
        print("🚀 OptiPC Multi-Architecture Builder (With Admin Rights)")
        print("=" * 60)
        
        # Install PyInstaller
        if not self.install_pyinstaller():
            return False
        
        # Clean previous builds
        self.clean_build_dirs()
        
        # Build for each architecture
        successful_builds = []
        for arch_key in self.architectures.keys():
            print(f"\n🔨 Building {arch_key} with administrator privileges...")
            if self.build_for_architecture(arch_key):
                if self.create_release_package(arch_key):
                    successful_builds.append(arch_key)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Build Summary (All with Admin Rights):")
        for arch_key in self.architectures.keys():
            status = "✓ Success" if arch_key in successful_builds else "✗ Failed"
            arch_config = self.architectures[arch_key]
            print(f"  {arch_config['name']}: {status}")
        
        if successful_builds:
            print(f"\n📦 Release packages created in: {self.build_dir}")
            print("\n📋 Distribution Instructions:")
            print("1. Share the ZIP files for each architecture")
            print("2. Users extract and run the appropriate executable")
            print("3. All versions will automatically prompt for admin rights")
            print("4. No installation required - fully portable")
        
        return len(successful_builds) > 0
    
    def build_single_architecture(self, arch_key=None):
        """Build for a specific architecture"""
        if arch_key is None:
            # Auto-detect current architecture
            machine = platform.machine().lower()
            if machine in ['amd64', 'x86_64']:
                arch_key = 'x64'
            elif machine in ['i386', 'i686']:
                arch_key = 'x86'
            elif machine in ['arm64', 'aarch64']:
                arch_key = 'arm64'
            else:
                arch_key = 'x64'  # Default to x64
        
        if arch_key not in self.architectures:
            print(f"❌ Invalid architecture: {arch_key}")
            print(f"Available: {', '.join(self.architectures.keys())}")
            return False
        
        print(f"🎯 Building single architecture: {arch_key}")
        
        # Install PyInstaller
        if not self.install_pyinstaller():
            return False
        
        # Clean previous builds
        self.clean_build_dirs()
        
        # Build and package
        if self.build_for_architecture(arch_key):
            if self.create_release_package(arch_key):
                print(f"\n✅ Build completed successfully!")
                print(f"📦 Release package: {self.build_dir}/OptiPC_{arch_key}_Release.zip")
                return True
        
        print(f"\n❌ Build failed for {arch_key}")
        return False

def main():
    builder = MultiArchBuilder()
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--all":
            builder.build_all_architectures()
        elif arg == "--x64":
            builder.build_single_architecture("x64")
        elif arg == "--x86":
            builder.build_single_architecture("x86")
        elif arg == "--arm64":
            builder.build_single_architecture("arm64")
        elif arg == "--help":
            print("""
OptiPC Multi-Architecture Builder

Usage:
  python build_multi_arch.py [option]

Options:
  --all        Build for all architectures (x64, x86, arm64)
  --x64        Build only for 64-bit systems
  --x86        Build only for 32-bit systems  
  --arm64      Build only for ARM64 systems
  [no args]    Build for current system architecture

Examples:
  python build_multi_arch.py --all
  python build_multi_arch.py --x64
  python build_multi_arch.py
            """)
        else:
            print(f"❌ Unknown option: {arg}")
            print("Use --help for available options")
    else:
        # Build for current architecture
        builder.build_single_architecture()
    
    if len(sys.argv) <= 1:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
