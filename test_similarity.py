import os
import pandas as pd
from data_loader import clean_and_prepare_dataset, load_data, CLEANED_FILE_PATH
from similarity import VibeSimilarityEngine, VIBE_FEATURES

def test_pipeline():
    print("=== Memulai Pengujian Pipeline Vibe Music Finder ===")
    
    # 1. Jalankan download dan cleaning
    print("\n1. Menguji Data Loader...")
    success = clean_and_prepare_dataset()
    if not success:
        print("[FAIL] data_loader gagal mengunduh atau membersihkan data.")
        return False
        
    if not os.path.exists(CLEANED_FILE_PATH):
        print(f"[FAIL] File {CLEANED_FILE_PATH} tidak ditemukan setelah pembersihan.")
        return False
        
    print(f"[SUCCESS] File dataset bersih terbentuk di {CLEANED_FILE_PATH}")
    
    # 2. Muat data
    print("\n2. Menguji Pengisian Memori (Load Data)...")
    df = load_data()
    if df is None or df.empty:
        print("[FAIL] DataFrame kosong atau None setelah dimuat.")
        return False
    print(f"[SUCCESS] Memuat {len(df)} lagu ke memori.")
    
    # 3. Inisialisasi engine
    print("\n3. Menguji Inisialisasi Similarity Engine...")
    try:
        engine = VibeSimilarityEngine(df)
        print("[SUCCESS] Engine berhasil diinisialisasi dan fitur diskalakan.")
    except Exception as e:
        print(f"[FAIL] Inisialisasi engine error: {e}")
        return False
        
    # 4. Uji Kemiripan berdasarkan ID Lagu
    print("\n4. Menguji Rekomendasi berdasarkan Lagu Asal...")
    # Kita ambil satu lagu secara acak dari database untuk dijadikan target
    sample_song = df.iloc[100]
    print(f"Lagu Asal: '{sample_song['track_name']}' oleh {sample_song['artists']} (ID: {sample_song['track_id']})")
    
    try:
        recommendations = engine.find_similar_by_track_id(sample_song['track_id'], top_n=5)
        print(f"[SUCCESS] Menemukan {len(recommendations)} lagu rekomendasi.")
        for idx, (_, rec) in enumerate(recommendations.iterrows()):
            print(f"   [{idx+1}] {rec['artists']} - {rec['track_name']} (Kecocokan: {rec['similarity_pct']:.2f}%)")
    except Exception as e:
        print(f"[FAIL] Pencarian kemiripan lagu error: {e}")
        return False
        
    # 5. Uji Kemiripan berdasarkan Vibe Kustom
    print("\n5. Menguji Rekomendasi berdasarkan Vibe Kustom...")
    custom_vibe = {
        'danceability': 0.8,
        'energy': 0.9,
        'loudness': -5.0,
        'speechiness': 0.05,
        'acousticness': 0.1,
        'instrumentalness': 0.0,
        'liveness': 0.15,
        'valence': 0.85,
        'tempo': 128.0
    }
    
    try:
        recommendations = engine.find_similar_by_features(custom_vibe, top_n=5)
        print(f"[SUCCESS] Menemukan {len(recommendations)} lagu untuk vibe kustom.")
        for idx, (_, rec) in enumerate(recommendations.iterrows()):
            print(f"   [{idx+1}] {rec['artists']} - {rec['track_name']} (Kecocokan: {rec['similarity_pct']:.2f}%)")
    except Exception as e:
        print(f"[FAIL] Pencarian vibe kustom error: {e}")
        return False
        
    print("\n[SUCCESS] SEMUA PENGUJIAN BERHASIL DISELESAIKAN!")
    return True

if __name__ == "__main__":
    test_pipeline()
