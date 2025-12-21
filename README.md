# E-Commerce App

Sebuah aplikasi e-commerce berbasis Command Line Interface (CLI) menggunakan Python dan SQLite. Aplikasi ini mendukung manajemen produk, keranjang belanja, checkout, dan autentikasi pengguna (admin & pelanggan).

## Fitur

### Admin

- Login sebagai admin.
- Melihat daftar produk.
- Menambahkan produk baru.
- Mengupdate produk.
- Menghapus produk.

### Pelanggan

- Registrasi akun pelanggan.
- Login sebagai pelanggan.
- Melihat daftar produk.
- Menambahkan produk ke keranjang.
- Melihat isi keranjang.
- Checkout dengan metode pembayaran:
   - Credit Card
   - Cash on Delivery (COD)
   - E-Wallet
- Melihat riwayat transaksi.

## Struktur Folder dan Kode

```
.
├── Exceptions
│   └── exceptions.py        # Semua custom exception aplikasi
├── Models
│   └── models.py            # Model untuk Produk, Pelanggan, Admin, Keranjang, Transaksi
├── Repository
│   └── repository.py        # Mengelola operasi database (CRUD) untuk user, produk, dan transaksi
├── Services
│   └── services.py          # Logika bisnis: AuthService, ProdukService, CheckoutService
├── main.py                  # Entry point aplikasi CLI
└── README.md
```

## Penjelasan Modul

- Exceptions: Semua custom exception untuk error handling, misal `ProdukTidakDitemukanError`, `StokTidakCukupError`.
- Models: Mewakili entitas utama aplikasi: `Produk`, `Pelanggan`, `Admin`, `Keranjang`, dan `Transaksi`.
- Repository: Abstraksi database untuk operasi CRUD.
   - `UserRepository`: mengelola data pengguna.
   - `ProdukRepository`: mengelola data produk.
   - `TransaksiRepository`: mengelola data transaksi.
- Services: Berisi logika bisnis.
   - `AuthService`: registrasi & login pengguna.
   - `ProdukService`: tambah, update, hapus produk.
   - `CheckoutService`: proses checkout & pembayaran (Credit Card, COD, E-Wallet).
- main.py: CLI untuk interaksi pengguna.

## Pola dan Prinsip OOP

- Encapsulation: Data model disimpan dalam class (`Produk`, `Pelanggan`) dan diakses melalui method.
- Abstraction: `Repository` dan `Service` menyembunyikan kompleksitas database dan logika bisnis.
- Inheritance: `Admin` dan `Pelanggan` mewarisi `User` (shared properties & methods).
- Polymorphism: Sistem pembayaran mendukung metode berbeda (`CreditCard`, `COD`, `EWallet`) melalui interface yang sama.
