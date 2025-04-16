import os
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import concurrent.futures
import subprocess
import re
from typing import List, Dict

# Load environment variables
load_dotenv()

# Get all API keys from environment
API_KEYS = [
    os.getenv(f'ELEVENLABS_API_KEY_{i}') 
    for i in range(1, 11)
]

def fetch_essay_content(url: str) -> str:
    """Fetch the full content of an essay from paulgraham.com"""
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
        return text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def split_into_chunks(text: str, chunk_size: int = 4000) -> List[str]:
    """Split text into chunks of approximately equal size, trying to break at paragraph boundaries"""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        if current_size + len(paragraph) > chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = []
            current_size = 0
            
        current_chunk.append(paragraph)
        current_size += len(paragraph)
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def generate_audio_chunk(chunk_text, output_file, chunk_index):
    # Use a different API key for each chunk
    api_key = API_KEYS[chunk_index % len(API_KEYS)]
    
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": chunk_text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"Generated audio for chunk {chunk_index + 1}")
        return True
    except Exception as e:
        print(f"Error generating audio for chunk {chunk_index + 1}: {e}")
        return False

def merge_audio_files(input_files: List[str], output_file: str) -> bool:
    """Merge multiple audio files into one using ffmpeg"""
    try:
        # Create a temporary file with the list of files to concatenate
        with open('file_list.txt', 'w') as f:
            for file in input_files:
                f.write(f"file '{file}'\n")
        
        # Use ffmpeg to concatenate the files
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', 'file_list.txt',
            '-c', 'copy',
            output_file
        ]
        
        subprocess.run(cmd, check=True)
        print(f"Merged audio files into {output_file}")
        return True
    except Exception as e:
        print(f"Error merging audio files: {e}")
        return False
    finally:
        # Clean up the temporary file
        if os.path.exists('file_list.txt'):
            os.remove('file_list.txt')

def process_essay(essay_url, essay_title):
    # Create output and chunks directories if they don't exist
    os.makedirs('output', exist_ok=True)
    os.makedirs('chunks', exist_ok=True)
    
    # Fetch essay content
    content = fetch_essay_content(essay_url)
    if not content:
        return False
    
    # Split into chunks
    chunks = split_into_chunks(content)
    print(f"Split essay into {len(chunks)} chunks")
    
    # Generate audio for each chunk in parallel
    audio_files = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(API_KEYS)) as executor:
        futures = []
        for i, chunk in enumerate(chunks):
            chunk_file = f'chunks/{essay_title.lower()}_chunk_{i+1}.txt'
            audio_file = f'chunks/{essay_title.lower()}_audio_{i+1}.mp3'
            
            # Save chunk to file
            with open(chunk_file, 'w') as f:
                f.write(chunk)
            
            # Submit audio generation task
            future = executor.submit(generate_audio_chunk, chunk, audio_file, i)
            futures.append((future, audio_file))
        
        # Wait for all tasks to complete and collect results
        for future, audio_file in futures:
            if future.result():
                audio_files.append(audio_file)
    
    # Merge audio files if all chunks were generated successfully
    if len(audio_files) == len(chunks):
        final_audio = f'output/{essay_title.lower()}.mp3'
        return merge_audio_files(audio_files, final_audio)
    else:
        print("Failed to generate all audio chunks")
        return False

if __name__ == "__main__":
    # Process the next 3 essays after "Do"
    essays_to_process = [
        {"title": "Woke", "url": "https://paulgraham.com/woke.html"},
        {"title": "When", "url": "https://paulgraham.com/when.html"},
        {"title": "Writes", "url": "https://paulgraham.com/writes.html"}
    ]
    
    for essay in essays_to_process:
        print(f"\nProcessing essay: {essay['title']}")
        success = process_essay(essay['url'], essay['title'])
        if success:
            print(f"Successfully generated audio for '{essay['title']}'")
        else:
            print(f"Failed to generate audio for '{essay['title']}'") 