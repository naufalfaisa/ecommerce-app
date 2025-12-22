# Services/services.py
from abc import ABC, abstractmethod
import hashlib
from Exceptions.exceptions import LoginGagalError, ProdukTidakDitemukanError, StokTidakCukupError, UsernameSudahAdaError
from Models.models import Keranjang, Produk, Transaksi
from Repository.repository import ProdukRepository, TransaksiRepository, UserRepository


class AuthService:
    """
    Service yang menangani proses autentikasi:
    - Register user
    - Login user
    """
    def __init__(self, userRepo: UserRepository):
        self._userRepo = userRepo

    def register(self, username, password, role):
        """
        Mendaftarkan user baru.

        Alur:
        1. Cek apakah username sudah ada
        2. Hash password
        3. Simpan ke database
        """
        if self._userRepo.findByUsername(username):
            # Jika username sudah terdaftar
            raise UsernameSudahAdaError(
                f"Username '{username}' sudah ada"
            )
        # Password di-hash
        hashed = hashlib.sha256(password.encode()).hexdigest()

        # Simpan user baru
        self._userRepo.save(username, hashed, role)

    def login(self, username, password):
        """
        Proses login user.

        Alur:
        1. Cari user berdasarkan username
        2. Hash password input
        3. Cocokkan dengan password di database
        """
        user = self._userRepo.findByUsername(username)
        if not user:
            raise LoginGagalError("Username tidak ditemukan")
        
        hashed = hashlib.sha256(password.encode()).hexdigest()

        if user[2] != hashed:
            raise LoginGagalError("Password salah")
        
        return user


class ProdukService:
    """
    Service yang menangani logika bisnis produk.
    """
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
    """Abstract class untuk metode pembayaran."""

    @abstractmethod
    def bayar(self, total):    
        pass

class CreditCard(Payment):
    def bayar(self, total): 
        print(f"CreditCard Rp{total} OK")

class COD(Payment):
    def bayar(self, total): 
        print(f"COD Rp{total} dicatat")

class EWallet(Payment):
    def bayar(self, total): 
        print(f"EWallet Rp{total} OK")


class CheckoutService:
    """
    Service yang menangani proses checkout.
    """
    
    def __init__(self, trxRepo: TransaksiRepository, produkRepo: ProdukRepository):
        self._trxRepo = trxRepo
        self._produkRepo = produkRepo

    def checkout(self, user_id, keranjang: Keranjang, payment: Payment):
        """
        Proses checkout pelanggan.

        Alur:
        1. Ambil item dari keranjang
        2. Validasi produk ada
        3. Validasi stok cukup
        4. Hitung total harga
        5. Proses pembayaran
        6. Simpan transaksi
        7. Simpan detail transaksi
        8. Kurangi stok produk
        """        
        total = 0

        # 1–3: Validasi produk dan hitung total
        for pid, qty in keranjang.get_items().items():
            produk = self._produkRepo.findById(pid)
            if not produk:
                raise ProdukTidakDitemukanError(f"Produk dengan ID {pid} tidak ditemukan")
            if produk.stok < qty:
                raise StokTidakCukupError(f"Stok produk '{produk.nama}' tidak cukup")
            
            total += produk.harga * qty

        # 4: Proses pembayaran 
        payment.bayar(total)

        # 5: Simpan transaksi
        trx_id = self._trxRepo.save(
            Transaksi(None, user_id, total, "selesai")
        )

        # 6–7: Simpan detail transaksi & update stok
        for pid, qty in keranjang.get_items().items():
            produk = self._produkRepo.findById(pid)
            self._trxRepo.saveItem(trx_id, pid, qty, produk.harga)
            produk.kurangi_stok(qty)
            self._produkRepo.update(produk)

        return trx_id