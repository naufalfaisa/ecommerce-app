import sqlite3
import os
import hashlib
from abc import ABC, abstractmethod

class EcommerceError(Exception): pass

class ProdukTidakDitemukanError(EcommerceError): pass
class StokTidakCukupError(EcommerceError): pass

class TransaksiTidakDitemukanError(EcommerceError): pass
class TransaksiSudahDibatalkanError(EcommerceError): pass

class AuthError(EcommerceError): pass
class UsernameSudahAdaError(AuthError): pass
class LoginGagalError(AuthError): pass


class User:
    def __init__(self, id, username):
        self._id = id
        self._username = username

    @property
    def id(self):
        return self._id

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if not value:
            raise ValueError("Username tidak boleh kosong")
        self._username = value


class Pelanggan(User):
    pass


class Admin(User):
    pass


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
        if not value:
            raise ValueError("Nama produk tidak boleh kosong")
        self._nama = value

    @property
    def harga(self):
        return self._harga
    @harga.setter
    def harga(self, value):
        if value < 0:
            raise ValueError("Harga tidak boleh negatif")
        self._harga = value

    @property
    def stok(self):
        return self._stok
    @stok.setter
    def stok(self, value):
        if value < 0:
            raise ValueError("Stok tidak boleh negatif")
        self._stok = value

    def kurangi_stok(self, qty):
        if qty > self._stok:
            raise StokTidakCukupError(f"Stok produk '{self.nama}' tidak cukup")
        self._stok -= qty


class Keranjang:
    def __init__(self):
        self._items = {}

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
        self._id = id
        self._user_id = user_id
        self._total = total
        self._status = status

    @property
    def id(self):
        return self._id

    @property
    def user_id(self):
        return self._user_id

    @property
    def total(self):
        return self._total
    @total.setter
    def total(self, value):
        if value < 0:
            raise ValueError("Total tidak boleh negatif")
        self._total = value

    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        if not value:
            raise ValueError("Status tidak boleh kosong")
        self._status = value


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


class AuthService:
    def __init__(self, userRepo: UserRepository):
        self._userRepo = userRepo

    def register(self, username, password, role):
        if self._userRepo.findByUsername(username):
            raise UsernameSudahAdaError(f"Username '{username}' sudah ada")
        hashed = hashlib.sha256(password.encode()).hexdigest()
        self._userRepo.save(username, hashed, role)

    def login(self, username, password):
        user = self._userRepo.findByUsername(username)
        if not user:
            raise LoginGagalError("Username tidak ditemukan")
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if user[2] != hashed:
            raise LoginGagalError("Password salah")
        return user


class ProdukService:
    def __init__(self, repo: ProdukRepository):
        self._repo = repo

    def tambahProduk(self, nama, harga, stok):
        self._repo.save(nama, harga, stok)

    def updateProduk(self, produk: Produk):
        if not self._repo.findById(produk.id):
            raise ProdukTidakDitemukanError(f"Produk ID {produk.id} tidak ditemukan")
        self._repo.update(produk)

    def hapusProduk(self, id):
        if not self._repo.findById(id):
            raise ProdukTidakDitemukanError(f"Produk ID {id} tidak ditemukan")
        self._repo.delete(id)


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
    def __init__(self, trxRepo: TransaksiRepository, produkRepo: ProdukRepository):
        self._trxRepo = trxRepo
        self._produkRepo = produkRepo

    def checkout(self, user_id, keranjang: Keranjang, payment: Payment):
        total = 0
        for pid, qty in keranjang.get_items().items():
            produk = self._produkRepo.findById(pid)
            if not produk:
                raise ProdukTidakDitemukanError(f"Produk dengan ID {pid} tidak ditemukan")
            if produk.stok < qty:
                raise StokTidakCukupError(f"Stok produk '{produk.nama}' tidak cukup")
            total += produk.harga * qty

        payment.bayar(total)

        trx_id = self._trxRepo.save(
            Transaksi(None, user_id, total, "selesai")
        )

        for pid, qty in keranjang.get_items().items():
            produk = self._produkRepo.findById(pid)
            self._trxRepo.saveItem(trx_id, pid, qty, produk.harga)
            produk.kurangi_stok(qty)
            self._produkRepo.update(produk)

class App:
    def __init__(self):
        self._db = Database()

        self._user_repo = UserRepository(self._db)
        self._produk_repo = ProdukRepository(self._db)
        self._trx_repo = TransaksiRepository(self._db)

        self._auth_service = AuthService(self._user_repo)
        self._produk_service = ProdukService(self._produk_repo)
        self._checkout_service = CheckoutService(self._trx_repo, self._produk_repo)

        self._cart = Keranjang()
        self._current_user = None

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
                self._login("admin")
            elif p == "2":
                self._login("pelanggan")
            elif p == "3":
                self._register_pelanggan()
            elif p == "4":
                break

    def _login(self, role):
        os.system("cls" if os.name == "nt" else "clear")
        print(f"=== LOGIN {role.upper()} ===")
        u = input("Username: ")
        p = input("Password: ")
        try:
            user = self._auth_service.login(u, p)
            if user[3] != role:
                raise LoginGagalError("Role tidak sesuai")
            self._current_user = user
            if role == "admin":
                self._menu_admin()
            else:
                self._menu_pelanggan()
        except LoginGagalError as e:
            print(f"Login gagal: {e}")
            input("Enter...")

    def _register_pelanggan(self):
        os.system("cls" if os.name == "nt" else "clear")
        print("=== REGISTER PELANGGAN ===")
        u = input("Username: ")
        p = input("Password: ")
        if not u or not p:
            print("Username dan Password tidak boleh kosong")
            input("Enter...")
            return
        try:
            self._auth_service.register(u, p, "pelanggan")
            print("Registrasi berhasil")
        except UsernameSudahAdaError as e:
            print(f"Registrasi gagal: {e}")
        input("Enter...")

    def _menu_admin(self):
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
                for pr in self._produk_repo.findAll():
                    print(pr.id, pr.nama, pr.harga, pr.stok)
                input("Enter...")
            elif p == "2":
                try:
                    self._produk_service.tambahProduk(
                        input("Nama: "),
                        float(input("Harga: ")),
                        int(input("Stok: "))
                    )
                    print("Produk berhasil ditambah")
                except ValueError:
                    print("Input tidak valid")
                input("Enter...")
            elif p == "3":
                try:
                    pid = int(input("ID Produk: "))
                    produk = self._produk_repo.findById(pid)
                    if not produk:
                        raise ProdukTidakDitemukanError(f"Produk ID {pid} tidak ditemukan")
                    produk.nama = input("Nama: ")
                    produk.harga = float(input("Harga: "))
                    produk.stok = int(input("Stok: "))
                    self._produk_service.updateProduk(produk)
                    print("Produk berhasil diupdate")
                except ProdukTidakDitemukanError as e:
                    print(e)
                except ValueError:
                    print("Input tidak valid")
                input("Enter...")
            elif p == "4":
                try:
                    pid = int(input("ID Produk: "))
                    self._produk_service.hapusProduk(pid)
                    print("Produk berhasil dihapus")
                except ProdukTidakDitemukanError as e:
                    print(e)
                except ValueError:
                    print("Input tidak valid")
                input("Enter...")
            elif p == "5":
                break

    def _menu_pelanggan(self):
        user_id = self._current_user[0]
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
                for pr in self._produk_repo.findAll():
                    print(pr.id, pr.nama, pr.harga, pr.stok)
                input("Enter...")
            elif p == "2":
                try:
                    pid = int(input("ID Produk: "))
                    qty = int(input("Jumlah: "))
                    produk = self._produk_repo.findById(pid)
                    if not produk:
                        raise ProdukTidakDitemukanError(f"Produk dengan ID {pid} tidak ditemukan")
                    self._cart.tambah(pid, qty)
                    print("Produk ditambahkan ke keranjang")
                except ValueError:
                    print("Input tidak valid")
                except ProdukTidakDitemukanError as e:
                    print(f"Gagal menambahkan ke keranjang: {e}")
                input("Enter...")
            elif p == "3":
                items = self._cart.get_items()
                if not items:
                    print("Keranjang kosong")
                    input("Enter...")
                    continue
                for pid, qty in items.items():
                    produk = self._produk_repo.findById(pid)
                    if produk:
                        print(f"{produk.nama} | Harga: {produk.harga} | Qty: {qty}")
                input("Enter...")
            elif p == "4":
                if not self._cart.get_items():
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
                    self._checkout_service.checkout(
                        user_id,
                        self._cart,
                        metode
                    )
                    self._cart.kosongkan()
                    print("Checkout berhasil")
                except ProdukTidakDitemukanError as e:
                    print(f"Checkout gagal: {e}")
                except StokTidakCukupError as e:
                    print(f"Checkout gagal: {e}")
                except Exception as e:
                    print(f"Checkout gagal: {e}")
                input("Enter...")
            elif p == "5":
                try:
                    transaksis = self._trx_repo.findByUser(user_id)
                    if not transaksis:
                        print("Belum ada transaksi")
                    for t in transaksis:
                        print(f"ID: {t[0]}, Total: {t[2]}, Status: {t[3]}")
                except Exception as e:
                    print(f"Error: {e}")
                input("Enter...")
            elif p == "6":
                break


if __name__ == "__main__":
    App().run()
