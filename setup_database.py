import sqlite3
from werkzeug.security import generate_password_hash

# Membuat database dan tabel
conn = sqlite3.connect('lab_inventory.db')
c = conn.cursor()

# Tabel untuk pengguna
c.execute(''' 
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'user'
)
''')

# Tabel untuk peminjaman dengan kolom tanggal_peminjaman dan waktu_peminjaman
c.execute(''' 
CREATE TABLE IF NOT EXISTS peminjaman (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    nim TEXT,
    jenis_alat TEXT,
    tanggal_peminjaman TEXT,  -- Kolom untuk tanggal peminjaman
    waktu_peminjaman TEXT,     -- Kolom untuk jam peminjaman
    user_id INTEGER,
    status TEXT DEFAULT 'peminjaman diajukan',
    tanggal_selesai TEXT,      -- Kolom untuk tanggal selesai
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Menambahkan kolom tanggal_peminjaman, waktu_peminjaman, dan tanggal_selesai jika tabel sudah ada tetapi kolom belum ada
try:
    c.execute('ALTER TABLE peminjaman ADD COLUMN tanggal_peminjaman TEXT')
except sqlite3.OperationalError:
    # Kolom sudah ada, jadi kita bisa lanjut
    pass

try:
    c.execute('ALTER TABLE peminjaman ADD COLUMN waktu_peminjaman TEXT')
except sqlite3.OperationalError:
    # Kolom sudah ada, jadi kita bisa lanjut
    pass

try:
    c.execute('ALTER TABLE peminjaman ADD COLUMN tanggal_selesai TEXT')
except sqlite3.OperationalError:
    # Kolom sudah ada, jadi kita bisa lanjut
    pass

# Tambahkan pengguna admin secara manual
c.execute('INSERT OR IGNORE INTO users (email, password, role) VALUES (?, ?, ?)', 
          ('mhd.kadarfitrawan@gmail.com', generate_password_hash('fitrawan25'), 'admin'))

conn.commit()
conn.close()
