from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", 'default_secret_key')  # Simpan secret_key di variabel lingkungan dalam produksi

# Helper untuk koneksi database
def get_db_connection():
    conn = sqlite3.connect('lab_inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

# Rute untuk Halaman Utama
@app.route('/')
def index():
    return redirect(url_for('login'))

# Rute untuk Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Email atau password salah.', 'danger')

    return render_template('login.html')

# Rute untuk Pendaftaran
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        with get_db_connection() as conn:
            try:
                conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
                conn.commit()
                flash('Pendaftaran berhasil! Silakan login.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Email sudah digunakan. Silakan gunakan email lain.', 'danger')
    
    return render_template('register.html')

# Rute untuk Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu.', 'warning')
        return redirect(url_for('login'))

    user_role = session.get('role', 'user')
    with get_db_connection() as conn:
        if user_role == 'admin':
            peminjaman_list = conn.execute('SELECT * FROM peminjaman').fetchall()
        else:
            peminjaman_list = conn.execute(
                'SELECT * FROM peminjaman WHERE user_id = ?', (session['user_id'],)
            ).fetchall()
    
    return render_template('dashboard.html', peminjaman_list=peminjaman_list, role=user_role)

# Rute untuk Form Peminjaman
@app.route('/form_peminjaman', methods=['GET', 'POST'])
def form_peminjaman():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nama = request.form['nama']
        nim = request.form['nim']
        jenis_alat = request.form['jenis_alat']
        tanggal_peminjaman = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Menyimpan tanggal dan waktu saat ini

        with get_db_connection() as conn:
            conn.execute('INSERT INTO peminjaman (nama, nim, jenis_alat, tanggal_peminjaman, user_id) VALUES (?, ?, ?, ?, ?)', 
                         (nama, nim, jenis_alat, tanggal_peminjaman, session['user_id']))
            conn.commit()
        
        return redirect(url_for('dashboard'))

    # Kirim tanggal dan waktu saat ini ke template
    return render_template('form_peminjaman.html', current_datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Rute untuk Riwayat Peminjaman
@app.route('/riwayat_peminjaman')
def riwayat_peminjaman():
    if 'user_id' not in session:
        flash('Anda harus login untuk melihat riwayat peminjaman.', 'warning')
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        riwayat = conn.execute(
            'SELECT * FROM peminjaman WHERE user_id = ?', (session['user_id'],)
        ).fetchall()

    print("Riwayat Peminjaman:", riwayat)  # Debugging

    return render_template('riwayat_peminjaman.html', riwayat=riwayat)


# Rute untuk Mengubah Status Peminjaman
@app.route('/update_status/<int:peminjaman_id>/<status>', methods=['POST'])
def update_status(peminjaman_id, status):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        if status == "Selesai":
            tanggal_selesai = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute('UPDATE peminjaman SET status = ?, tanggal_selesai = ? WHERE id = ?', 
                         (status, tanggal_selesai, peminjaman_id))
        else:
            conn.execute('UPDATE peminjaman SET status = ? WHERE id = ?', (status, peminjaman_id))
        conn.commit()
    
    return redirect(url_for('dashboard'))



# Rute untuk Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Anda berhasil logout.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
