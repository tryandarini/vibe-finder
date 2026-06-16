import os
import json
import hashlib

USERS_FILE = "users.json"

def hash_password(password):
    """Mengamankan password menggunakan hash SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def load_users():
    """Memuat daftar user dari file users.json."""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    """Menyimpan daftar user ke file users.json."""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        return True
    except Exception:
        return False

def initialize_default_users():
    """Menginisialisasi akun admin bawaan jika file users.json belum ada."""
    users = load_users()
    # Jika admin belum terdaftar, tambahkan default admin
    if "admin" not in users:
        users["admin"] = hash_password("admin123")
        save_users(users)

def register_user(username, password):
    """
    Mendaftarkan user baru.
    Mengembalikan True jika sukses, False jika username sudah ada.
    """
    users = load_users()
    username = username.strip().lower()
    
    if not username or not password:
        return False
        
    if username in users:
        return False  # Username sudah terdaftar
        
    users[username] = hash_password(password)
    return save_users(users)

def verify_user(username, password):
    """
    Memverifikasi kombinasi username dan password.
    Mengembalikan True jika cocok, False jika salah.
    """
    users = load_users()
    username = username.strip().lower()
    
    if username not in users:
        return False
        
    return users[username] == hash_password(password)

# Inisialisasi awal saat modul diimpor
initialize_default_users()
