import hashlib
import sqlite3

from Models.models import Produk, Transaksi
from Exceptions.exceptions import TransaksiSudahDibatalkanError, TransaksiTidakDitemukanError


class Database:
    def __init__(self, name="ecommerce.db"):
        self._conn = sqlite3.connect(name)
        self._cursor = self._conn.cursor()
        self._init()

    def _init(self):
        self._cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )""")

        self._cursor.execute("""
        CREATE TABLE IF NOT EXISTS produk(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            harga REAL,
            stok INTEGER
        )""")

        self._cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total REAL,
            status TEXT
        )""")

        self._cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi_item(
            transaksi_id INTEGER,
            produk_id INTEGER,
            qty INTEGER,
            harga REAL
        )""")
        
        self._cursor.execute("SELECT * FROM users WHERE role='admin'")
        if not self._cursor.fetchone():
            pw = hashlib.sha256("admin123".encode()).hexdigest()
            self._cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?,?,?)",
                ("admin", pw, "admin")
            )
        self._conn.commit()

    def execute(self, q, p=()):
        self._cursor.execute(q, p)
        self._conn.commit()

    def fetchone(self, q, p=()):
        self._cursor.execute(q, p)
        return self._cursor.fetchone()

    def fetchall(self, q, p=()):
        self._cursor.execute(q, p)
        return self._cursor.fetchall()


class UserRepository:
    def __init__(self, db: Database):
        self._db = db

    def save(self, username, password, role):
        self._db.execute(
            "INSERT INTO users(username,password,role) VALUES (?,?,?)",
            (username, password, role)
        )

    def findByUsername(self, username):
        return self._db.fetchone(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )


class ProdukRepository:
    def __init__(self, db: Database):
        self._db = db

    def findAll(self):
        return [Produk(*r) for r in self._db.fetchall("SELECT * FROM produk")]

    def findById(self, id):
        r = self._db.fetchone("SELECT * FROM produk WHERE id=?", (id,))
        return Produk(*r) if r else None

    def save(self, nama, harga, stok):
        self._db.execute(
            "INSERT INTO produk(nama,harga,stok) VALUES (?,?,?)",
            (nama, harga, stok)
        )

    def update(self, produk: Produk):
        self._db.execute(
            "UPDATE produk SET nama=?,harga=?,stok=? WHERE id=?",
            (produk.nama, produk.harga, produk.stok, produk.id)
        )

    def delete(self, id):
        self._db.execute("DELETE FROM produk WHERE id=?", (id,))


class TransaksiRepository:
    def __init__(self, db: Database):
        self._db = db

    def save(self, transaksi: Transaksi):
        self._db.execute(
            "INSERT INTO transaksi(user_id,total,status) VALUES (?,?,?)",
            (transaksi.user_id, transaksi.total, transaksi.status)
        )
        return self._db.fetchone("SELECT last_insert_rowid()")[0]

    def saveItem(self, transaksi_id, produk_id, qty, harga):
        self._db.execute(
            "INSERT INTO transaksi_item VALUES (?,?,?,?)",
            (transaksi_id, produk_id, qty, harga)
        )

    def findByUser(self, user_id):
        return self._db.fetchall(
            "SELECT * FROM transaksi WHERE user_id=?",
            (user_id,)
        )

    def findById(self, transaksi_id):
        trx = self._db.fetchone("SELECT * FROM transaksi WHERE id=?", (transaksi_id,))
        if not trx:
            raise TransaksiTidakDitemukanError(f"Transaksi ID {transaksi_id} tidak ditemukan")
        return trx

    def cancel(self, transaksi_id):
        trx = self.findById(transaksi_id)
        if trx[3] == "dibatalkan":
            raise TransaksiSudahDibatalkanError(f"Transaksi ID {transaksi_id} sudah dibatalkan")
        self._db.execute("UPDATE transaksi SET status='dibatalkan' WHERE id=?", (transaksi_id,))
