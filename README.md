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

## Struktur Kode

- `Pelanggan` & `Admin`: model untuk pengguna.
- `Produk`: model produk dengan properti `nama`, `harga`, dan `stok`.
- `Keranjang`: menyimpan produk yang ditambahkan pelanggan.
- `Transaksi`: menyimpan data transaksi.
- `Database`: abstraksi untuk SQLite.
- Repository:
   - `UserRepository`: mengelola data pengguna.
   - `ProdukRepository`: mengelola data produk.
   - `TransaksiRepository`: mengelola data transaksi.
- Service:
   - `AuthService`: registrasi & login.
   - `ProdukService`: tambah, update, hapus produk.
   - `CheckoutService`: proses checkout & pembayaran.
- Payment (polimorfisme):
   - `CreditCard`, `COD`, `EWallet`.
- `App`: CLI untuk interaksi pengguna.


