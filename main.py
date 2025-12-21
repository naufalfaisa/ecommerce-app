import os
from Exceptions.exceptions import LoginGagalError, ProdukTidakDitemukanError, StokTidakCukupError, UsernameSudahAdaError
from Models.models import Keranjang
from Repository.repository import Database, ProdukRepository, TransaksiRepository, UserRepository
from Services.services import COD, AuthService, CheckoutService, CreditCard, EWallet, ProdukService


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