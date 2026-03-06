#!/usr/bin/env python3
"""musicdb - interactive music search"""

import json
import os
import sys

class MusicDatabase:
    def __init__(self, data_path):
        self.data_path = data_path
        self.songs = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.data_path):
            print(f"Error: File not found: {self.data_path}", file=sys.stderr)
            sys.exit(1)
        with open(self.data_path, "r") as f:
            return json.load(f)

    def find_songs(self, query):
        query = query.lower()
        return [s for s in self.songs if
                query in s.get("title", "").lower() or
                query in s.get("artist", "").lower() or
                query in s.get("genre", "").lower()]

class Display:
    @staticmethod
    def show_results(results):
        if not results:
            print("\nNo matching songs found.")
            return
        print(f"\n--- Found {len(results)} Result(s) ---")
        for song in results:
            print(f"🎵 {song.get('title')} by {song.get('artist')}")
            print(f"   Year: {song.get('year')} | Genre: {song.get('genre')}")
            print("-" * 30)

def main():
    # Allow path as command-line argument (default to music_data.json in current dir)
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    else:
        data_file = "music_data.json"
        print(f"Using default data file: {data_file}")

    db = MusicDatabase(data_file)
    ui = Display()

    print("--- Music Database Search ---")
    while True:
        try:
            search_word = input("\nEnter a song, artist, or genre (or 'quit'): ").strip()
            if search_word.lower() in ("quit", "exit", "q"):
                break
            if not search_word:
                continue
            matching_songs = db.find_songs(search_word)
            ui.show_results(matching_songs)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
 
