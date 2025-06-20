# app/utils/decorators.py
from functools import wraps
import time
from flask import current_app
from app.extensions import cache


def cache_result(timeout=300, key_prefix=None):
    """Décorateur pour mettre en cache le résultat d'une fonction"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Générer une clé de cache
            cache_key = key_prefix or f.__name__
            if args or kwargs:
                cache_key += f":{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Essayer de récupérer depuis le cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Exécuter la fonction et mettre en cache
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            return result
        return decorated
    return decorator


def log_execution_time(f):
    """Décorateur pour logger le temps d'exécution"""
    @wraps(f)
    def decorated(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        execution_time = time.time() - start_time
        
        current_app.logger.info(f"{f.__name__} executed in {execution_time:.3f}s")
        return result
    return decorated
