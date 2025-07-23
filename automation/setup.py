#!/usr/bin/env python3
"""
Setup script for LinkedIn Content Automation
Creates necessary directories and configuration files
"""

import os
import yaml
from pathlib import Path

def create_directory_structure():
    """Create necessary directories"""
    base_path = Path(".")
    directories = [
        "automation/config",
        "automation/data",
        "automation/scripts",
        "automation/logs",
        ".windsurf/workflows"
    ]
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file template"""
    env_content = """# LinkedIn Content Automation Environment Variables
# Copy this to .env and fill in your actual values

# LinkedIn API
LINKEDIN_CLIENT_ID=your_linkedin_app_id
LINKEDIN_CLIENT_SECRET=your_linkedin_app_secret

# OpenAI API (for content analysis)
OPENAI_API_KEY=your_openai_api_key

# Research APIs
NEWS_API_KEY=your_news_api_key
SERPAPI_KEY=your_serpapi_key

# Content Paths
DRAFTS_FOLDER=Drafts
STRATEGY_FILE=enhanced_linkedin_strategy_2024.md

# Automation Settings
AUTO_POST=false
DRY_RUN=true
DEBUG=false
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    print("✅ Created .env.example")

def create_quick_start_script():
    """Create a quick start script"""
    quick_start = """#!/usr/bin/env python3
# Quick Start Script for LinkedIn Content Automation

import subprocess
import sys
import os

def run_content_analysis():
    print("🔍 Running content analysis...")
    subprocess.run([sys.executable, "automation/scripts/content_analyzer.py", "--scan-drafts", "--create-timetable"])

def setup_linkedin_auth():
    print("🔐 Setting up LinkedIn authentication...")
    subprocess.run([sys.executable, "automation/scripts/linkedin_poster.py", "--authenticate"])

def test_posting():
    print("🧪 Testing posting (dry run)...")
    subprocess.run([sys.executable, "automation/scripts/linkedin_poster.py", "--post-now", "Test post", "--dry-run"])

def main():
    print("LinkedIn Content Automation - Quick Start")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("Drafts"):
        print("❌ Error: Please run this from the 'Content - My Articles' directory")
        print("   Expected to find 'Drafts' folder in current directory")
        return
    
    print("Available options:")
    print("1. Analyze content drafts")
    print("2. Setup LinkedIn authentication")
    print("3. Test posting (dry run)")
    print("4. Install dependencies")
    
    choice = input("\\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        run_content_analysis()
    elif choice == "2":
        setup_linkedin_auth()
    elif choice == "3":
        test_posting()
    elif choice == "4":
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "automation/requirements.txt"])
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
"""
    
    with open('quick_start.py', 'w') as f:
        f.write(quick_start)
    print("✅ Created quick_start.py")

def create_readme():
    """Create README file"""
    readme_content = """# LinkedIn Content Automation

Automated content analysis, enhancement, and posting system for LinkedIn.

## Quick Start

1. **Install dependencies:**
   ```bash
   python quick_start.py
   # Choose option 4 to install dependencies
   ```

2. **Analyze your content:**
   ```bash
   python quick_start.py
   # Choose option 1 to analyze drafts
   ```

3. **Setup LinkedIn API (optional):**
   ```bash
   python quick_start.py
   # Choose option 2 to setup authentication
   ```

## Directory Structure

```
Content - My Articles/
├── Drafts/                          # Your draft articles
├── automation/
│   ├── config/                      # Configuration files
│   ├── data/                        # Analysis cache and tokens
│   ├── scripts/                     # Automation scripts
│   └── requirements.txt             # Python dependencies
├── .windsurf/workflows/             # Windsurf workflows
└── quick_start.py                   # Easy setup script
```

## Features

- **AI-Powered Content Analysis**: Automatically categorizes content by theme
- **Smart Scheduling**: Maps content to optimal posting days/times
- **Enhancement Suggestions**: AI-generated improvement recommendations
- **LinkedIn Integration**: Automated posting with OAuth authentication
- **Performance Tracking**: Monitor engagement and lead generation

## Usage

### Content Analysis
```bash
python automation/scripts/content_analyzer.py --scan-drafts --create-timetable
```

### LinkedIn Posting
```bash
# Dry run (recommended first)
python automation/scripts/linkedin_poster.py --schedule-post "Drafts/your-article.md" --day tuesday --dry-run

# Actual posting
python automation/scripts/linkedin_poster.py --schedule-post "Drafts/your-article.md" --day tuesday
```

## Configuration

1. **LinkedIn API**: Update `automation/config/linkedin_api.yaml` with your app credentials
2. **Content Strategy**: Modify `automation/config/content_strategy.yaml` for your posting schedule
3. **Environment**: Copy `.env.example` to `.env` and add your API keys

## Support

For issues or questions, check the workflow documentation in `.windsurf/workflows/content-automation.md`
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("✅ Created README.md")

def main():
    print("Setting up LinkedIn Content Automation...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("Drafts"):
        print("❌ Error: Please run this from the 'Content - My Articles' directory")
        print("   Expected to find 'Drafts' folder in current directory")
        return
    
    create_directory_structure()
    print()
    
    create_env_file()
    print()
    
    create_quick_start_script()
    print()
    
    create_readme()
    print()
    
    print("🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Run: python quick_start.py")
    print("2. Choose option 4 to install dependencies")
    print("3. Choose option 1 to analyze your content")
    print("4. Update automation/config/linkedin_api.yaml with your LinkedIn app credentials")
    print("\nFor detailed instructions, see README.md")

if __name__ == "__main__":
    main()
