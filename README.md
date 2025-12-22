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


Penerapan OOP

1. Exceptions/exceptions.py
class EcommerceError(Exception): 
    pass
class ProdukTidakDitemukanError(EcommerceError): 
    pass
class StokTidakCukupError(EcommerceError): 
    pass
class TransaksiTidakDitemukanError(EcommerceError): 
    pass
class AuthError(EcommerceError): 
    pass
class UsernameSudahAdaError(AuthError): 
    pass
class LoginGagalError(AuthError): 
    pass


Pilar OOP yang diterapkan:

Inheritance (Pewarisan)

Semua error mewarisi EcommerceError, yang memudahkan penanganan exception secara generik.

Contoh: UsernameSudahAdaError mewarisi AuthError → memudahkan identifikasi kesalahan autentikasi.

Alasan:

Mempermudah penanganan kesalahan secara hirarkis dan meningkatkan reusability kode error handling.

2. Models/models.py
Class User dan Subclass
class User:
    ...
class Pelanggan(User):
    pass
class Admin(User):
    pass


Pilar OOP:

Encapsulation (Enkapsulasi)

Atribut _id dan _username bersifat private dengan property getter/setter.

Setter memvalidasi data (misal username tidak boleh kosong).

Inheritance (Pewarisan)

Pelanggan dan Admin mewarisi User.

Tidak perlu mendefinisikan ulang atribut atau method.

Class Produk
class Produk:
    ...
    def kurangi_stok(self, qty):
        if qty > self._stok:
            raise StokTidakCukupError(...)
        self._stok -= qty


Pilar OOP:

Encapsulation

Atribut _nama, _harga, _stok dibungkus dengan getter/setter.

Setter memvalidasi input (harga ≥ 0, stok ≥ 0).

Abstraction (Abstraksi)

Method kurangi_stok menyembunyikan detail pengurangan stok dari pengguna kelas.

Class Keranjang
class Keranjang:
    ...


Pilar OOP:

Encapsulation

_items disembunyikan, akses hanya melalui method (tambah, hapus, kosongkan).

Abstraction

Pengguna kelas tidak perlu tahu struktur internal dictionary _items.

Class Transaksi
class Transaksi:
    ...


Pilar OOP:

Encapsulation

Atribut _id, _user_id, _total, _status dibungkus getter/setter.

Validasi data dilakukan melalui setter.

3. Repository/repository.py
Class Database
class Database:
    ...


Pilar OOP:

Encapsulation

_conn dan _cursor disembunyikan, hanya method tertentu yang mengakses database.

Abstraction

Pengguna Database tidak perlu tahu SQL detail, cukup gunakan execute, fetchone, fetchall.

Class UserRepository, ProdukRepository, TransaksiRepository
class UserRepository:
    ...
class ProdukRepository:
    ...
class TransaksiRepository:
    ...


Pilar OOP:

Encapsulation & Abstraction

Semua operasi CRUD dibungkus dalam method repository.

Pengguna repository tidak perlu tahu detail SQL.

Reusability

Method save, findById, dll. bisa digunakan berulang.

4. Services/services.py
AuthService
class AuthService:
    ...


Pilar OOP:

Encapsulation & Abstraction

Mengelola logika autentikasi tanpa pengguna tahu detail database.

Reusability

Method register dan login bisa dipanggil dari berbagai tempat.

ProdukService
class ProdukService:
    ...


Pilar OOP:

Abstraction & Encapsulation

Mengatur logika validasi produk (update, hapus) sebelum operasi database.

Polymorphism dengan Payment
class Payment(ABC):
    @abstractmethod
    def bayar(self, total): pass

class CreditCard(Payment):
    def bayar(self, total): print(...)

class COD(Payment):
    def bayar(self, total): print(...)

class EWallet(Payment):
    def bayar(self, total): print(...)


Pilar OOP:

Polymorphism (Polimorfisme)

Semua kelas pembayaran bisa dipanggil melalui interface Payment.

Contoh: checkout(payment) tidak peduli apakah payment tipe CreditCard, COD, atau EWallet.

Abstraction

Menggunakan abstract class Payment menyembunyikan implementasi detail masing-masing metode bayar.

CheckoutService
class CheckoutService:
    def checkout(self, user_id, keranjang: Keranjang, payment: Payment):
        ...


Pilar OOP:

Abstraction & Encapsulation

Mengelola proses checkout, validasi stok, dan pembayaran tanpa pengguna tahu detail implementasi.

Polymorphism

payment.bayar(total) bersifat polymorphic → bisa diganti metode pembayaran lain.

5. main.py / Class App

Pilar OOP:

Encapsulation

State aplikasi (_current_user, _cart) disembunyikan.

Akses hanya melalui method internal (_login, _menu_admin, dll).

Reusability & Abstraction

Method internal menangani flow menu tanpa pengguna perlu tahu detail service/repository.