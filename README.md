# LinkedIn Content Automation System

Automated LinkedIn content analysis, enhancement, and posting system with voice integration and intelligent scheduling.

## 🎯 Features

- **AI-Powered Content Analysis**: Automatically categorizes drafts by theme (failure prevention, technical deep-dive, reality check, success stories, capacity building)
- **Voice-Authentic Snippet Generation**: Creates LinkedIn posts in your authentic writing style
- **Smart Scheduling**: Maps content to optimal posting days based on enhanced LinkedIn strategy
- **Human Oversight**: Interactive review and approval for all AI suggestions
- **Posted Folder Management**: Organizes completed articles automatically
- **Virtual Environment Isolation**: Clean dependency management
- **Windsurf Workflow Integration**: Easy access via `/content-automation` command

## 🚀 Quick Start

### Option 1: Windsurf Workflow (Recommended)
```bash
/content-automation
```

### Option 2: Direct Command
```bash
python content_automation_workflow.py
```

### Option 3: Interactive Menu
```bash
python run_with_env.py
```

## 📁 Directory Structure

```
Content - My Articles/
├── Drafts/                          # Your draft articles
├── Posted/                          # Completed/posted articles
├── automation/
│   ├── config/                      # Configuration files
│   ├── scripts/                     # Automation scripts
│   ├── data/                        # Analysis cache and tokens
│   └── requirements.txt             # Python dependencies
├── .windsurf/workflows/             # Windsurf workflows
├── content_automation_env/          # Virtual environment
├── futureworks/                     # Future development plans
└── README.md                        # This file
```

## 🎨 Content Strategy

Based on your enhanced LinkedIn strategy for 2024:

- **Monday**: Failure Prevention (10 AM, 12 PM)
- **Tuesday**: Technical Deep-Dive (10 AM-3 PM) - Peak day
- **Wednesday**: Reality Check (10 AM, 1 PM)
- **Thursday**: Success Stories (12 PM-4 PM) - Second peak
- **Friday**: Capacity Building (2 PM)

## 🔧 Setup

1. **Environment Setup** (one-time):
   ```bash
   python run_with_env.py
   # Choose option 7 to update environment
   ```

2. **LinkedIn API Setup** (optional):
   - Create LinkedIn Developer App
   - Update `automation/config/linkedin_api.yaml`

3. **Run Content Analysis**:
   ```bash
   python content_automation_workflow.py
   ```

## 📊 Usage Examples

### Analyze All Drafts
```bash
python content_automation_workflow.py
# Choose option 1
```

### Generate Snippet for Specific File
```bash
python automation/scripts/simple_snippet_generator.py article.md
```

### Move Article to Posted
```bash
python content_automation_workflow.py
# Choose option 3
```

## 🎯 Voice Integration

The system generates LinkedIn snippets using your authentic writing voice:
- **Persona**: Approachable Expert (friendly mentor + sharp industry expert)
- **Tone**: Witty, insightful, and provocative
- **Goal**: Empower readers with actionable value
- **Style**: Clear, dynamic structure with analogies
- **CTAs**: Soft, conversational, community-building

## 🔄 Workflow Integration

This system integrates with Windsurf workflows for seamless content management:
- Automatic theme detection and categorization
- Voice-consistent snippet generation
- Human oversight for all decisions
- Posted folder organization
- Git version control integration

## 📈 Future Enhancements

See `futureworks/` directory for planned features:
- Local desktop application
- Advanced AI integrations
- Multi-platform posting
- Analytics dashboard
- Team collaboration features

## 🤝 Contributing

This is a personal content automation system. For suggestions or improvements, see `futureworks/suggestions.md`.

## 📄 License

Personal use only.

---

*Last updated: July 23, 2025*
*Author: Atwine - Healthcare AI Consultant specializing in LMICs*
