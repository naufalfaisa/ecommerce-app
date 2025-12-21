
from Exceptions.exceptions import StokTidakCukupError


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