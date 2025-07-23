#!/usr/bin/env python3
"""
Complete Content Automation Workflow
Single command to run the entire LinkedIn content automation process
"""

import os
import sys
import subprocess
from pathlib import Path

def run_complete_workflow():
    """Run the complete content automation workflow"""
    print("🎯 LinkedIn Content Automation Workflow")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    # Step 1: Environment check
    print("1️⃣ Checking environment...")
    env_dir = base_dir / "content_automation_env"
    if env_dir.exists():
        print("   ✅ Virtual environment ready")
    else:
        print("   🔧 Setting up environment...")
        subprocess.run([sys.executable, "-m", "venv", "content_automation_env"])
        print("   ✅ Environment created")
    
    # Step 2: Interactive menu
    print("\n2️⃣ Content Automation Options:")
    print("   1. 📊 Analyze all drafts and generate snippets")
    print("   2. 📝 Generate snippet for specific file")
    print("   3. 📁 Move file to Posted folder")
    print("   4. 🔄 Quick scan (non-interactive)")
    print("   5. 🚀 Setup LinkedIn authentication")
    
    choice = input("\nChoose option (1-5): ").strip()
    
    if choice == "1":
        print("\n📊 Analyzing all drafts...")
        # List all drafts
        drafts_folder = Path("Drafts")
        if drafts_folder.exists():
            md_files = list(drafts_folder.glob("*.md"))
            if md_files:
                print(f"Found {len(md_files)} draft files:")
                for i, file in enumerate(md_files, 1):
                    print(f"   {i}. {file.name}")
                
                print("\n🔍 Generating snippets for all files...")
                for file in md_files:
                    print(f"\n📝 Processing: {file.name}")
                    subprocess.run([sys.executable, "automation/scripts/simple_snippet_generator.py", file.name])
                    
                    # Ask if user wants to move to Posted
                    move = input(f"\n📁 Move {file.name} to Posted folder? (y/n): ").strip().lower()
                    if move == 'y':
                        try:
                            destination = Path("Posted") / file.name
                            file.rename(destination)
                            print(f"   ✅ Moved to Posted folder")
                        except Exception as e:
                            print(f"   ❌ Error moving file: {e}")
            else:
                print("   📭 No draft files found")
        else:
            print("   ❌ Drafts folder not found")
    
    elif choice == "2":
        filename = input("Enter filename (e.g., article1.md): ").strip()
        if filename:
            subprocess.run([sys.executable, "automation/scripts/simple_snippet_generator.py", filename])
    
    elif choice == "3":
        filename = input("Enter filename to move to Posted: ").strip()
        if filename:
            try:
                source = Path("Drafts") / filename
                destination = Path("Posted") / filename
                if source.exists():
                    source.rename(destination)
                    print(f"✅ Moved {filename} to Posted folder")
                else:
                    print(f"❌ File not found: {filename}")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    elif choice == "4":
        print("🔍 Running quick content scan...")
        subprocess.run([sys.executable, "automation/scripts/content_analyzer.py", "--scan-drafts", "--create-timetable"])
    
    elif choice == "5":
        print("🚀 Setting up LinkedIn authentication...")
        subprocess.run([sys.executable, "automation/scripts/linkedin_poster.py", "--authenticate"])
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        run_complete_workflow()
    except KeyboardInterrupt:
        print("\n👋 Workflow cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your setup and try again")
