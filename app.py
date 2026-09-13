import os
from dotenv import load_dotenv
import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 1. Load secret keys from your hidden .env file
load_dotenv()

# Configure API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# Authenticate with OpenAI
openai.api_key = OPENAI_API_KEY

# Authenticate with Spotify (This opens a browser window to log you in)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-modify-public"
))

def generate_vibe_tracks(mood_prompt):
    """Uses OpenAI to turn a mood description into a list of 5 songs."""
    print(f"\n🔮 Asking AI to generate tracks for vibe: '{mood_prompt}'...")
    
    system_instruction = "You are a music expert. Output exactly 5 real tracks matching the user's mood. Format exactly like this: Track Name - Artist Name (one per line). Do not write anything else."
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini", # Using a fast, modern model
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": mood_prompt}
        ]
    )
    
    ai_output = response.choices[0].message.content
    lines = [line.strip() for line in ai_output.strip().split("\n") if line.strip()]
    return lines

def create_spotify_playlist(playlist_name, track_queries):
    """Searches Spotify for the tracks and saves them to a new playlist."""
    # Find current user's ID
    user_id = sp.current_user()["id"]
    
    # Create an empty playlist
    print(f"🎵 Creating a new Spotify playlist: '{playlist_name}'...")
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    playlist_id = new_playlist["id"]
    
    track_uris = []
    # Search for each song track on Spotify
    for query in track_queries:
        print(f"🔍 Searching Spotify for: {query}")
        results = sp.search(q=query, limit=1, type='track')
        tracks = results['tracks']['items']
        
        if tracks:
            track_uris.append(tracks[0]['uri'])
        else:
            print(f"⚠️ Could not find '{query}' on Spotify.")
            
    # Add songs to the playlist if any were found
    if track_uris:
        sp.playlist_add_items(playlist_id=playlist_id, items=track_uris)
        print(f"✅ Success! Your playlist is ready on Spotify!")
    else:
        print("❌ No songs could be added.")

# 🚀 MAIN RUNNER LOOP
if __name__ == "__main__":
    print("=== Welcome to the AI Spotify Vibe Playlist Generator ===")
    
    # Ask user what vibe they want
    user_vibe = input("What kind of music vibe or mood are you feeling right now? \n(e.g., 'Rainy Sunday lofi jazz' or 'Cyberpunk gym motivation'): ")
    
    try:
        # Step 1: Get song ideas from AI
        suggested_tracks = generate_vibe_tracks(user_vibe)
        print("\n✨ AI Suggested Tracks:")
        for track in suggested_tracks:
            print(f" - {track}")
            
        # Step 2: Push them directly to Spotify
        playlist_title = f"AI Vibe: {user_vibe.title()}"
        create_spotify_playlist(playlist_title, suggested_tracks)
        
    except Exception as e:
        print(f"\n⚠️ An error occurred: {e}")
        print("Tip: Make sure your .env file keys are accurate and active!")
