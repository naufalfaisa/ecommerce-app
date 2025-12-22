import os

# Import custom exception untuk penanganan error
from Exceptions.exceptions import (
    LoginGagalError,
    ProdukTidakDitemukanError,
    StokTidakCukupError,
    UsernameSudahAdaError
)

# Import model Keranjang
from Models.models import Keranjang

# Import repository (untuk akses database)
from Repository.repository import (
    Database,
    ProdukRepository,
    TransaksiRepository,
    UserRepository
)

# Import service (untuk logika bisnis)
from Services.services import (
    COD,
    AuthService,
    CheckoutService,
    CreditCard,
    EWallet,
    ProdukService
)


# CLASS APLIKASI UTAMA (CLI)
class App:
    """
    Class utama aplikasi E-Commerce berbasis CLI.
    Mengatur alur program, menu, dan interaksi user.
    """

    def __init__(self):
        """
        Inisialisasi seluruh dependency aplikasi.
        """

        # Inisialisasi database
        self._db = Database()

        # Inisialisasi repository
        self._user_repo = UserRepository(self._db)
        self._produk_repo = ProdukRepository(self._db)
        self._trx_repo = TransaksiRepository(self._db)

        # Inisialisasi service (business logic)
        self._auth_service = AuthService(self._user_repo)
        self._produk_service = ProdukService(self._produk_repo)
        self._checkout_service = CheckoutService(
            self._trx_repo,
            self._produk_repo
        )

        # Keranjang belanja untuk pelanggan
        self._cart = Keranjang()

        # Menyimpan user yang sedang login
        self._current_user = None


    # MENU UTAMA APLIKASI
    def run(self):
        """
        Menjalankan aplikasi dan menampilkan menu utama.
        """
        while True:
            # Membersihkan layar (Windows / Linux / Mac)
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


    # LOGIN
    def _login(self, role):
        """
        Proses login admin atau pelanggan.
        """
        os.system("cls" if os.name == "nt" else "clear")
        print(f"=== LOGIN {role.upper()} ===")

        u = input("Username: ")
        p = input("Password: ")

        try:
            # Autentikasi user
            user = self._auth_service.login(u, p)

            # Validasi role
            if user[3] != role:
                raise LoginGagalError("Role tidak sesuai")

            # Simpan user yang sedang login
            self._current_user = user

            # Arahkan ke menu sesuai role
            if role == "admin":
                self._menu_admin()
            else:
                self._menu_pelanggan()

        except LoginGagalError as e:
            print(f"Login gagal: {e}")
            input("Enter...")


    # REGISTER PELANGGAN
    def _register_pelanggan(self):
        """
        Proses registrasi pelanggan baru.
        """
        os.system("cls" if os.name == "nt" else "clear")
        print("=== REGISTER PELANGGAN ===")

        u = input("Username: ")
        p = input("Password: ")

        # Validasi input kosong
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


    # MENU ADMIN
    def _menu_admin(self):
        """
        Menu khusus admin untuk mengelola produk.
        """
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
                # Menampilkan semua produk
                for pr in self._produk_repo.findAll():
                    print(pr.id, pr.nama, pr.harga, pr.stok)
                input("Enter...")

            elif p == "2":
                # Menambah produk baru
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
                # Update produk
                try:
                    pid = int(input("ID Produk: "))
                    produk = self._produk_repo.findById(pid)

                    if not produk:
                        raise ProdukTidakDitemukanError(
                            f"Produk ID {pid} tidak ditemukan"
                        )

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
                # Hapus produk
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


    # MENU PELANGGAN
    def _menu_pelanggan(self):
        """
        Menu khusus pelanggan.
        """
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
                # Menampilkan produk
                for pr in self._produk_repo.findAll():
                    print(pr.id, pr.nama, pr.harga, pr.stok)
                input("Enter...")

            elif p == "2":
                # Tambah produk ke keranjang
                try:
                    pid = int(input("ID Produk: "))
                    qty = int(input("Jumlah: "))

                    produk = self._produk_repo.findById(pid)
                    if not produk:
                        raise ProdukTidakDitemukanError(
                            f"Produk dengan ID {pid} tidak ditemukan"
                        )

                    self._cart.tambah(pid, qty)
                    print("Produk ditambahkan ke keranjang")

                except ValueError:
                    print("Input tidak valid")
                except ProdukTidakDitemukanError as e:
                    print(f"Gagal menambahkan ke keranjang: {e}")

                input("Enter...")

            elif p == "3":
                # Melihat isi keranjang
                items = self._cart.get_items()

                if not items:
                    print("Keranjang kosong")
                    input("Enter...")
                    continue

                for pid, qty in items.items():
                    produk = self._produk_repo.findById(pid)
                    if produk:
                        print(
                            f"{produk.nama} | "
                            f"Harga: {produk.harga} | "
                            f"Qty: {qty}"
                        )
                input("Enter...")

            elif p == "4":
                # Checkout
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
                    trx_id = self._checkout_service.checkout(
                        user_id,
                        self._cart,
                        metode
                    )
                    self._cart.kosongkan()
                    print("Checkout berhasil")
                    print("Detail transaksi:")

                    details = self._trx_repo.findDetailByTransaksi(trx_id)
                    total = 0

                    for nama, qty, harga, subtotal in details:
                        total += subtotal
                        print(
                            f"{nama} | "
                            f"Qty: {qty} | "
                            f"Harga: {harga} | "
                            f"Subtotal: {subtotal}"
                        )

                except ProdukTidakDitemukanError as e:
                    print(f"Checkout gagal: {e}")
                except StokTidakCukupError as e:
                    print(f"Checkout gagal: {e}")
                except Exception as e:
                    print(f"Checkout gagal: {e}")

                input("Enter...")

            elif p == "5":
                # Riwayat transaksi
                try:
                    transaksi = self._trx_repo.findByUser(user_id)
                    if not transaksi:
                        print("Belum ada transaksi")

                    for t in transaksi:
                        print(
                            f"ID: {t[0]}, "
                            f"Total: {t[2]}, "
                            f"Status: {t[3]}"
                        )
                except Exception as e:
                    print(f"Error: {e}")

                input("Enter...")

            elif p == "6":
                break


# ENTRY POINT PROGRAM
if __name__ == "__main__":
    App().run()
