#!/usr/bin/env python3
"""
Simple LinkedIn Snippet Generator
Creates engaging LinkedIn snippets in user's authentic voice
"""

import re
from pathlib import Path

def extract_hook_from_content(content: str) -> str:
    """Extract the most engaging hook from content"""
    lines = content.split('\n')
    
    # Look for subtitle or compelling first paragraph
    for line in lines:
        line = line.strip()
        if line.startswith('**Subtitle:'):
            # Extract subtitle
            subtitle = line.replace('**Subtitle:', '').replace('**', '').strip()
            return subtitle
        elif line and not line.startswith('#') and len(line) > 50:
            # Clean up markdown
            clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            clean_line = re.sub(r'\*(.*?)\*', r'\1', clean_line)
            clean_line = re.sub(r'`(.*?)`', r'\1', clean_line)
            return clean_line
    
    return "Interesting insights ahead..."

def detect_theme(content: str) -> str:
    """Simple theme detection"""
    content_lower = content.lower()
    
    if any(word in content_lower for word in ['fail', 'mistake', 'error', 'disaster', 'prevent']):
        return 'failure_prevention'
    elif any(word in content_lower for word in ['reality', 'truth', 'myth', 'hype', 'assumption']):
        return 'reality_check'
    elif any(word in content_lower for word in ['success', 'result', 'achieve', 'impact', 'roi']):
        return 'success_stories'
    elif any(word in content_lower for word in ['training', 'learn', 'skill', 'guide', 'framework']):
        return 'capacity_building'
    else:
        return 'technical_deep_dive'

def generate_snippet(content: str, title: str) -> str:
    """Generate LinkedIn snippet based on content and theme"""
    hook = extract_hook_from_content(content)
    theme = detect_theme(content)
    
    # Extract any dollar amounts or metrics
    cost_pattern = r'\$[\d,]+|\d+%|[\d,]+ (million|thousand|hours|days|months)'
    costs = re.findall(cost_pattern, content)
    
    if theme == 'failure_prevention':
        emoji = "🚨"
        if costs:
            cost_mention = f"Cost: {costs[0]}"
        else:
            cost_mention = "The price of getting this wrong is steep."
        
        snippet = f"""{emoji} {hook}

{cost_mention}

Here's what I learned from watching projects crash and burn (and how you can sidestep these traps):

👉 Read the full breakdown: [Link in comments]

What's the most expensive mistake you've seen in AI projects? Let me know in the comments.

#AI #ProjectManagement #LessonsLearned #LMIC"""

    elif theme == 'reality_check':
        snippet = f"""🤔 Unpopular opinion: {hook}

While Silicon Valley celebrates the next shiny thing, here's what's actually happening on the ground in LMICs:

The gap between hype and reality is wider than you think.

👉 Full reality check: [Link in comments]

Am I being too harsh, or do you see this disconnect too? What's your take?

#RealityCheck #AI #LMIC #TechRealism #Uganda"""

    elif theme == 'success_stories':
        if costs:
            metric_highlight = f"Result: {costs[0]}"
        else:
            metric_highlight = "Measurable impact achieved."
        
        snippet = f"""✅ Success story: {hook}

{metric_highlight}

This isn't just another feel-good case study. It's a blueprint for what works when you focus on real problems, not flashy solutions.

👉 Full case study with implementation details: [Link in comments]

What success stories from your work would you like to share? I'd love to feature more real-world wins.

#SuccessStory #Impact #AI #Healthcare #LMIC #Results"""

    elif theme == 'capacity_building':
        snippet = f"""🎯 {hook}

Here's the step-by-step framework I use to build sustainable AI capacity in resource-constrained environments:

✓ Practical tools you can implement immediately
✓ Real examples from Uganda and other LMICs
✓ Common pitfalls and how to avoid them

👉 Complete framework: [Link in comments]

What's your biggest challenge in building AI capacity? Let's solve it together in the comments.

#CapacityBuilding #Leadership #AI #Training #Empowerment #LMIC"""

    else:  # technical_deep_dive
        snippet = f"""⚡ {hook}

The technical reality behind the hype:
• Real-world implementation challenges
• Cost-effective solutions for resource-constrained environments
• What actually works (vs. what sounds impressive)

Perfect for technical leaders who need practical guidance, not just theory.

👉 Full technical breakdown: [Link in comments]

What's your experience with AI implementation? Share your insights below.

#TechnicalLeadership #AI #Implementation #LMIC #HealthTech"""

    return snippet

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python simple_snippet_generator.py <filename>")
        return
    
    filename = sys.argv[1]
    file_path = Path("Drafts") / filename
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title
    title = ""
    for line in content.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    snippet = generate_snippet(content, title)
    
    print(f"\n📝 LinkedIn Snippet for {filename}:")
    print("-" * 50)
    print(snippet)
    print("-" * 50)

if __name__ == "__main__":
    main()
