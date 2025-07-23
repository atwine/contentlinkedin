#!/usr/bin/env python3
"""
Enhanced LinkedIn Content Analyzer with Voice Integration and Snippet Generation
Analyzes content, generates engaging snippets, and manages posting workflow
"""

import os
import json
import yaml
import argparse
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import re

class EnhancedContentAnalyzer:
    def __init__(self, config_path: str = "automation/config/content_strategy.yaml"):
        self.config_path = config_path
        self.load_config()
        self.drafts_folder = Path("Drafts")
        self.posted_folder = Path("Posted")
        self.voice_file = Path("my_writing_voice_prompt.md")
        self.strategy_file = Path("enhanced_linkedin_strategy_2024.md")
        self.database_file = Path("automation/data/content_database.json")
        self.ensure_directories()
        self.load_voice_guidelines()
        
    def load_config(self):
        """Load content strategy configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # Default configuration
            self.config = {
                'posting_schedule': {
                    'monday': {'theme': 'Failure Prevention', 'optimal_times': ['10:00', '12:00']},
                    'tuesday': {'theme': 'Technical Deep-Dive', 'optimal_times': ['10:00', '11:00', '14:00', '15:00']},
                    'wednesday': {'theme': 'Reality Check', 'optimal_times': ['10:00', '13:00']},
                    'thursday': {'theme': 'Success Stories', 'optimal_times': ['12:00', '13:00', '14:00', '15:00', '16:00']},
                    'friday': {'theme': 'Capacity Building', 'optimal_times': ['14:00']}
                }
            }
    
    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        self.database_file.parent.mkdir(parents=True, exist_ok=True)
        self.posted_folder.mkdir(exist_ok=True)
        
    def load_voice_guidelines(self):
        """Load writing voice guidelines"""
        try:
            with open(self.voice_file, 'r', encoding='utf-8') as f:
                self.voice_content = f.read()
                
            # Extract key voice elements
            self.voice_guidelines = {
                'persona': 'Approachable Expert - friendly mentor and sharp industry expert',
                'tone': 'witty, insightful, and provocative',
                'goal': 'empower the reader with actionable value',
                'style': 'clear, dynamic structure with analogies for complex topics',
                'cta_style': 'soft, conversational, community-building'
            }
        except FileNotFoundError:
            print("⚠️  Voice guidelines file not found. Using default voice.")
            self.voice_guidelines = {
                'persona': 'Expert consultant',
                'tone': 'professional and engaging',
                'goal': 'provide value',
                'style': 'clear and structured',
                'cta_style': 'engaging'
            }
    
    def analyze_content_theme(self, content: str, filename: str) -> Dict:
        """Analyze content to determine theme and optimal posting day"""
        content_lower = content.lower()
        
        # Enhanced theme analysis with more sophisticated scoring
        theme_scores = {
            'failure_prevention': 0,
            'technical_deep_dive': 0,
            'reality_check': 0,
            'success_stories': 0,
            'capacity_building': 0
        }
        
        # Failure Prevention keywords (weighted)
        failure_keywords = {
            'fail': 3, 'failure': 3, 'mistake': 2, 'error': 2, 'problem': 2, 
            'wrong': 2, 'disaster': 3, 'crisis': 3, 'prevent': 3, 'avoid': 3, 
            'trap': 3, 'pitfall': 3, 'warning': 2, 'danger': 2
        }
        
        # Technical Deep-Dive keywords (weighted)
        technical_keywords = {
            'model': 2, 'algorithm': 3, 'api': 3, 'code': 2, 'technical': 3,
            'implementation': 3, 'architecture': 3, 'framework': 2, 'system': 2,
            'integration': 2, 'deployment': 2, 'configuration': 2, 'setup': 2
        }
        
        # Reality Check keywords (weighted)
        reality_keywords = {
            'reality': 3, 'truth': 3, 'assumption': 3, 'myth': 3, 'hype': 3,
            'challenge': 2, 'contrast': 2, 'different': 1, 'actually': 2,
            'however': 2, 'but': 1, 'misconception': 3, 'illusion': 3
        }
        
        # Success Stories keywords (weighted)
        success_keywords = {
            'success': 3, 'achieve': 2, 'result': 2, 'outcome': 2, 'impact': 3,
            'measurable': 3, 'roi': 3, 'testimonial': 3, 'case study': 3,
            'victory': 2, 'breakthrough': 3, 'transformation': 2
        }
        
        # Capacity Building keywords (weighted)
        capacity_keywords = {
            'training': 3, 'education': 2, 'learn': 2, 'skill': 2, 'capacity': 3,
            'empower': 3, 'guide': 2, 'how-to': 3, 'framework': 2, 'teach': 2,
            'mentor': 2, 'develop': 2, 'build': 2
        }
        
        # Calculate weighted scores
        for word, weight in failure_keywords.items():
            theme_scores['failure_prevention'] += content_lower.count(word) * weight
            
        for word, weight in technical_keywords.items():
            theme_scores['technical_deep_dive'] += content_lower.count(word) * weight
            
        for word, weight in reality_keywords.items():
            theme_scores['reality_check'] += content_lower.count(word) * weight
            
        for word, weight in success_keywords.items():
            theme_scores['success_stories'] += content_lower.count(word) * weight
            
        for word, weight in capacity_keywords.items():
            theme_scores['capacity_building'] += content_lower.count(word) * weight
        
        # Determine primary theme
        primary_theme = max(theme_scores, key=theme_scores.get)
        
        # Map theme to posting day
        theme_to_day = {
            'failure_prevention': 'monday',
            'technical_deep_dive': 'tuesday',
            'reality_check': 'wednesday',
            'success_stories': 'thursday',
            'capacity_building': 'friday'
        }
        
        optimal_day = theme_to_day.get(primary_theme, 'tuesday')
        
        # Calculate confidence (normalize by content length)
        total_score = sum(theme_scores.values())
        confidence = theme_scores[primary_theme] / max(total_score, 1) if total_score > 0 else 0
        
        return {
            'primary_theme': primary_theme,
            'theme_scores': theme_scores,
            'optimal_day': optimal_day,
            'confidence': confidence
        }
    
    def generate_linkedin_snippet(self, content: str, title: str, theme: str) -> str:
        """Generate engaging LinkedIn snippet in user's voice"""
        
        # Extract key elements from content
        lines = content.split('\n')
        
        # Find the hook - usually in first few paragraphs
        hook = ""
        substantial_paragraphs = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 50:
                # Clean up markdown
                clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Remove bold
                clean_line = re.sub(r'\*(.*?)\*', r'\1', clean_line)  # Remove italic
                clean_line = re.sub(r'`(.*?)`', r'\1', clean_line)  # Remove code
                substantial_paragraphs.append(clean_line)
                
        if substantial_paragraphs:
            hook = substantial_paragraphs[0]
        
        # Create snippet based on theme and voice guidelines
        snippet_templates = {
            'failure_prevention': self._create_failure_prevention_snippet,
            'technical_deep_dive': self._create_technical_snippet,
            'reality_check': self._create_reality_check_snippet,
            'success_stories': self._create_success_story_snippet,
            'capacity_building': self._create_capacity_building_snippet
        }
        
        snippet_func = snippet_templates.get(theme, self._create_generic_snippet)
        return snippet_func(hook, title, substantial_paragraphs)
    
    def _create_failure_prevention_snippet(self, hook: str, title: str, paragraphs: List[str]) -> str:
        """Create failure prevention snippet with provocative hook"""
        # Extract failure cost or consequence
        cost_pattern = r'\$[\d,]+|\d+%|[\d,]+ (hours|days|months|years)'
        costs = re.findall(cost_pattern, hook + ' '.join(paragraphs[:2]))
        
        if costs:
            cost_mention = f"Cost: {costs[0]}"
        else:
            cost_mention = "The price of getting this wrong is steep."
        
        snippet = f"🚨 {hook[:120]}...\n\n{cost_mention}\n\nHere's what I learned from watching projects crash and burn (and how you can sidestep these traps):\n\n👉 Read the full breakdown: [Link in comments]\n\nWhat's the most expensive mistake you've seen in AI projects? Let me know in the comments.\n\n#AI #ProjectManagement #LessonsLearned #LMIC"
        
        return snippet
    
    def _create_technical_snippet(self, hook: str, title: str, paragraphs: List[str]) -> str:
        """Create technical deep-dive snippet with accessible hook"""
        # Find technical concepts to highlight
        tech_terms = ['AI', 'API', 'model', 'algorithm', 'framework', 'system', 'integration']
        mentioned_terms = [term for term in tech_terms if term.lower() in hook.lower()]
        
        snippet = f"⚡ {hook[:150]}...\n\nThe technical reality behind the hype:\n• Real-world implementation challenges\n• Cost-effective solutions for resource-constrained environments\n• What actually works (vs. what sounds impressive)\n\nPerfect for technical leaders who need practical guidance, not just theory.\n\n👉 Full technical breakdown: [Link in comments]\n\nWhat's your experience with {mentioned_terms[0] if mentioned_terms else 'AI'} implementation? Share your insights below.\n\n#TechnicalLeadership #AI #Implementation #LMIC #HealthTech"
        
        return snippet
    
    def _create_reality_check_snippet(self, hook: str, title: str, paragraphs: List[str]) -> str:
        """Create reality check snippet with contrasting perspective"""
        
        snippet = f"""🤔 Unpopular opinion: {hook[:140]}...

While Silicon Valley celebrates the next shiny thing, here's what's actually happening on the ground in LMICs:

The gap between hype and reality is wider than you think.

I break down the real story (with examples from Uganda and beyond):

👉 Full reality check: [Link in comments]

Am I being too harsh, or do you see this disconnect too? What's your take?

#RealityCheck #AI #LMIC #TechRealism #Uganda"""
        
        return snippet
    
    def _create_success_story_snippet(self, hook: str, title: str, paragraphs: List[str]) -> str:
        """Create success story snippet with measurable outcomes"""
        # Look for metrics in the content
        metrics_pattern = r'(\d+%|\d+x|\$[\d,]+|[\d,]+ (patients|users|hours|days))'
        metrics = re.findall(metrics_pattern, ' '.join(paragraphs[:3]))
        
        if metrics:
            metric_highlight = f"Result: {metrics[0][0] if isinstance(metrics[0], tuple) else metrics[0]}"
        else:
            metric_highlight = "Measurable impact achieved."
        
        snippet = f"""✅ Success story: {hook[:130]}...

{metric_highlight}

This isn't just another feel-good case study. It's a blueprint for what works when you:
• Focus on real problems, not flashy solutions
• Design for resource constraints
• Measure what matters

👉 Full case study with implementation details: [Link in comments]

What success stories from your work would you like to share? I'd love to feature more real-world wins.

#SuccessStory #Impact #AI #Healthcare #LMIC #Results"""
        
        return snippet
    
    def _create_capacity_building_snippet(self, hook: str, title: str, paragraphs: List[str]) -> str:
        """Create capacity building snippet with actionable value"""
        
        snippet = f"""🎯 {hook[:140]}...

Here's the step-by-step framework I use to build sustainable AI capacity in resource-constrained environments:

✓ Practical tools you can implement immediately
✓ Real examples from Uganda and other LMICs
✓ Common pitfalls and how to avoid them

Perfect for leaders who want to empower their teams, not just deploy technology.

👉 Complete framework: [Link in comments]

What's your biggest challenge in building AI capacity? Let's solve it together in the comments.

#CapacityBuilding #Leadership #AI #Training #Empowerment #LMIC"""
        
        return snippet
    
    def _create_generic_snippet(self, hook: str, title: str, paragraphs: List[str]) -> str:
        """Create generic snippet maintaining voice"""
        
        snippet = f"""{hook[:150]}...

This hits different when you're working in resource-constrained environments.

I break down:
• What actually works (vs. what sounds good in theory)
• Practical implementation strategies
• Real-world examples from Uganda and beyond

👉 Full analysis: [Link in comments]

What's been your experience with this? Share your thoughts below.

#AI #LMIC #PracticalSolutions #RealWorld"""
        
        return snippet
    
    def move_to_posted(self, filename: str) -> bool:
        """Move article from Drafts to Posted folder"""
        source = self.drafts_folder / filename
        destination = self.posted_folder / filename
        
        try:
            if source.exists():
                shutil.move(str(source), str(destination))
                print(f"✅ Moved {filename} to Posted folder")
                return True
            else:
                print(f"❌ File not found: {filename}")
                return False
        except Exception as e:
            print(f"❌ Error moving {filename}: {e}")
            return False
    
    def interactive_content_review(self, filename: str, analysis: Dict) -> Dict:
        """Interactive review of content analysis with human oversight"""
        print(f"\n{'='*60}")
        print(f"REVIEWING: {filename}")
        print(f"{'='*60}")
        
        # Show analysis
        theme = analysis['theme_analysis']['primary_theme'].replace('_', ' ').title()
        day = analysis['theme_analysis']['optimal_day'].title()
        confidence = analysis['theme_analysis']['confidence']
        
        print(f"📊 AI Analysis:")
        print(f"   Theme: {theme} (confidence: {confidence:.2f})")
        print(f"   Optimal Day: {day}")
        print(f"   Word Count: {analysis['word_count']}")
        
        # Show snippet
        print(f"\n📝 Generated LinkedIn Snippet:")
        print("-" * 40)
        print(analysis['linkedin_snippet'])
        print("-" * 40)
        
        # Show enhancement notes
        print(f"\n💡 Enhancement Suggestions:")
        for i, note in enumerate(analysis['enhancement_notes'][:5], 1):
            print(f"   {i}. {note}")
        
        # Interactive decision
        print(f"\n🤔 Does this analysis look correct?")
        print(f"1. ✅ Yes, looks good")
        print(f"2. 📝 Edit the snippet")
        print(f"3. 🔄 Change the theme/day")
        print(f"4. ⏭️  Skip for now")
        
        choice = input("\nYour choice (1-4): ").strip()
        
        if choice == "2":
            print("\n📝 Current snippet:")
            print(analysis['linkedin_snippet'])
            new_snippet = input("\nEnter your improved snippet (or press Enter to keep current): ").strip()
            if new_snippet:
                analysis['linkedin_snippet'] = new_snippet
                analysis['snippet_edited'] = True
        
        elif choice == "3":
            print("\nAvailable themes:")
            themes = ['failure_prevention', 'technical_deep_dive', 'reality_check', 'success_stories', 'capacity_building']
            for i, t in enumerate(themes, 1):
                print(f"{i}. {t.replace('_', ' ').title()}")
            
            theme_choice = input("Choose theme (1-5) or press Enter to keep current: ").strip()
            if theme_choice.isdigit() and 1 <= int(theme_choice) <= 5:
                new_theme = themes[int(theme_choice) - 1]
                analysis['theme_analysis']['primary_theme'] = new_theme
                
                # Update optimal day
                theme_to_day = {
                    'failure_prevention': 'monday',
                    'technical_deep_dive': 'tuesday',
                    'reality_check': 'wednesday',
                    'success_stories': 'thursday',
                    'capacity_building': 'friday'
                }
                analysis['theme_analysis']['optimal_day'] = theme_to_day[new_theme]
                analysis['theme_manually_adjusted'] = True
        
        analysis['human_reviewed'] = True
        analysis['review_timestamp'] = datetime.now().isoformat()
        
        return analysis
    
    def scan_and_analyze_with_interaction(self) -> Dict:
        """Scan drafts with interactive review for each piece"""
        database = self.load_content_database()
        results = {'new_files': [], 'updated_files': [], 'analysis': {}}
        
        if not self.drafts_folder.exists():
            print(f"❌ Drafts folder not found: {self.drafts_folder}")
            return results
        
        print(f"🔍 Scanning {self.drafts_folder} for content...")
        
        for file_path in self.drafts_folder.glob("*.md"):
            file_hash = self.get_file_hash(file_path)
            filename = file_path.name
            
            # Check if file is new or updated
            if filename not in database['files']:
                results['new_files'].append(filename)
                is_new = True
            elif database['files'][filename]['hash'] != file_hash:
                results['updated_files'].append(filename)
                is_new = False
            else:
                # File unchanged, skip analysis unless forced
                results['analysis'][filename] = database['files'][filename]['analysis']
                continue
            
            # Read and analyze content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title
                title = ""
                for line in content.split('\n'):
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                
                # Analyze theme
                theme_analysis = self.analyze_content_theme(content, filename)
                
                # Generate snippet
                linkedin_snippet = self.generate_linkedin_snippet(
                    content, title, theme_analysis['primary_theme']
                )
                
                # Generate enhancement notes
                enhancement_notes = self.generate_enhancement_notes(content, theme_analysis)
                
                analysis = {
                    'theme_analysis': theme_analysis,
                    'linkedin_snippet': linkedin_snippet,
                    'enhancement_notes': enhancement_notes,
                    'word_count': len(content.split()),
                    'title': title,
                    'last_analyzed': datetime.now().isoformat(),
                    'status': 'new' if is_new else 'updated'
                }
                
                # Interactive review
                analysis = self.interactive_content_review(filename, analysis)
                
                # Update database
                database['files'][filename] = {
                    'hash': file_hash,
                    'analysis': analysis,
                    'file_path': str(file_path)
                }
                
                results['analysis'][filename] = analysis
                
            except Exception as e:
                print(f"❌ Error analyzing {filename}: {e}")
        
        self.save_content_database(database)
        return results
    
    def get_file_hash(self, filepath: Path) -> str:
        """Generate hash of file content for change detection"""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def load_content_database(self) -> Dict:
        """Load existing content database"""
        if self.database_file.exists():
            with open(self.database_file, 'r') as f:
                return json.load(f)
        return {'files': {}, 'last_scan': None}
    
    def save_content_database(self, database: Dict):
        """Save content database"""
        database['last_scan'] = datetime.now().isoformat()
        with open(self.database_file, 'w') as f:
            json.dump(database, f, indent=2)
    
    def generate_enhancement_notes(self, content: str, theme_analysis: Dict) -> List[str]:
        """Generate enhancement recommendations based on content analysis and voice guidelines"""
        notes = []
        
        # Voice-specific enhancements
        if 'analogy' not in content.lower() and 'like' not in content.lower():
            notes.append("Add analogies to explain complex concepts (per your voice guidelines)")
        
        if content.count('?') < 2:
            notes.append("Add more questions to engage readers and build community")
        
        if 'uganda' not in content.lower() and 'lmic' not in content.lower():
            notes.append("Add Uganda/LMIC-specific examples to maintain authenticity")
        
        # Check for voice elements
        if not any(word in content.lower() for word in ['however', 'but', 'actually', 'reality']):
            notes.append("Add contrasting perspectives to challenge assumptions")
        
        if '2024' not in content and '2025' not in content:
            notes.append("Update with current 2024/2025 statistics and examples")
        
        if '$' not in content and 'cost' not in content.lower():
            notes.append("Add cost analysis and ROI data for practical value")
        
        # Theme-specific enhancements
        theme = theme_analysis['primary_theme']
        
        if theme == 'failure_prevention':
            notes.extend([
                "Include specific failure case studies with measurable costs",
                "Add prevention frameworks and actionable checklists",
                "Research recent AI project failure statistics for credibility"
            ])
        
        elif theme == 'technical_deep_dive':
            notes.extend([
                "Update technical specifications and current pricing",
                "Add step-by-step implementation guides",
                "Include resource constraints and LMIC considerations"
            ])
        
        elif theme == 'reality_check':
            notes.extend([
                "Add contrasting examples (Silicon Valley vs LMIC reality)",
                "Include poll questions for LinkedIn engagement",
                "Add myth-busting statistics and data"
            ])
        
        elif theme == 'success_stories':
            notes.extend([
                "Add specific measurable outcomes and KPIs",
                "Include client testimonials or case study details",
                "Create clear before/after comparisons"
            ])
        
        elif theme == 'capacity_building':
            notes.extend([
                "Add practical exercises and implementation checklists",
                "Include resource links and further reading",
                "Create educational framework or step-by-step guide"
            ])
        
        return notes[:8]  # Limit to most important suggestions

def main():
    parser = argparse.ArgumentParser(description='Enhanced LinkedIn content analysis with voice integration')
    parser.add_argument('--interactive-scan', action='store_true', help='Scan drafts with interactive review')
    parser.add_argument('--move-to-posted', type=str, help='Move specific file to Posted folder')
    parser.add_argument('--generate-snippet', type=str, help='Generate snippet for specific file')
    
    args = parser.parse_args()
    
    analyzer = EnhancedContentAnalyzer()
    
    if args.interactive_scan:
        print("🎯 Starting interactive content analysis...")
        results = analyzer.scan_and_analyze_with_interaction()
        
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"New files: {len(results['new_files'])}")
        print(f"Updated files: {len(results['updated_files'])}")
        print(f"Total analyzed: {len(results['analysis'])}")
        
    elif args.move_to_posted:
        analyzer.move_to_posted(args.move_to_posted)
        
    elif args.generate_snippet:
        # Generate snippet for specific file
        file_path = Path("Drafts") / args.generate_snippet
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = ""
            for line in content.split('\n'):
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            theme_analysis = analyzer.analyze_content_theme(content, args.generate_snippet)
            snippet = analyzer.generate_linkedin_snippet(content, title, theme_analysis['primary_theme'])
            
            print(f"\n📝 LinkedIn Snippet for {args.generate_snippet}:")
            print("-" * 50)
            print(snippet)
            print("-" * 50)
        else:
            print(f"❌ File not found: {args.generate_snippet}")
    
    else:
        print("Use --help to see available options")
        print("Recommended: --interactive-scan for full analysis with human oversight")

if __name__ == "__main__":
    main()
