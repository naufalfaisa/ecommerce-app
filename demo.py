# ecommerce_app.py
import sqlite3
import os
import hashlib
from abc import ABC, abstractmethod

# =========================
# EXCEPTIONS
# =========================
class EcommerceError(Exception): pass

class ProdukTidakDitemukanError(EcommerceError): pass
class StokTidakCukupError(EcommerceError): pass
class TransaksiTidakDitemukanError(EcommerceError): pass
class TransaksiSudahDibatalkanError(EcommerceError): pass


class Pelanggan:
    def __init__(self, id, username):
        self.id = id
        self.username = username

class Admin:
    def __init__(self, id, username):
        self.id = id
        self.username = username

class Produk:
    def __init__(self, id, nama, harga, stok):
        self._id = id
        self._nama = nama
        self._harga = harga
        self._stok = stok

    @property
    def id(self):
        return self._id

    @property
    def nama(self):
        return self._nama
    @nama.setter
    def nama(self, value):
        self._nama = value

    @property
    def harga(self):
        return self._harga
    @harga.setter
    def harga(self, value):
        self._harga = value

    @property
    def stok(self):
        return self._stok
    @stok.setter
    def stok(self, value):
        self._stok = value

    def kurangi_stok(self, qty):
        if qty > self._stok:
            raise StokTidakCukupError()
        self._stok -= qty

class Keranjang:
    def __init__(self):
        self._items = {}  # {produk_id: qty}

    def tambah(self, produk_id, qty):
        if qty <= 0:
            raise ValueError("Jumlah harus > 0")
        self._items[produk_id] = self._items.get(produk_id, 0) + qty

    def hapus(self, produk_id):
        self._items.pop(produk_id, None)

    def kosongkan(self):
        self._items.clear()

    def get_items(self):
        return self._items.copy()

class Transaksi:
    def __init__(self, id, user_id, total, status):
        self.id = id
        self.user_id = user_id
        self.total = total
        self.status = status
        
        
class Database:
    def __init__(self, name="ecommerce.db"):
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()
        self.init()

    def init(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS produk(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            harga REAL,
            stok INTEGER
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total REAL,
            status TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi_item(
            transaksi_id INTEGER,
            produk_id INTEGER,
            qty INTEGER,
            harga REAL
        )""")
        
        self.cursor.execute("SELECT * FROM users WHERE role='admin'")
        if not self.cursor.fetchone():
            pw = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?,?,?)",
                ("admin", pw, "admin")
            )
            
        self.conn.commit()

    def execute(self, q, p=()):
        self.cursor.execute(q, p)
        self.conn.commit()

    def fetchone(self, q, p=()):
        self.cursor.execute(q, p)
        return self.cursor.fetchone()

    def fetchall(self, q, p=()):
        self.cursor.execute(q, p)
        return self.cursor.fetchall()


class UserRepository:
    def __init__(self, db):
        self.db = db

    def save(self, username, password, role):
        self.db.execute(
            "INSERT INTO users(username,password,role) VALUES (?,?,?)",
            (username, password, role)
        )

    def findByUsername(self, username):
        return self.db.fetchone(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )


class ProdukRepository:
    def __init__(self, db):
        self.db = db

    def findAll(self):
        return [Produk(*r) for r in self.db.fetchall("SELECT * FROM produk")]

    def findById(self, id):
        r = self.db.fetchone("SELECT * FROM produk WHERE id=?", (id,))
        return Produk(*r) if r else None

    def save(self, nama, harga, stok):
        self.db.execute(
            "INSERT INTO produk(nama,harga,stok) VALUES (?,?,?)",
            (nama, harga, stok)
        )

    def update(self, produk: Produk):
        self.db.execute(
            "UPDATE produk SET nama=?,harga=?,stok=? WHERE id=?",
            (produk.nama, produk.harga, produk.stok, produk.id)
        )

    def delete(self, id):
        self.db.execute("DELETE FROM produk WHERE id=?", (id,))


class TransaksiRepository:
    def __init__(self, db):
        self.db = db

    def save(self, transaksi: Transaksi):
        self.db.execute(
            "INSERT INTO transaksi(user_id,total,status) VALUES (?,?,?)",
            (transaksi.user_id, transaksi.total, transaksi.status)
        )
        return self.db.fetchone("SELECT last_insert_rowid()")[0]

    def saveItem(self, transaksi_id, produk_id, qty, harga):
        self.db.execute(
            "INSERT INTO transaksi_item VALUES (?,?,?,?)",
            (transaksi_id, produk_id, qty, harga)
        )

    def findByUser(self, user_id):
        return self.db.fetchall(
            "SELECT * FROM transaksi WHERE user_id=?",
            (user_id,)
        )


class AuthService:
    def __init__(self, userRepo: UserRepository):
        self.userRepo = userRepo

    def register(self, username, password, role):
        if self.userRepo.findByUsername(username):
            raise Exception("Username sudah ada")
        hashed = hashlib.sha256(password.encode()).hexdigest()
        self.userRepo.save(username, hashed, role)

    def login(self, username, password):
        user = self.userRepo.findByUsername(username)
        if not user:
            return None
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return user if user[2] == hashed else None


class ProdukService:
    def __init__(self, repo: ProdukRepository):
        self.repo = repo

    def tambahProduk(self, nama, harga, stok):
        self.repo.save(nama, harga, stok)

    def updateProduk(self, produk: Produk):
        self.repo.update(produk)

    def hapusProduk(self, id):
        self.repo.delete(id)


class Payment(ABC):
    @abstractmethod
    def bayar(self, total): pass

class CreditCard(Payment):
    def bayar(self, total): print(f"CreditCard Rp{total} OK")

class COD(Payment):
    def bayar(self, total): print(f"COD Rp{total} dicatat")

class EWallet(Payment):
    def bayar(self, total): print(f"EWallet Rp{total} OK")


class CheckoutService:
    def __init__(self, trxRepo, produkRepo):
        self.trxRepo = trxRepo
        self.produkRepo = produkRepo

    def checkout(self, user_id, keranjang: Keranjang, payment: Payment):
        total = 0

        # hitung total & validasi stok
        for pid, qty in keranjang.get_items().items():
            produk = self.produkRepo.findById(pid)
            if not produk:
                raise ProdukTidakDitemukanError()
            if produk.stok < qty:
                raise StokTidakCukupError()
            total += produk.harga * qty

        # bayar (polymorphism)
        payment.bayar(total)

        # simpan transaksi
        trx_id = self.trxRepo.save(
            Transaksi(None, user_id, total, "selesai")
        )

        # simpan item & update stok
        for pid, qty in keranjang.get_items().items():
            produk = self.produkRepo.findById(pid)
            self.trxRepo.saveItem(trx_id, pid, qty, produk.harga)
            produk.stok -= qty
            self.produkRepo.update(produk)

# =========================
# CLI
# =========================
class App:
    def __init__(self):
        self.db = Database()

        # repository
        self.user_repo = UserRepository(self.db)
        self.produk_repo = ProdukRepository(self.db)
        self.trx_repo = TransaksiRepository(self.db)

        # service
        self.auth_service = AuthService(self.user_repo)
        self.produk_service = ProdukService(self.produk_repo)
        self.checkout_service = CheckoutService(self.trx_repo, self.produk_repo)

        self.cart = Keranjang()
        self.current_user = None   # (id, username, role)

    # =========================
    # ROOT MENU
    # =========================
    def run(self):
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print("=== E-COMMERCE CLI ===")
            print("1. Login Admin")
            print("2. Login Pelanggan")
            print("3. Register Pelanggan")
            print("4. Keluar")

            p = input("Pilih: ")

            if p == "1":
                self.login("admin")
            elif p == "2":
                self.login("pelanggan")
            elif p == "3":
                self.register_pelanggan()
            elif p == "4":
                break

    # =========================
    # AUTH
    # =========================
    def login(self, role):
        os.system("cls" if os.name == "nt" else "clear")
        print(f"=== LOGIN {role.upper()} ===")
        u = input("Username: ")
        p = input("Password: ")

        user = self.auth_service.login(u, p)
        if not user or user[3] != role:
            print("Login gagal / role salah")
            input("Enter...")
            return

        self.current_user = user

        if role == "admin":
            self.menu_admin()
        else:
            self.menu_pelanggan()

    def register_pelanggan(self):
        os.system("cls" if os.name == "nt" else "clear")
        print("=== REGISTER PELANGGAN ===")
        u = input("Username: ")
        p = input("Password: ")

        try:
            self.auth_service.register(u, p, "pelanggan")
            print("Registrasi berhasil")
        except Exception as e:
            print(e)

        input("Enter...")

    # =========================
    # MENU ADMIN
    # =========================
    def menu_admin(self):
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print("=== MENU ADMIN ===")
            print("1. Lihat Produk")
            print("2. Tambah Produk")
            print("3. Update Produk")
            print("4. Hapus Produk")
            print("5. Logout")

            p = input("Pilih: ")

            if p == "1":
                for pr in self.produk_repo.findAll():
                    print(pr.id, pr.nama, pr.harga, pr.stok)
                input("Enter...")

            elif p == "2":
                self.produk_service.tambahProduk(
                    input("Nama: "),
                    float(input("Harga: ")),
                    int(input("Stok: "))
                )

            elif p == "3":
                pr = self.produk_repo.findById(int(input("ID Produk: ")))
                if pr:
                    pr.nama = input("Nama: ")
                    pr.harga = float(input("Harga: "))
                    pr.stok = int(input("Stok: "))
                    self.produk_service.updateProduk(pr)

            elif p == "4":
                self.produk_service.hapusProduk(int(input("ID Produk: ")))

            elif p == "5":
                break

    # =========================
    # MENU PELANGGAN
    # =========================
    def menu_pelanggan(self):
        user_id = self.current_user[0]

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print("=== MENU PELANGGAN ===")
            print("1. Lihat Produk")
            print("2. Tambah ke Keranjang")
            print("3. Lihat Keranjang")
            print("4. Checkout")
            print("5. Riwayat Transaksi")
            print("6. Logout")

            p = input("Pilih: ")

            if p == "1":
                for pr in self.produk_repo.findAll():
                    print(pr.id, pr.nama, pr.harga, pr.stok)
                input("Enter...")

            elif p == "2":
                self.cart.tambah(
                    int(input("ID Produk: ")),
                    int(input("Jumlah: "))
                )

            elif p == "3":
                items = self.cart.get_items()
                if not items:
                    print("Keranjang kosong")
                    input("Enter...")
                    continue
                for pid, qty in items.items():
                    produk = self.produk_repo.findById(pid)
                    if produk:
                        print(f"{produk.nama} | Harga: {produk.harga} | Qty: {qty}")
                input("Enter...")

            elif p == "4":
                if not self.cart.get_items():
                    print("Keranjang masih kosong")
                    input("Enter...")
                    continue
                os.system("cls" if os.name == "nt" else "clear")
                print("=== PILIH METODE PEMBAYARAN ===")
                print("1. Credit Card")
                print("2. COD")
                print("3. E-Wallet")
                metode = {
                    "1": CreditCard(),
                    "2": COD(),
                    "3": EWallet()
                }.get(input("Pilih: "))
                if not metode:
                    print("Metode tidak valid")
                    input("Enter...")
                    continue
                try:
                    self.checkout_service.checkout(
                        user_id,
                        self.cart,
                        metode
                    )
                    self.cart.kosongkan()
                    print("Checkout berhasil")
                except Exception as e:
                    print(e)
                input("Enter...")

            elif p == "5":
                for t in self.trx_repo.findByUser(user_id):
                    print(t)
                input("Enter...")

            elif p == "6":
                break


if __name__ == "__main__":
    App().run()