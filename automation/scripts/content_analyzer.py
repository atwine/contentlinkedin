#!/usr/bin/env python3
"""
LinkedIn Content Analyzer
Automatically analyzes draft content and maps to optimal posting schedule
"""

import os
import json
import yaml
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

class ContentAnalyzer:
    def __init__(self, config_path: str = "automation/config/content_strategy.yaml"):
        self.config_path = config_path
        self.load_config()
        self.drafts_folder = Path("C:/Users/ic/OneDrive/Desktop/Other Things/Content - My Articles/Drafts")
        self.strategy_file = Path("C:/Users/ic/OneDrive/Desktop/Other Things/Content - My Articles/enhanced_linkedin_strategy_2024.md")
        self.database_file = Path("automation/data/content_database.json")
        self.ensure_data_directory()
        
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
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        self.database_file.parent.mkdir(parents=True, exist_ok=True)
        
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
    
    def analyze_content_theme(self, content: str, filename: str) -> Dict:
        """Analyze content to determine theme and optimal posting day"""
        content_lower = content.lower()
        
        # Theme analysis based on keywords and content
        theme_scores = {
            'failure_prevention': 0,
            'technical_deep_dive': 0,
            'reality_check': 0,
            'success_stories': 0,
            'capacity_building': 0
        }
        
        # Failure Prevention keywords
        failure_keywords = ['fail', 'mistake', 'error', 'problem', 'wrong', 'disaster', 'crisis', 'prevent', 'avoid', 'trap']
        theme_scores['failure_prevention'] = sum(1 for word in failure_keywords if word in content_lower)
        
        # Technical Deep-Dive keywords
        technical_keywords = ['model', 'algorithm', 'api', 'code', 'technical', 'implementation', 'architecture', 'framework', 'system']
        theme_scores['technical_deep_dive'] = sum(1 for word in technical_keywords if word in content_lower)
        
        # Reality Check keywords
        reality_keywords = ['reality', 'truth', 'assumption', 'myth', 'hype', 'challenge', 'contrast', 'different', 'actually']
        theme_scores['reality_check'] = sum(1 for word in reality_keywords if word in content_lower)
        
        # Success Stories keywords
        success_keywords = ['success', 'achieve', 'result', 'outcome', 'impact', 'measurable', 'roi', 'testimonial', 'case study']
        theme_scores['success_stories'] = sum(1 for word in success_keywords if word in content_lower)
        
        # Capacity Building keywords
        capacity_keywords = ['training', 'education', 'learn', 'skill', 'capacity', 'empower', 'guide', 'how-to', 'framework']
        theme_scores['capacity_building'] = sum(1 for word in capacity_keywords if word in content_lower)
        
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
        
        optimal_day = theme_to_day.get(primary_theme, 'tuesday')  # Default to Tuesday
        
        return {
            'primary_theme': primary_theme,
            'theme_scores': theme_scores,
            'optimal_day': optimal_day,
            'confidence': theme_scores[primary_theme] / max(sum(theme_scores.values()), 1)
        }
    
    def generate_enhancement_notes(self, content: str, theme_analysis: Dict) -> List[str]:
        """Generate enhancement recommendations based on content analysis"""
        notes = []
        
        # General enhancements
        if 'uganda' not in content.lower():
            notes.append("Add Uganda/LMIC-specific examples and context")
        
        if '2024' not in content and '2025' not in content:
            notes.append("Update with 2024/2025 statistics and current data")
        
        if '$' not in content and 'cost' not in content.lower():
            notes.append("Add cost analysis and ROI data")
        
        # Theme-specific enhancements
        theme = theme_analysis['primary_theme']
        
        if theme == 'failure_prevention':
            notes.extend([
                "Add specific failure case studies with dollar amounts",
                "Include prevention frameworks and checklists",
                "Research recent AI project failure statistics"
            ])
        
        elif theme == 'technical_deep_dive':
            notes.extend([
                "Update technical specifications and pricing",
                "Add step-by-step implementation guides",
                "Include compatibility and system requirements"
            ])
        
        elif theme == 'reality_check':
            notes.extend([
                "Find contrasting examples (Silicon Valley vs LMIC)",
                "Add poll questions for engagement",
                "Include myth-busting statistics"
            ])
        
        elif theme == 'success_stories':
            notes.extend([
                "Add measurable outcomes and KPIs",
                "Include client testimonials if possible",
                "Create before/after comparisons"
            ])
        
        elif theme == 'capacity_building':
            notes.extend([
                "Add practical exercises and checklists",
                "Include resource links and references",
                "Create educational infographic concepts"
            ])
        
        return notes
    
    def scan_drafts_folder(self) -> Dict:
        """Scan drafts folder and analyze all content"""
        database = self.load_content_database()
        results = {'new_files': [], 'updated_files': [], 'analysis': {}}
        
        if not self.drafts_folder.exists():
            print(f"Drafts folder not found: {self.drafts_folder}")
            return results
        
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
                # File unchanged, skip analysis
                results['analysis'][filename] = database['files'][filename]['analysis']
                continue
            
            # Read and analyze content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                theme_analysis = self.analyze_content_theme(content, filename)
                enhancement_notes = self.generate_enhancement_notes(content, theme_analysis)
                
                analysis = {
                    'theme_analysis': theme_analysis,
                    'enhancement_notes': enhancement_notes,
                    'word_count': len(content.split()),
                    'last_analyzed': datetime.now().isoformat(),
                    'status': 'new' if is_new else 'updated'
                }
                
                # Update database
                database['files'][filename] = {
                    'hash': file_hash,
                    'analysis': analysis,
                    'file_path': str(file_path)
                }
                
                results['analysis'][filename] = analysis
                
            except Exception as e:
                print(f"Error analyzing {filename}: {e}")
        
        self.save_content_database(database)
        return results
    
    def create_timetable(self, analysis_results: Dict) -> str:
        """Create posting timetable based on analysis results"""
        timetable_content = []
        timetable_content.append("# LinkedIn Content Posting Timetable")
        timetable_content.append("## Auto-Generated from Content Analysis")
        timetable_content.append("")
        timetable_content.append("| **Day** | **Theme** | **Optimal Time** | **Article** | **Confidence** | **Enhancement Notes** |")
        timetable_content.append("|---------|-----------|------------------|-------------|----------------|----------------------|")
        
        # Group files by optimal day
        day_groups = {}
        for filename, analysis in analysis_results['analysis'].items():
            optimal_day = analysis['theme_analysis']['optimal_day']
            if optimal_day not in day_groups:
                day_groups[optimal_day] = []
            day_groups[optimal_day].append((filename, analysis))
        
        # Sort by day of week
        day_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        
        for day in day_order:
            if day not in day_groups:
                continue
                
            day_config = self.config['posting_schedule'][day]
            theme = day_config['theme']
            times = ', '.join(day_config['optimal_times'])
            
            for filename, analysis in day_groups[day]:
                confidence = f"{analysis['theme_analysis']['confidence']:.2f}"
                notes = "; ".join(analysis['enhancement_notes'][:3])  # First 3 notes
                
                timetable_content.append(f"| **{day.title()}** | {theme} | {times} | `{filename}` | {confidence} | {notes} |")
        
        timetable_content.append("")
        timetable_content.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(timetable_content)
    
    def generate_report(self, analysis_results: Dict):
        """Generate analysis report"""
        print("\n" + "="*60)
        print("LINKEDIN CONTENT ANALYSIS REPORT")
        print("="*60)
        
        print(f"\nScan Results:")
        print(f"  New files: {len(analysis_results['new_files'])}")
        print(f"  Updated files: {len(analysis_results['updated_files'])}")
        print(f"  Total analyzed: {len(analysis_results['analysis'])}")
        
        if analysis_results['new_files']:
            print(f"\n📄 New Files:")
            for filename in analysis_results['new_files']:
                print(f"  - {filename}")
        
        if analysis_results['updated_files']:
            print(f"\n🔄 Updated Files:")
            for filename in analysis_results['updated_files']:
                print(f"  - {filename}")
        
        print(f"\n📊 Content Analysis:")
        for filename, analysis in analysis_results['analysis'].items():
            theme = analysis['theme_analysis']['primary_theme'].replace('_', ' ').title()
            day = analysis['theme_analysis']['optimal_day'].title()
            confidence = analysis['theme_analysis']['confidence']
            
            print(f"\n  📝 {filename}")
            print(f"     Theme: {theme} (confidence: {confidence:.2f})")
            print(f"     Optimal Day: {day}")
            print(f"     Word Count: {analysis['word_count']}")
            print(f"     Enhancement Notes: {len(analysis['enhancement_notes'])}")
            
            if analysis['enhancement_notes']:
                print(f"     Top Suggestions:")
                for note in analysis['enhancement_notes'][:3]:
                    print(f"       • {note}")

def main():
    parser = argparse.ArgumentParser(description='Analyze LinkedIn content drafts')
    parser.add_argument('--scan-drafts', action='store_true', help='Scan drafts folder for new/updated content')
    parser.add_argument('--create-timetable', action='store_true', help='Create posting timetable')
    parser.add_argument('--config', default='automation/config/content_strategy.yaml', help='Configuration file path')
    
    args = parser.parse_args()
    
    analyzer = ContentAnalyzer(args.config)
    
    if args.scan_drafts:
        print("🔍 Scanning drafts folder...")
        results = analyzer.scan_drafts_folder()
        analyzer.generate_report(results)
        
        if args.create_timetable:
            print("\n📅 Creating posting timetable...")
            timetable = analyzer.create_timetable(results)
            
            # Save timetable
            timetable_path = Path("auto_generated_timetable.md")
            with open(timetable_path, 'w', encoding='utf-8') as f:
                f.write(timetable)
            
            print(f"✅ Timetable saved to: {timetable_path}")
    
    else:
        print("Use --scan-drafts to analyze content")

if __name__ == "__main__":
    main()
