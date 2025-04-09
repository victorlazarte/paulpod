import requests
from bs4 import BeautifulSoup
import json
import os
import re

def fetch_essay_content(url):
    try:
        print(f"\nFetching {url}...")
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main content table
        content_table = soup.find('table', width="435")
        if not content_table:
            print(f"Could not find content table in {url}")
            return None
        
        # Get all text from the table
        text = content_table.get_text(separator='\n').strip()
        
        # Get the first 4 lines
        lines = [line for line in text.split('\n') if line.strip()]  # Split by newline and remove empty lines
        preview = '\n'.join(lines[:4])  # Get first 4 non-empty lines
        
        return preview
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def update_index_html(essays_with_previews):
    try:
        with open('index.html', 'r') as f:
            content = f.read()
        
        # Update each essay preview
        for essay in essays_with_previews:
            if 'preview' in essay:
                # Create pattern to match the specific essay's preview div
                title_pattern = re.escape(essay['title'])
                pattern = f'(<h2 class="essay-title">{title_pattern}</h2>.*?<div class="essay-preview">)[^<]*(</div>)'
                replacement = f'\\1\n                {essay["preview"]}\n            \\2'
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open('index.html', 'w') as f:
            f.write(content)
            
        print("\nSuccessfully updated index.html with all essay previews")
    except Exception as e:
        print(f"Error updating index.html: {e}")

# Test with just the first essay
essay = {
    "title": "How to Start Google",
    "url": "https://paulgraham.com/google.html",
    "date": "March 2024"
}

preview = fetch_essay_content(essay['url'])
if preview:
    print("\nFirst few paragraphs of the essay:")
    print("-" * 80)
    print(preview)
    print("-" * 80)
    update_index_html([essay])
else:
    print("Failed to fetch essay content")

# List of Paul Graham's essays
essays = [
    {"title": "How to Start Google", "url": "https://paulgraham.com/google.html", "date": "March 2024"},
    {"title": "The Reddits", "url": "https://paulgraham.com/reddits.html", "date": "March 2024"},
    {"title": "Great Work", "url": "https://paulgraham.com/greatwork.html", "date": "February 2024"},
    {"title": "Wealth", "url": "https://paulgraham.com/wealth.html", "date": "February 2024"},
    {"title": "Superlinear Returns", "url": "https://paulgraham.com/superlinear.html", "date": "January 2024"},
    {"title": "Woke", "url": "https://paulgraham.com/woke.html", "date": "January 2024"},
    {"title": "Best", "url": "https://paulgraham.com/best.html", "date": "December 2023"},
    {"title": "HWH", "url": "https://paulgraham.com/hwh.html", "date": "December 2023"},
    {"title": "Words", "url": "https://paulgraham.com/words.html", "date": "November 2023"},
    {"title": "Writes", "url": "https://paulgraham.com/writes.html", "date": "November 2023"},
    {"title": "When", "url": "https://paulgraham.com/when.html", "date": "October 2023"},
    {"title": "Weird", "url": "https://paulgraham.com/weird.html", "date": "October 2023"},
    {"title": "Want", "url": "https://paulgraham.com/want.html", "date": "September 2023"},
    {"title": "Users", "url": "https://paulgraham.com/users.html", "date": "September 2023"},
    {"title": "Smart", "url": "https://paulgraham.com/smart.html", "date": "August 2023"},
    {"title": "Read", "url": "https://paulgraham.com/read.html", "date": "August 2023"},
    {"title": "Persistence", "url": "https://paulgraham.com/persistence.html", "date": "July 2023"},
    {"title": "Own", "url": "https://paulgraham.com/own.html", "date": "July 2023"},
    {"title": "Heresy", "url": "https://paulgraham.com/heresy.html", "date": "June 2023"},
    {"title": "Good Taste", "url": "https://paulgraham.com/goodtaste.html", "date": "June 2023"},
    {"title": "Get Ideas", "url": "https://paulgraham.com/getideas.html", "date": "May 2023"},
    {"title": "Founder Mode", "url": "https://paulgraham.com/foundermode.html", "date": "May 2023"},
    {"title": "Do", "url": "https://paulgraham.com/do.html", "date": "April 2023"},
    {"title": "Alien", "url": "https://paulgraham.com/alien.html", "date": "April 2023"}
]

# Fetch content for each essay
for essay in essays:
    preview = fetch_essay_content(essay['url'])
    if preview:
        essay['preview'] = preview

# Update all essay previews in index.html
update_index_html(essays)

# Save the essays data to a JSON file
with open('essays.json', 'w') as f:
    json.dump(essays, f, indent=2)

print("Essay content fetched and saved to essays.json") 