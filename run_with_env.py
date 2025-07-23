#!/usr/bin/env python3
"""
Environment Management Script
Ensures all content automation scripts run in the dedicated virtual environment
"""

import os
import sys
import subprocess
from pathlib import Path

class EnvironmentManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.env_dir = self.base_dir / "content_automation_env"
        self.scripts_dir = self.base_dir / "automation" / "scripts"
        
        # Platform-specific paths
        if os.name == 'nt':  # Windows
            self.python_exe = self.env_dir / "Scripts" / "python.exe"
            self.pip_exe = self.env_dir / "Scripts" / "pip.exe"
        else:  # Unix/Linux/Mac
            self.python_exe = self.env_dir / "bin" / "python"
            self.pip_exe = self.env_dir / "bin" / "pip"
    
    def ensure_environment(self):
        """Ensure virtual environment exists and is properly set up"""
        if not self.env_dir.exists():
            print("🔧 Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(self.env_dir)])
            print("✅ Virtual environment created")
        
        if not self.python_exe.exists():
            print("❌ Virtual environment seems corrupted. Recreating...")
            import shutil
            shutil.rmtree(self.env_dir)
            subprocess.run([sys.executable, "-m", "venv", str(self.env_dir)])
            print("✅ Virtual environment recreated")
        
        # Install/update requirements
        requirements_file = self.base_dir / "automation" / "requirements.txt"
        if requirements_file.exists():
            print("📦 Installing/updating dependencies...")
            subprocess.run([str(self.pip_exe), "install", "-r", str(requirements_file)], 
                         capture_output=True)
            print("✅ Dependencies updated")
    
    def run_script(self, script_name: str, args: list = None):
        """Run a script in the virtual environment"""
        self.ensure_environment()
        
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False
        
        cmd = [str(self.python_exe), str(script_path)]
        if args:
            cmd.extend(args)
        
        print(f"🚀 Running: {' '.join(cmd)}")
        print(f"📁 Working directory: {self.base_dir}")
        
        # Change to base directory and run
        original_cwd = os.getcwd()
        try:
            os.chdir(self.base_dir)
            result = subprocess.run(cmd)
            return result.returncode == 0
        finally:
            os.chdir(original_cwd)
    
    def interactive_menu(self):
        """Interactive menu for running content automation tasks"""
        print("🎯 LinkedIn Content Automation")
        print("=" * 50)
        print("Environment:", "✅ Active" if self.python_exe.exists() else "❌ Not found")
        print()
        
        options = {
            "1": ("Analyze content (interactive)", "enhanced_content_analyzer.py", ["--interactive-scan"]),
            "2": ("Generate snippet for specific file", None, None),
            "3": ("Move file to Posted folder", None, None),
            "4": ("Quick content scan (non-interactive)", "content_analyzer.py", ["--scan-drafts", "--create-timetable"]),
            "5": ("Setup LinkedIn authentication", "linkedin_poster.py", ["--authenticate"]),
            "6": ("Test posting (dry run)", "linkedin_poster.py", ["--post-now", "Test content", "--dry-run"]),
            "7": ("Update environment", None, None),
            "8": ("Exit", None, None)
        }
        
        for key, (desc, _, _) in options.items():
            print(f"{key}. {desc}")
        
        choice = input("\nChoose option (1-8): ").strip()
        
        if choice == "1":
            return self.run_script("enhanced_content_analyzer.py", ["--interactive-scan"])
        
        elif choice == "2":
            filename = input("Enter filename (e.g., article1.md): ").strip()
            if filename:
                return self.run_script("enhanced_content_analyzer.py", ["--generate-snippet", filename])
        
        elif choice == "3":
            filename = input("Enter filename to move to Posted: ").strip()
            if filename:
                return self.run_script("enhanced_content_analyzer.py", ["--move-to-posted", filename])
        
        elif choice == "4":
            return self.run_script("content_analyzer.py", ["--scan-drafts", "--create-timetable"])
        
        elif choice == "5":
            return self.run_script("linkedin_poster.py", ["--authenticate"])
        
        elif choice == "6":
            return self.run_script("linkedin_poster.py", ["--post-now", "Test content", "--dry-run"])
        
        elif choice == "7":
            self.ensure_environment()
            print("✅ Environment updated")
            return True
        
        elif choice == "8":
            print("👋 Goodbye!")
            return False
        
        else:
            print("❌ Invalid choice")
            return True

def main():
    env_manager = EnvironmentManager()
    
    # Check if script arguments were provided
    if len(sys.argv) > 1:
        script_name = sys.argv[1]
        script_args = sys.argv[2:] if len(sys.argv) > 2 else []
        env_manager.run_script(script_name, script_args)
    else:
        # Interactive mode
        while True:
            try:
                if not env_manager.interactive_menu():
                    break
                input("\nPress Enter to continue...")
                print("\n" + "="*50 + "\n")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

if __name__ == "__main__":
    main()
