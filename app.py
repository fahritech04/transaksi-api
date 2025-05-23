from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')
PORT = int(os.getenv('PORT', 5000))

# Fungsi untuk koneksi ke database PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, sslmode='require')
    return conn

# CREATE: Menambah transaksi baru
@app.route('/api/transaksi', methods=['POST'])
def create_transaksi():
    data = request.get_json()

    nama_transaksi = data.get('nama_transaksi')
    mata_uang_asal = data.get('mata_uang_asal')
    mata_uang_tujuan = data.get('mata_uang_tujuan')
    jumlah_usd = data.get('jumlah_usd')
    jumlah_idr = data.get('jumlah_idr')
    nilai_tukar = data.get('nilai_tukar')
    tanggal = data.get('tanggal')
    kategori_transaksi = data.get('kategori_transaksi')
    gambar = data.get('gambar')
    status_pembayaran = data.get('status_pembayaran')
    catatan = data.get('catatan')

    # Validasi pilihan mata uang dan status pembayaran
    valid_mata_uang = ['USD', 'IDR']
    valid_status = ['Paid', 'Pending', 'Success']
    
    if mata_uang_asal not in valid_mata_uang or mata_uang_tujuan not in valid_mata_uang:
        return jsonify({'error': 'Mata uang asal atau tujuan tidak valid'}), 400
    
    if status_pembayaran not in valid_status:
        return jsonify({'error': 'Status pembayaran tidak valid'}), 400

    if not all([nama_transaksi, mata_uang_asal, mata_uang_tujuan, jumlah_usd, jumlah_idr, nilai_tukar, tanggal, kategori_transaksi, status_pembayaran]):
        return jsonify({'error': 'Semua field wajib diisi'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO transaksi (nama_transaksi, mata_uang_asal, mata_uang_tujuan, jumlah_usd, jumlah_idr, nilai_tukar, tanggal, kategori_transaksi, gambar, status_pembayaran, catatan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (nama_transaksi, mata_uang_asal, mata_uang_tujuan, jumlah_usd, jumlah_idr, nilai_tukar, tanggal, kategori_transaksi, gambar, status_pembayaran, catatan))
        new_transaksi = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Transaksi berhasil ditambahkan', 'transaksi': new_transaksi}), 201
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

# READ: Mendapatkan semua transaksi
@app.route('/api/transaksi', methods=['GET'])
def get_transaksi():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM transaksi;')
    transaksi = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(transaksi)

# READ: Mendapatkan transaksi berdasarkan ID
@app.route('/api/transaksi/<int:id>', methods=['GET'])
def get_transaksi_by_id(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM transaksi WHERE id = %s;', (id,))
    transaksi = cur.fetchone()
    cur.close()
    conn.close()
    if transaksi is None:
        return jsonify({'error': 'Transaksi tidak ditemukan'}), 404
    return jsonify(transaksi)

# UPDATE: Memperbarui transaksi berdasarkan ID
@app.route('/api/transaksi/<int:id>', methods=['PUT'])
def update_transaksi(id):
    data = request.get_json()

    nama_transaksi = data.get('nama_transaksi')
    mata_uang_asal = data.get('mata_uang_asal')
    mata_uang_tujuan = data.get('mata_uang_tujuan')
    jumlah_usd = data.get('jumlah_usd')
    jumlah_idr = data.get('jumlah_idr')
    nilai_tukar = data.get('nilai_tukar')
    tanggal = data.get('tanggal')
    kategori_transaksi = data.get('kategori_transaksi')
    gambar = data.get('gambar')
    status_pembayaran = data.get('status_pembayaran')
    catatan = data.get('catatan')

    # Validasi pilihan mata uang dan status pembayaran
    valid_mata_uang = ['USD', 'IDR']
    valid_status = ['Paid', 'Pending', 'Success']
    
    if mata_uang_asal not in valid_mata_uang or mata_uang_tujuan not in valid_mata_uang:
        return jsonify({'error': 'Mata uang asal atau tujuan tidak valid'}), 400
    
    if status_pembayaran not in valid_status:
        return jsonify({'error': 'Status pembayaran tidak valid'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE transaksi
        SET nama_transaksi = %s, mata_uang_asal = %s, mata_uang_tujuan = %s, jumlah_usd = %s, jumlah_idr = %s, nilai_tukar = %s, 
            tanggal = %s, kategori_transaksi = %s, gambar = %s, status_pembayaran = %s, catatan = %s
        WHERE id = %s
        RETURNING *;
    """, (nama_transaksi, mata_uang_asal, mata_uang_tujuan, jumlah_usd, jumlah_idr, nilai_tukar, tanggal, kategori_transaksi, gambar, status_pembayaran, catatan, id))
    updated_transaksi = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if updated_transaksi is None:
        return jsonify({'error': 'Transaksi tidak ditemukan'}), 404
    return jsonify({'message': 'Transaksi berhasil diperbarui', 'transaksi': updated_transaksi})

# DELETE: Menghapus transaksi berdasarkan ID
@app.route('/api/transaksi/<int:id>', methods=['DELETE'])
def delete_transaksi(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM transaksi WHERE id = %s RETURNING *;', (id,))
    deleted_transaksi = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if deleted_transaksi is None:
        return jsonify({'error': 'Transaksi tidak ditemukan'}), 404
    return jsonify({'message': 'Transaksi berhasil dihapus', 'transaksi': deleted_transaksi})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
