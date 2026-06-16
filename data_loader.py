import os
import requests
import pandas as pd
import streamlit as st

DATA_URL = "https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset/resolve/main/dataset.csv"
RAW_FILE_PATH = "spotify_tracks_raw.csv"
CLEANED_FILE_PATH = "spotify_tracks_cleaned.csv"

def download_dataset():
    """Downloads the raw dataset from Hugging Face if it doesn't exist locally."""
    if os.path.exists(RAW_FILE_PATH):
        print("Raw dataset already exists.")
        return True
    
    print(f"Downloading dataset from {DATA_URL}...")
    try:
        response = requests.get(DATA_URL, stream=True)
        response.raise_for_status()
        
        # Download file with a progress print (Streamlit will handle spinner)
        with open(RAW_FILE_PATH, 'wb') as f:
            total_length = int(response.headers.get('content-length', 0))
            dl = 0
            for chunk in response.iter_content(chunk_size=1024*1024): # 1MB chunks
                if chunk:
                    f.write(chunk)
                    dl += len(chunk)
                    done = int(50 * dl / total_length) if total_length else 0
                    print(f"\rDownloading: [{'=' * done}{' ' * (50-done)}] {dl/(1024*1024):.1f}MB", end='')
        print("\nDownload completed successfully!")
        return True
    except Exception as e:
        print(f"\nFailed to download dataset: {e}")
        if os.path.exists(RAW_FILE_PATH):
            os.remove(RAW_FILE_PATH)
        return False

def clean_and_prepare_dataset():
    """Reads the raw dataset, deduplicates by track_id while aggregating genres, and saves it."""
    if os.path.exists(CLEANED_FILE_PATH):
        print("Cleaned dataset already exists.")
        return True
    
    if not download_dataset():
        return False
        
    print("Processing and cleaning dataset...")
    try:
        df = pd.read_csv(RAW_FILE_PATH)
        
        # Drop the unnamed column if it exists
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])
            
        # Group by track_id to clean duplicates (since a song can have multiple genres)
        # We aggregate the genres into a list/comma separated string, and take the first of other features.
        # But we also sort by popularity descending first so we keep metadata for the most popular version if IDs differ.
        df = df.sort_values(by='popularity', ascending=False)
        
        # Aggregation dictionary
        agg_dict = {
            'artists': 'first',
            'album_name': 'first',
            'track_name': 'first',
            'popularity': 'max',
            'duration_ms': 'first',
            'explicit': 'first',
            'danceability': 'first',
            'energy': 'first',
            'key': 'first',
            'loudness': 'first',
            'mode': 'first',
            'speechiness': 'first',
            'acousticness': 'first',
            'instrumentalness': 'first',
            'liveness': 'first',
            'valence': 'first',
            'tempo': 'first',
            'time_signature': 'first',
            'track_genre': lambda x: ", ".join(sorted(list(set(x.dropna()))))
        }
        
        # Group by track_id
        cleaned_df = df.groupby('track_id').agg(agg_dict).reset_index()
        
        # Save to CSV
        cleaned_df.to_csv(CLEANED_FILE_PATH, index=False)
        print(f"Cleaned dataset saved to {CLEANED_FILE_PATH} with {len(cleaned_df)} unique tracks.")
        return True
    except Exception as e:
        print(f"Error processing dataset: {e}")
        return False

@st.cache_data(show_spinner="Loading and preparing song database...")
def load_data():
    """Loads the cleaned dataset into memory, cached by Streamlit."""
    if not os.path.exists(CLEANED_FILE_PATH):
        success = clean_and_prepare_dataset()
        if not success:
            st.error("Gagal memproses database lagu. Pastikan koneksi internet aktif.")
            return None
            
    df = pd.read_csv(CLEANED_FILE_PATH)
    # Handle any potential NaNs in categorical columns
    df['track_name'] = df['track_name'].fillna('Unknown Track')
    df['artists'] = df['artists'].fillna('Unknown Artist')
    df['album_name'] = df['album_name'].fillna('Unknown Album')
    df['track_genre'] = df['track_genre'].fillna('unknown')
    
    return df

if __name__ == "__main__":
    # Test execution
    clean_and_prepare_dataset()
