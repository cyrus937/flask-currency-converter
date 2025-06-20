# app/providers/base_provider.py
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BaseProvider(ABC):
    """Classe de base pour les providers de taux de change"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = ""
        self.name = ""
        self.rate_limit = 1000  # requêtes par mois par défaut
        self.timeout = 10  # secondes
        
        # Configuration des retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    @abstractmethod
    def fetch_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Récupère un taux de change spécifique"""
        pass
    
    @abstractmethod
    def fetch_rates(self, base_currency: str = 'USD') -> Dict[str, Decimal]:
        """Récupère tous les taux pour une devise de base"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Vérifie si le provider est disponible"""
        pass
    
    def get_supported_currencies(self) -> List[str]:
        """Retourne la liste des devises supportées"""
        return []
    
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Effectue une requête HTTP avec gestion d'erreurs"""
        try:
            response = self.session.get(
                url, 
                params=params or {}, 
                timeout=self.timeout
            )
            self._handle_response_errors(response)
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception(f"Timeout lors de la requête vers {self.name}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Erreur de connexion vers {self.name}")
        except Exception as e:
            raise Exception(f"Erreur {self.name}: {str(e)}")
    
    def _handle_response_errors(self, response: requests.Response) -> None:
        """Gère les erreurs de réponse HTTP"""
        if response.status_code == 200:
            return
        
        error_messages = {
            400: "Requête invalide",
            401: "Clé API invalide ou manquante",
            403: "Accès refusé",
            404: "Endpoint non trouvé",
            429: "Limite de taux dépassée",
            500: "Erreur serveur interne",
            503: "Service temporairement indisponible"
        }
        
        message = error_messages.get(
            response.status_code, 
            f"Erreur HTTP {response.status_code}"
        )
        
        raise Exception(f"{self.name}: {message}")
    
    def _convert_to_decimal(self, value) -> Decimal:
        """Convertit une valeur en Decimal avec validation"""
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            raise Exception(f"Valeur de taux invalide: {value}")
