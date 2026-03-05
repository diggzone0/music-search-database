#!/usr/bin/env python3
"""This script looks through your music folder and makes a list of all your songs"""

import os
import json

# 👇 THIS IS THE ONLY LINE YOU NEED TO CHANGE
your_music_folder = "/mnt/e/mu51q/audio"

print("🎵 Let me look for your music files...")

# Find all the music files
all_songs = []
for folder, subfolders, files in os.walk(your_music_folder):
    for file in files:
        # Is this a music file?
        if file.endswith(('.mp3', '.flac', '.m4a', '.wav', '.ogg', '.aac')):
            full_path = os.path.join(folder, file)
            
            # Try to figure out the song name from the filename
            filename = file.replace('.mp3', '').replace('.flac', '').replace('.m4a', '').replace('.wav', '').replace('.ogg', '').replace('.aac', '')
            
            # If filename has " - ", maybe it's "Artist - Song"
            if ' - ' in filename:
                parts = filename.split(' - ', 1)
                artist, title = parts[0], parts[1]
            else:
                artist = "Unknown"
                title = filename
            
            all_songs.append({
                "title": title,
                "artist": artist,
                "year": "Unknown",
                "genre": "Unknown",
                "filepath": full_path
            })

print(f"📁 Found {len(all_songs)} songs!")

# Save everything to JSON
with open("music_data.json", "w") as f:
    json.dump(all_songs, f, indent=2)

print("✨ Done! Your song list is saved in 'music_data.json'")
print("👉 Now you can search with: python3 musicdb.py")
