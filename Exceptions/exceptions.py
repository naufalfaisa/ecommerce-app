# Exceptions/exceptions.py

# Semua error khusus aplikasi e-commerce dikelompokkan di file ini
# Tujuannya agar error lebih terstruktur dan mudah ditangani

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
