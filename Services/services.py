
from abc import ABC, abstractmethod
import hashlib
from Exceptions.exceptions import LoginGagalError, ProdukTidakDitemukanError, StokTidakCukupError, UsernameSudahAdaError
from Models.models import Keranjang, Produk, Transaksi
from Repository.repository import ProdukRepository, TransaksiRepository, UserRepository


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