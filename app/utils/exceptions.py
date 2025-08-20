# app/utils/exceptions.py
class AppException(Exception):
    """Exception de base de l'application"""
    def __init__(self, message, code=400):
        super().__init__(message)
        self.message = message
        self.code = code


class AuthenticationError(AppException):
    """Erreur d'authentification"""
    pass


class CurrencyError(AppException):
    """Erreur liée aux devises"""
    pass


class ValidationError(AppException):
    """Erreur de validation"""
    pass


class RateNotFoundError(CurrencyError):
    """Taux de change non trouvé"""
    pass


class ProviderError(CurrencyError):
    """Erreur du provider de taux"""
    pass
