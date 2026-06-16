import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data_loader import load_data, CLEANED_FILE_PATH
from similarity import VibeSimilarityEngine, VIBE_FEATURES
from auth import verify_user, register_user

# Pengaturan halaman Streamlit
st.set_page_config(
    page_title="VibeFinder - Cari Musik Berdasarkan Karakter Suara",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan premium dengan tema gelap ala Spotify
st.html("""
<style>
    /* Mengubah font dan background dasar */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Gelasmorfisme untuk kartu */
    .song-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    
    .song-card:hover {
        background: rgba(255, 255, 255, 0.07);
        border-color: #1DB954;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(29, 185, 84, 0.15);
    }
    
    /* Tag Genre */
    .genre-tag {
        display: inline-block;
        background: rgba(29, 185, 84, 0.15);
        color: #1DB954;
        border: 1px solid rgba(29, 185, 84, 0.3);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin-right: 5px;
        margin-bottom: 5px;
        text-transform: capitalize;
    }
    
    /* Match Percentage Badge */
    .match-badge {
        background: linear-gradient(135deg, #1DB954, #128C7E);
        color: white;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Header Estetis */
    .main-title {
        font-weight: 800;
        background: linear-gradient(135deg, #1DB954 30%, #8A2BE2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        margin-bottom: 5px;
        text-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .sub-title {
        color: #B3B3B3;
        font-size: 1.1rem;
        margin-bottom: 30px;
        font-weight: 300;
    }
    
    /* Sembunyikan footer streamlit */
    footer {visibility: hidden;}
</style>
""")# Inisialisasi status login di Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# Tampilkan halaman Login / Registrasi jika belum terautentikasi
if not st.session_state['logged_in']:
    st.markdown('<h1 class="main-title" style="text-align: center;">🎵 VibeFinder</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title" style="text-align: center;">Sistem Pencari & Rekomendasi Lagu Berdasarkan Karakteristik Audio</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.html("""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 24px; margin-bottom: 20px;">
            <h3 style="text-align: center; color: #1DB954; margin-top: 0;">🔐 Autentikasi Pengguna</h3>
            <p style="text-align: center; color: #B3B3B3; font-size: 0.9rem;">Silakan masuk atau daftarkan akun baru untuk menggunakan sistem.</p>
        </div>
        """)
        
        tab_login, tab_register = st.tabs(["🔑 Masuk (Login)", "📝 Daftar Baru (Register)"])
        
        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Masukkan username Anda...")
                password = st.text_input("Password", type="password", placeholder="Masukkan password Anda...")
                login_btn = st.form_submit_button("Masuk", width="stretch")
                
                if login_btn:
                    if verify_user(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username.strip().lower()
                        st.success("Login berhasil! Memuat aplikasi...")
                        st.rerun()
                    else:
                        st.error("Username atau password salah.")
                        
        with tab_register:
            with st.form("register_form"):
                reg_username = st.text_input("Username Baru", placeholder="Pilih username unik...")
                reg_password = st.text_input("Password Baru", type="password", placeholder="Pilih password kuat...")
                reg_confirm = st.text_input("Konfirmasi Password Baru", type="password", placeholder="Ketik ulang password...")
                register_btn = st.form_submit_button("Daftarkan Akun", width="stretch")
                
                if register_btn:
                    reg_username = reg_username.strip()
                    if not reg_username or not reg_password:
                        st.error("Username dan password tidak boleh kosong.")
                    elif reg_password != reg_confirm:
                        st.error("Konfirmasi password tidak cocok.")
                    else:
                        if register_user(reg_username, reg_password):
                            st.success("Registrasi berhasil! Silakan pindah ke tab 'Masuk (Login)'.")
                        else:
                            st.error("Username sudah terdaftar. Silakan pilih username lain.")
                            
        st.info("💡 Akun percobaan bawaan:\n* **Username**: `admin` \n* **Password**: `admin123`")
    st.stop() # Hentikan eksekusi untuk user yang belum login

# Jika sudah login, lanjutkan memuat data & aplikasi
df = load_data()

if df is not None:
    engine = VibeSimilarityEngine(df)
    
    # ------------------ HEADER SECTION ------------------
    st.markdown('<h1 class="main-title">🎵 VibeFinder</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Cari lagu dengan kemiripan karakter suara (tempo, energi, emosi) secara instan menggunakan matematika Cosine Similarity.</p>', unsafe_allow_html=True)
    st.markdown(f"Selamat datang kembali, **{st.session_state['username'].capitalize()}**! 👋")
    
    # ------------------ SIDEBAR CONFIGURATION ------------------
    st.sidebar.markdown("### ⚙️ Pengaturan & Filter")
    
    # Tampilkan info user & Logout
    st.sidebar.markdown(f"👤 Masuk sebagai: **{st.session_state['username'].capitalize()}**")
    if st.sidebar.button("🔓 Keluar (Logout)", width="stretch"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # Kumpulkan semua genre unik untuk filter
    all_genres = set()
    for genres in df['track_genre'].dropna():
        # Beberapa genre digabung dengan koma, pisah kembali
        for g in genres.split(','):
            all_genres.add(g.strip())
            
    sorted_genres = ['All'] + sorted(list(all_genres))
    selected_genre = st.sidebar.selectbox(
        "Saring berdasarkan Genre:",
        options=sorted_genres,
        help="Hanya cari rekomendasi dari genre lagu tertentu."
    )
    
    limit_recommendations = st.sidebar.slider(
        "Jumlah Rekomendasi:",
        min_value=3,
        max_value=20,
        value=5,
        step=1
    )
    
    # Informational Sidebar Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Fitur Audio yang Dianalisis:")
    st.sidebar.info(
        "1. **Danceability**: Kesesuaian lagu untuk menari.\n"
        "2. **Energy**: Intensitas dan dinamika suara.\n"
        "3. **Valence**: Suasana hati (Rendah = Sedih/Depresi, Tinggi = Bahagia/Ceria).\n"
        "4. **Acousticness**: Keaslian instrumen fisik vs elektronik.\n"
        "5. **Instrumentalness**: Probabilitas lagu tidak memiliki vokal.\n"
        "6. **Tempo**: Kecepatan ketukan per menit (BPM)."
    )
    
    # ------------------ MAIN TABS ------------------
    tab1, tab2 = st.tabs(["🔍 Berdasarkan Lagu Favorit", "🎛️ Desain Vibe Sendiri"])
    
    # --- TAB 1: SEARCH BY SONG ---
    with tab1:
        st.write("Cari lagu favorit Anda di database kami untuk menganalisis profil getarannya (*vibe profile*) dan mencari lagu sejenis.")
        
        search_query = st.text_input(
            "Ketik Judul Lagu atau Nama Penyanyi:",
            placeholder="Contoh: Yellow, Coldplay, Queen, Billie Eilish...",
            key="song_search"
        )
                
        if search_query:
            # Cari lagu yang cocok di database
            query_matches = df[
                df['track_name'].str.contains(search_query, case=False, na=False) |
                df['artists'].str.contains(search_query, case=False, na=False)
            ].head(15)
            
            if not query_matches.empty:
                # Format pilihan dropdown agar mudah dibaca
                options_list = query_matches['track_id'].tolist()
                
                def format_label(tid):
                    row = query_matches[query_matches['track_id'] == tid].iloc[0]
                    return f"{row['artists']} - {row['track_name']} (Album: {row['album_name']})"
                    
                selected_track_id = st.selectbox(
                    "Pilih lagu yang Anda maksud dari hasil pencarian berikut:",
                    options=options_list,
                    format_func=format_label
                )
                
                # Load detail lagu yang dipilih
                song_data = df[df['track_id'] == selected_track_id].iloc[0]
                
                # Layout untuk Analisis Lagu Asal
                col_song_info, col_radar = st.columns([1, 1])
                
                with col_song_info:
                    st.subheader("🎵 Lagu yang Dipilih")
                    st.markdown(f"**Judul**: `{song_data['track_name']}`")
                    st.markdown(f"**Artis**: `{song_data['artists']}`")
                    st.markdown(f"**Album**: `{song_data['album_name']}`")
                    st.markdown(f"**Popularitas**: `{int(song_data['popularity'])}/100`")
                    st.markdown(f"**Tempo**: `{int(song_data['tempo'])} BPM`")
                    
                    # Tampilkan genre-tag
                    genres_list = str(song_data['track_genre']).split(',')
                    genre_html = "".join([f'<span class="genre-tag">{g.strip()}</span>' for g in genres_list])
                    st.markdown(genre_html, unsafe_allow_html=True)
                    st.write("")
                    
                    # Embed Spotify player untuk lagu asal
                    spotify_embed_url = f"https://open.spotify.com/embed/track/{selected_track_id}?utm_source=generator&theme=0"
                    st.iframe(
                        src=spotify_embed_url,
                        height=80
                    )
                    
                with col_radar:
                    # Buat Radar Chart untuk memvisualisasikan Vibe Profile
                    features_vals = [song_data[f] for f in VIBE_FEATURES[:-1]] # Kecuali tempo karena satuannya berbeda
                    # Tambahkan tempo yang dinormalisasi ke list agar lengkap
                    # Kita normalisasikan tempo secara manual untuk visualisasi radar (e.g. dibagi 200)
                    normalized_tempo = min(song_data['tempo'] / 200, 1.0)
                    features_vals.append(normalized_tempo)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=features_vals,
                        theta=[f.capitalize() for f in VIBE_FEATURES],
                        fill='toself',
                        fillcolor='rgba(29, 185, 84, 0.2)',
                        line=dict(color='#1DB954', width=2),
                        name=song_data['track_name']
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 1]
                            )
                        ),
                        showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=40, r=40, t=20, b=20),
                        height=250
                    )
                    st.plotly_chart(fig, width="stretch")
                
                # --- CALCULATE & DISPLAY RECOMMENDATIONS ---
                st.write("---")
                st.subheader(f"✨ {limit_recommendations} Lagu dengan Vibe Paling Serupa")
                
                with st.spinner("Menghitung kemiripan lagu..."):
                    recommendations = engine.find_similar_by_track_id(
                        selected_track_id, 
                        genre_filter=selected_genre, 
                        top_n=limit_recommendations
                    )
                    
                if not recommendations.empty:
                    for idx, (_, rec_song) in enumerate(recommendations.iterrows()):
                        # Kartu Lagu Rekomendasi
                        with st.container():
                            st.markdown(f"""
                            <div class="song-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                    <div>
                                        <span style="font-size: 1.2rem; font-weight: 600; color: white;">{idx+1}. {rec_song['track_name']}</span>
                                        <span style="font-size: 1rem; color: #B3B3B3; margin-left: 8px;">by {rec_song['artists']}</span>
                                    </div>
                                    <span class="match-badge">🎯 Kecocokan: {rec_song['similarity_pct']:.1f}%</span>
                                </div>
                                <div style="margin-bottom: 12px;">
                                    <strong>Album:</strong> {rec_song['album_name']} | 
                                    <strong>Tempo:</strong> {int(rec_song['tempo'])} BPM |
                                    <strong>Popularitas:</strong> {int(rec_song['popularity'])}/100
                                </div>
                                <div style="margin-bottom: 12px;">
                                    {"".join([f'<span class="genre-tag">{g.strip()}</span>' for g in str(rec_song['track_genre']).split(',')])}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Player musik untuk rekomendasi
                            rec_embed_url = f"https://open.spotify.com/embed/track/{rec_song['track_id']}?utm_source=generator&theme=0"
                            st.iframe(
                                src=rec_embed_url,
                                height=80
                            )
                else:
                    st.warning("Tidak ditemukan lagu yang cocok dengan kriteria saringan genre Anda.")
                    
            else:
                st.error("Lagu atau penyanyi tidak ditemukan di database. Coba kata kunci lain.")
        else:
            st.info("💡 Silakan ketik judul lagu favorit Anda atau klik tombol 'Butuh Ide' di atas untuk memulai.")
            
    # --- TAB 2: CUSTOM VIBE CREATOR ---
    with tab2:
        st.write("Sesuaikan geser (*slider*) di bawah ini untuk merancang profil getaran suara unik Anda. Algoritma akan mencari lagu yang paling cocok dengan pola kombinasi yang Anda inginkan.")
        
        col_sliders_1, col_sliders_2 = st.columns([1, 1])
        
        with col_sliders_1:
            custom_danceability = st.slider("💃 Danceability (Kesesuaian Dansa)", 0.0, 1.0, 0.5, 0.05, 
                                            help="Semakin tinggi, lagu semakin memiliki ritme ketukan yang cocok untuk berdansa.")
            custom_energy = st.slider("⚡ Energy (Energi & Semangat)", 0.0, 1.0, 0.5, 0.05,
                                      help="Energi mengukur intensitas kebisingan, keaktifan, dan kecepatan persepsi lagu.")
            custom_valence = st.slider("☀️ Valence (Suasana Emosi)", 0.0, 1.0, 0.5, 0.05,
                                       help="Rendah = sedih, suram, marah. Tinggi = ceria, senang, bahagia.")
            custom_acousticness = st.slider("🎸 Acousticness (Keaslian Akustik)", 0.0, 1.0, 0.2, 0.05,
                                            help="Semakin tinggi, semakin besar kemungkinan instrumen dalam lagu bersifat akustik alami.")
            
        with col_sliders_2:
            custom_instrumentalness = st.slider("🎹 Instrumentalness (Tanpa Vokal)", 0.0, 1.0, 0.1, 0.05,
                                                help="Semakin tinggi, semakin sedikit vokal (bagus untuk musik latar/belajar).")
            custom_speechiness = st.slider("🗣️ Speechiness (Kata Terucap)", 0.0, 1.0, 0.1, 0.05,
                                           help="Tinggi menunjukkan banyak kata terucap (seperti talkshow, puisi, atau Rap).")
            custom_liveness = st.slider("👥 Liveness (Nuansa Panggung)", 0.0, 1.0, 0.1, 0.05,
                                        help="Mendeteksi kehadiran penonton. Tinggi berarti rekaman konser langsung.")
            custom_tempo = st.slider("⏱️ Tempo (Kecepatan BPM)", 50, 200, 120, 5,
                                     help="Ketukan per menit. Lambat (< 80), Sedang (90-120), Cepat (> 130).")
            
            # Loudness disetel secara otomatis di latar belakang demi kemudahan pengguna
            custom_loudness = -10.0 # dB (nilai rata-rata industri yang wajar)
            
        # Tombol Temukan Lagu
        st.write("")
        find_custom_btn = st.button("🚀 Temukan Lagu dengan Vibe Ini", width="stretch")
        
        if find_custom_btn:
            # Siapkan kamus fitur input
            custom_features = {
                'danceability': custom_danceability,
                'energy': custom_energy,
                'loudness': custom_loudness,
                'speechiness': custom_speechiness,
                'acousticness': custom_acousticness,
                'instrumentalness': custom_instrumentalness,
                'liveness': custom_liveness,
                'valence': custom_valence,
                'tempo': custom_tempo
            }
            
            # Tampilkan Radar Chart Desain Pengguna
            col_res_radar, col_res_text = st.columns([1, 1])
            
            with col_res_radar:
                st.subheader("📊 Profil Vibe yang Anda Desain")
                normalized_custom_tempo = min(custom_tempo / 200, 1.0)
                custom_vals = [custom_features[f] for f in VIBE_FEATURES[:-1]] + [normalized_custom_tempo]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=custom_vals,
                    theta=[f.capitalize() for f in VIBE_FEATURES],
                    fill='toself',
                    fillcolor='rgba(138, 43, 226, 0.2)',
                    line=dict(color='#8A2BE2', width=2),
                    name="Vibe Desain"
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=40, r=40, t=20, b=20),
                    height=250
                )
                st.plotly_chart(fig, width="stretch")
                
            with col_res_text:
                st.subheader("💡 Karakter Vibe:")
                # Interpretasi Vibe secara kualitatif agar interaktif dan premium
                mood_desc = []
                if custom_valence > 0.7: mood_desc.append("Ceria & Positif")
                elif custom_valence < 0.3: mood_desc.append("Melankolis/Sedih")
                
                if custom_energy > 0.7: mood_desc.append("Penuh Energi/Intens")
                elif custom_energy < 0.3: mood_desc.append("Santai/Calm")
                
                if custom_danceability > 0.7: mood_desc.append("Sangat Ritmis/Groovy")
                if custom_acousticness > 0.7: mood_desc.append("Akustik Organik")
                if custom_instrumentalness > 0.7: mood_desc.append("Tanpa Vokal (Instrumental)")
                
                if not mood_desc:
                    mood_desc.append("Seimbang (Moderate)")
                    
                st.info(f"Vibe Anda tergolong: **{', '.join(mood_desc)}** dengan tempo **{custom_tempo} BPM**.")
                
            st.write("---")
            st.subheader(f"✨ {limit_recommendations} Lagu Paling Cocok")
            
            with st.spinner("Mencocokkan lagu di database..."):
                recommendations = engine.find_similar_by_features(
                    custom_features,
                    genre_filter=selected_genre,
                    top_n=limit_recommendations
                )
                
            if not recommendations.empty:
                for idx, (_, rec_song) in enumerate(recommendations.iterrows()):
                    # Kartu Lagu Rekomendasi
                    with st.container():
                        st.markdown(f"""
                        <div class="song-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <div>
                                    <span style="font-size: 1.2rem; font-weight: 600; color: white;">{idx+1}. {rec_song['track_name']}</span>
                                    <span style="font-size: 1rem; color: #B3B3B3; margin-left: 8px;">by {rec_song['artists']}</span>
                                </div>
                                <span class="match-badge">🎯 Kecocokan: {rec_song['similarity_pct']:.1f}%</span>
                            </div>
                            <div style="margin-bottom: 12px;">
                                <strong>Album:</strong> {rec_song['album_name']} | 
                                <strong>Tempo:</strong> {int(rec_song['tempo'])} BPM |
                                <strong>Popularitas:</strong> {int(rec_song['popularity'])}/100
                            </div>
                            <div style="margin-bottom: 12px;">
                                {"".join([f'<span class="genre-tag">{g.strip()}</span>' for g in str(rec_song['track_genre']).split(',')])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Player musik untuk rekomendasi
                        rec_embed_url = f"https://open.spotify.com/embed/track/{rec_song['track_id']}?utm_source=generator&theme=0"
                        st.iframe(
                            src=rec_embed_url,
                            height=80
                        )
            else:
                st.warning("Tidak ditemukan lagu yang cocok dengan kriteria saringan genre Anda.")
else:
    st.error("Database lagu tidak tersedia. Pastikan program `data_loader.py` dijalankan dengan sukses.")
