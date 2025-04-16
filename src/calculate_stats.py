import os
from pydub import AudioSegment
import json
import requests
from bs4 import BeautifulSoup

def get_essay_content(url):
    """Fetch and clean essay content from the given URL."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different methods to find the content
        content = None
        
        # Method 1: Look for font tag with helvetica
        content = soup.find('font', face='helvetica')
        
        # Method 2: Look for the main content div
        if not content:
            content = soup.find('div', {'class': 'content'})
        
        # Method 3: Look for the main text
        if not content:
            content = soup.find('body')
        
        if content:
            # Remove script and style elements
            for script in content(["script", "style"]):
                script.decompose()
            
            # Get text and clean it
            text = content.get_text()
            # Remove extra whitespace
            text = ' '.join(text.split())
            return text
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_audio_length(file_path):
    """Get the length of an audio file in seconds."""
    try:
        audio = AudioSegment.from_mp3(file_path)
        return len(audio) / 1000  # Convert milliseconds to seconds
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def format_duration(seconds):
    """Format seconds into MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def main():
    output_dir = "output"
    essays = [
        {"title": "Do", "url": "https://paulgraham.com/do.html", "audio": "do.mp3"},
        {"title": "Woke", "url": "https://paulgraham.com/woke.html", "audio": "woke.mp3"},
        {"title": "When", "url": "https://paulgraham.com/when.html", "audio": "when.mp3"},
        {"title": "Writes", "url": "https://paulgraham.com/writes.html", "audio": "writes.mp3"},
        {"title": "Founder Mode", "url": "https://paulgraham.com/foundermode.html", "audio": "foundermode.mp3"},
        {"title": "Persistence", "url": "https://paulgraham.com/persistence.html", "audio": "persistence.mp3"},
        {"title": "How to Start Google", "url": "https://paulgraham.com/google.html", "audio": "google.mp3"},
        {"title": "The Reddits", "url": "https://paulgraham.com/reddits.html", "audio": "reddits.mp3"},
        {"title": "Best", "url": "https://paulgraham.com/best.html", "audio": "best.mp3"},
        {"title": "Great Work", "url": "http://www.paulgraham.com/greatwork.html", "audio": "greatwork.mp3"},
        {"title": "Wealth", "url": "http://www.paulgraham.com/wealth.html", "audio": "wealth.mp3"},
        {"title": "Superlinear Returns", "url": "http://www.paulgraham.com/superlinear.html", "audio": "superlinear.mp3"},
        {"title": "Get Ideas", "url": "http://www.paulgraham.com/getideas.html", "audio": "getideas.mp3"},
        {"title": "Want", "url": "http://www.paulgraham.com/want.html", "audio": "want.mp3"},
        {"title": "Read", "url": "http://www.paulgraham.com/read.html", "audio": "read.mp3"},
        {"title": "Users", "url": "http://www.paulgraham.com/users.html", "audio": "users.mp3"},
        {"title": "Alien", "url": "http://www.paulgraham.com/alien.html", "audio": "alien.mp3"},
        {"title": "Heresy", "url": "http://www.paulgraham.com/heresy.html", "audio": "heresy.mp3"},
        {"title": "Words", "url": "http://www.paulgraham.com/words.html", "audio": "words.mp3"},
        {"title": "Good Taste", "url": "http://www.paulgraham.com/goodtaste.html", "audio": "goodtaste.mp3"},
        {"title": "Smart", "url": "http://www.paulgraham.com/smart.html", "audio": "smart.mp3"},
        {"title": "Weird", "url": "http://www.paulgraham.com/weird.html", "audio": "weird.mp3"},
        {"title": "HWH", "url": "http://www.paulgraham.com/hwh.html", "audio": "hwh.mp3"},
        {"title": "Own", "url": "http://www.paulgraham.com/own.html", "audio": "own.mp3"}
    ]

    stats = []
    for essay in essays:
        print(f"Processing {essay['title']}...")
        
        # Get character count
        content = get_essay_content(essay['url'])
        char_count = len(content) if content else 0
        print(f"Character count: {char_count}")
        
        # Get audio length
        audio_path = os.path.join(output_dir, essay['audio'])
        audio_length = get_audio_length(audio_path)
        formatted_length = format_duration(audio_length) if audio_length else "00:00"
        print(f"Audio length: {formatted_length}")
        
        stats.append({
            "title": essay['title'],
            "characters": char_count,
            "audio_length": formatted_length
        })
    
    # Save stats to a JSON file
    with open("essay_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    
    print("\nStats saved to essay_stats.json")

if __name__ == "__main__":
    main() 