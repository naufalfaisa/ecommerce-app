class EcommerceError(Exception): 
    pass
class ProdukTidakDitemukanError(EcommerceError): 
    pass
class StokTidakCukupError(EcommerceError): 
    pass
class TransaksiTidakDitemukanError(EcommerceError): 
    pass
class TransaksiSudahDibatalkanError(EcommerceError): 
    pass
class AuthError(EcommerceError): 
    pass
class UsernameSudahAdaError(AuthError): 
    pass
class LoginGagalError(AuthError): 
    pass
