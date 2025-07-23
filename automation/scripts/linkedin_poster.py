#!/usr/bin/env python3
"""
LinkedIn API Integration for Automated Posting
Handles authentication, scheduling, and posting to LinkedIn
"""

import os
import json
import requests
import yaml
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import time
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse

class LinkedInPoster:
    def __init__(self, config_path: str = "automation/config/linkedin_api.yaml"):
        self.config_path = config_path
        self.load_config()
        self.base_url = "https://api.linkedin.com/v2"
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.access_token = None
        self.user_id = None
        
    def load_config(self):
        """Load LinkedIn API configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  Configuration file not found: {self.config_path}")
            print("Please create the configuration file with your LinkedIn API credentials.")
            self.config = {
                'client_id': 'your_linkedin_app_id',
                'client_secret': 'your_linkedin_app_secret',
                'redirect_uri': 'http://localhost:8080/callback',
                'scopes': ['w_member_social', 'r_liteprofile']
            }
    
    def get_authorization_url(self) -> str:
        """Generate LinkedIn authorization URL"""
        params = {
            'response_type': 'code',
            'client_id': self.config['client_id'],
            'redirect_uri': self.config['redirect_uri'],
            'scope': ' '.join(self.config['scopes']),
            'state': 'linkedin_content_automation'
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict:
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.config['redirect_uri'],
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret']
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Save token for future use
            self.save_token(token_data)
            return token_data
        else:
            raise Exception(f"Failed to get access token: {response.text}")
    
    def save_token(self, token_data: Dict):
        """Save access token to file"""
        token_file = Path("automation/data/linkedin_token.json")
        token_file.parent.mkdir(parents=True, exist_ok=True)
        
        token_data['expires_at'] = datetime.now().timestamp() + token_data['expires_in']
        
        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
    
    def load_token(self) -> Optional[str]:
        """Load saved access token"""
        token_file = Path("automation/data/linkedin_token.json")
        
        if not token_file.exists():
            return None
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        # Check if token is still valid
        if datetime.now().timestamp() < token_data.get('expires_at', 0):
            self.access_token = token_data['access_token']
            return self.access_token
        
        return None
    
    def authenticate(self):
        """Handle LinkedIn authentication flow"""
        # Try to load existing token
        if self.load_token():
            print("✅ Using saved access token")
            return
        
        print("🔐 LinkedIn authentication required")
        print("1. Opening LinkedIn authorization page...")
        
        auth_url = self.get_authorization_url()
        webbrowser.open(auth_url)
        
        print("2. After authorizing, copy the 'code' parameter from the redirect URL")
        authorization_code = input("Enter authorization code: ").strip()
        
        print("3. Exchanging code for access token...")
        self.exchange_code_for_token(authorization_code)
        print("✅ Authentication successful!")
    
    def get_user_profile(self) -> Dict:
        """Get user profile information"""
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{self.base_url}/me", headers=headers)
        
        if response.status_code == 200:
            profile = response.json()
            self.user_id = profile['id']
            return profile
        else:
            raise Exception(f"Failed to get profile: {response.text}")
    
    def create_text_post(self, text: str, visibility: str = "PUBLIC") -> Dict:
        """Create a text post on LinkedIn"""
        if not self.access_token or not self.user_id:
            raise Exception("Not authenticated or user ID not available")
        
        post_data = {
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        response = requests.post(f"{self.base_url}/ugcPosts", 
                               json=post_data, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create post: {response.text}")
    
    def create_article_post(self, title: str, content: str, summary: str = "") -> Dict:
        """Create an article post on LinkedIn"""
        # LinkedIn articles require different API endpoints and permissions
        # This is a simplified version - full implementation would need article API
        
        post_text = f"{title}\n\n{summary}\n\n[Read full article...]"
        return self.create_text_post(post_text)
    
    def schedule_post(self, content: str, scheduled_time: datetime, dry_run: bool = True) -> Dict:
        """Schedule a post for future publishing"""
        if dry_run:
            print(f"🔍 DRY RUN - Would schedule post for {scheduled_time}")
            print(f"Content preview: {content[:100]}...")
            return {"status": "dry_run", "scheduled_time": scheduled_time.isoformat()}
        
        # For actual scheduling, you'd typically store the post data
        # and use a scheduler (like cron) to post at the right time
        print(f"📅 Scheduling post for {scheduled_time}")
        
        # Save to scheduling database
        schedule_data = {
            "content": content,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        self.save_scheduled_post(schedule_data)
        return schedule_data
    
    def save_scheduled_post(self, post_data: Dict):
        """Save scheduled post to database"""
        schedule_file = Path("automation/data/scheduled_posts.json")
        schedule_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing scheduled posts
        if schedule_file.exists():
            with open(schedule_file, 'r') as f:
                scheduled_posts = json.load(f)
        else:
            scheduled_posts = []
        
        scheduled_posts.append(post_data)
        
        with open(schedule_file, 'w') as f:
            json.dump(scheduled_posts, f, indent=2)
    
    def post_now(self, content: str, dry_run: bool = True) -> Dict:
        """Post content immediately"""
        if dry_run:
            print(f"🔍 DRY RUN - Would post now:")
            print(f"Content: {content}")
            return {"status": "dry_run", "content": content}
        
        try:
            result = self.create_text_post(content)
            print("✅ Post published successfully!")
            return result
        except Exception as e:
            print(f"❌ Failed to publish post: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_optimal_posting_time(self, day: str) -> datetime:
        """Get optimal posting time for a given day"""
        # Load content strategy
        try:
            with open("automation/config/content_strategy.yaml", 'r') as f:
                strategy = yaml.safe_load(f)
        except FileNotFoundError:
            # Default times
            strategy = {
                'posting_schedule': {
                    'monday': {'optimal_times': ['10:00', '12:00']},
                    'tuesday': {'optimal_times': ['10:00', '14:00']},
                    'wednesday': {'optimal_times': ['10:00', '13:00']},
                    'thursday': {'optimal_times': ['12:00', '15:00']},
                    'friday': {'optimal_times': ['14:00']}
                }
            }
        
        day_config = strategy['posting_schedule'].get(day.lower(), {'optimal_times': ['12:00']})
        optimal_time = day_config['optimal_times'][0]  # Use first optimal time
        
        # Calculate next occurrence of this day and time
        today = datetime.now()
        days_ahead = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'].index(day.lower())
        days_until = (days_ahead - today.weekday()) % 7
        
        if days_until == 0 and today.hour >= int(optimal_time.split(':')[0]):
            days_until = 7  # Schedule for next week if time has passed today
        
        target_date = today + timedelta(days=days_until)
        hour, minute = map(int, optimal_time.split(':'))
        
        return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def create_post_from_draft(self, draft_file: Path, snippet_length: int = 300) -> str:
        """Create LinkedIn post from draft file"""
        with open(draft_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title (first line starting with #)
        lines = content.split('\n')
        title = ""
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # Create engaging snippet
        # Remove markdown formatting for LinkedIn
        clean_content = content.replace('#', '').replace('*', '').replace('`', '')
        
        # Find first substantial paragraph
        paragraphs = [p.strip() for p in clean_content.split('\n\n') if len(p.strip()) > 50]
        
        if paragraphs:
            snippet = paragraphs[0][:snippet_length]
            if len(paragraphs[0]) > snippet_length:
                snippet += "..."
        else:
            snippet = clean_content[:snippet_length] + "..."
        
        # Add call to action
        linkedin_post = f"{snippet}\n\n👉 Read the full article: [Link to be added]\n\n#AI #healthcare #LMIC #digitaltransformation"
        
        return linkedin_post

def main():
    parser = argparse.ArgumentParser(description='LinkedIn posting automation')
    parser.add_argument('--authenticate', action='store_true', help='Authenticate with LinkedIn')
    parser.add_argument('--post-now', type=str, help='Post content immediately')
    parser.add_argument('--schedule-post', type=str, help='Schedule post from draft file')
    parser.add_argument('--day', type=str, help='Day of week for scheduling')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual posting)')
    parser.add_argument('--config', default='automation/config/linkedin_api.yaml', help='Configuration file path')
    
    args = parser.parse_args()
    
    poster = LinkedInPoster(args.config)
    
    if args.authenticate:
        poster.authenticate()
        profile = poster.get_user_profile()
        print(f"✅ Authenticated as: {profile.get('firstName', '')} {profile.get('lastName', '')}")
        return
    
    if args.post_now:
        draft_file = Path(args.post_now)
        if draft_file.exists():
            content = poster.create_post_from_draft(draft_file)
            poster.post_now(content, dry_run=args.dry_run)
        else:
            poster.post_now(args.post_now, dry_run=args.dry_run)
        return
    
    if args.schedule_post:
        draft_file = Path(args.schedule_post)
        day = args.day or 'tuesday'  # Default to Tuesday
        
        if draft_file.exists():
            content = poster.create_post_from_draft(draft_file)
            scheduled_time = poster.get_optimal_posting_time(day)
            poster.schedule_post(content, scheduled_time, dry_run=args.dry_run)
        else:
            print(f"❌ Draft file not found: {draft_file}")
        return
    
    print("Use --help to see available options")

if __name__ == "__main__":
    main()
