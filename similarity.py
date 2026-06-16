import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# Fitur audio yang digunakan untuk menentukan "Vibe"
VIBE_FEATURES = [
    'danceability',
    'energy',
    'loudness',
    'speechiness',
    'acousticness',
    'instrumentalness',
    'liveness',
    'valence',
    'tempo'
]

class VibeSimilarityEngine:
    def __init__(self, df):
        self.df = df
        self.scaler = MinMaxScaler()
        
        # Ekstrak dan skalakan fitur audio ke rentang [0, 1]
        raw_features = self.df[VIBE_FEATURES].values
        self.scaled_features = self.scaler.fit_transform(raw_features)
        
    def find_similar_by_features(self, target_features, genre_filter=None, exclude_track_id=None, top_n=10):
        """
        Mencari lagu yang memiliki kemiripan tertinggi berdasarkan array target_features.
        target_features harus berupa kamus atau array yang berisi nilai untuk VIBE_FEATURES.
        """
        # Ubah target_features ke format array 2D jika diperlukan
        if isinstance(target_features, dict):
            target_arr = np.array([[target_features[f] for f in VIBE_FEATURES]])
        else:
            target_arr = np.array(target_features).reshape(1, -1)
            
        # Skalakan fitur target menggunakan scaler yang sama
        scaled_target = self.scaler.transform(target_arr)
        
        # Hitung cosine similarity antara target dengan seluruh database
        similarities = cosine_similarity(scaled_target, self.scaled_features).flatten()
        
        # Buat salinan dataframe dan tambahkan skor kemiripan
        results_df = self.df.copy()
        results_df['similarity_score'] = similarities
        
        # Konversi ke persentase kecocokan (0 sampai 100)
        # Cosine similarity berkisar -1 hingga 1, kita petakan ke 0 - 100%
        results_df['similarity_pct'] = (results_df['similarity_score'] + 1) / 2 * 100
        
        # Filter berdasarkan ID lagu yang ingin dikecualikan (misal: lagu asal)
        if exclude_track_id:
            results_df = results_df[results_df['track_id'] != exclude_track_id]
            
        # Filter berdasarkan genre jika ditentukan
        if genre_filter and genre_filter.lower() != 'all':
            # Pencarian substring tidak sensitif huruf besar-kecil karena track_genre berisi gabungan genre
            results_df = results_df[results_df['track_genre'].str.contains(genre_filter, case=False, na=False)]
            
        # Urutkan berdasarkan skor kemiripan tertinggi dan popularitas
        results_df = results_df.sort_values(by=['similarity_score', 'popularity'], ascending=[False, False])
        
        return results_df.head(top_n)

    def find_similar_by_track_id(self, track_id, genre_filter=None, top_n=10):
        """Mencari lagu yang mirip berdasarkan track_id dari lagu yang sudah ada."""
        track_row = self.df[self.df['track_id'] == track_id]
        if track_row.empty:
            raise ValueError(f"Track ID {track_id} tidak ditemukan di database.")
            
        # Ambil nilai fitur audio dari lagu tersebut
        target_features = track_row[VIBE_FEATURES].iloc[0].to_dict()
        
        return self.find_similar_by_features(
            target_features, 
            genre_filter=genre_filter, 
            exclude_track_id=track_id, 
            top_n=top_n
        )
