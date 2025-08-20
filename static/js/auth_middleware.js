// static/js/auth-middleware.js
/**
 * Middleware d'authentification pour gérer automatiquement les tokens JWT
 * Gère le refresh automatique des tokens et les redirections
 */

class AuthMiddleware {
    constructor() {
        this.refreshing = false;
        this.failedQueue = [];
        this.setupAxiosInterceptors();
        this.setupTokenRefresh();
    }

    /**
     * Configure les intercepteurs Axios pour gérer automatiquement les tokens
     */
    setupAxiosInterceptors() {
        // Intercepteur de requête - ajouter le token d'accès
        axios.interceptors.request.use(
            (config) => {
                const token = this.getAccessToken();
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        // Intercepteur de réponse - gérer les tokens expirés
        axios.interceptors.response.use(
            (response) => response,
            async (error) => {
                const originalRequest = error.config;

                // Si le token est expiré (401) et qu'on n'a pas déjà essayé de le renouveler
                if (error.response?.status === 401 && !originalRequest._retry) {
                    if (this.refreshing) {
                        // Si un refresh est déjà en cours, mettre la requête en file d'attente
                        return new Promise((resolve, reject) => {
                            this.failedQueue.push({ resolve, reject });
                        }).then(token => {
                            originalRequest.headers.Authorization = `Bearer ${token}`;
                            return axios(originalRequest);
                        }).catch(err => {
                            return Promise.reject(err);
                        });
                    }

                    originalRequest._retry = true;
                    this.refreshing = true;

                    try {
                        const newToken = await this.refreshAccessToken();
                        this.processQueue(null, newToken);
                        originalRequest.headers.Authorization = `Bearer ${newToken}`;
                        return axios(originalRequest);
                    } catch (refreshError) {
                        this.processQueue(refreshError, null);
                        this.handleAuthenticationFailure();
                        return Promise.reject(refreshError);
                    } finally {
                        this.refreshing = false;
                    }
                }

                return Promise.reject(error);
            }
        );
    }

    /**
     * Traite la file d'attente des requêtes en échec
     */
    processQueue(error, token = null) {
        this.failedQueue.forEach(({ resolve, reject }) => {
            if (error) {
                reject(error);
            } else {
                resolve(token);
            }
        });
        
        this.failedQueue = [];
    }

    /**
     * Récupère le token d'accès depuis le localStorage
     */
    getAccessToken() {
        return localStorage.getItem('access_token');
    }

    /**
     * Récupère le refresh token depuis le localStorage
     */
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }

    /**
     * Stocke les tokens dans le localStorage
     */
    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
    }

    /**
     * Supprime tous les tokens du localStorage
     */
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_email');
    }

    /**
     * Renouvelle le token d'accès en utilisant le refresh token
     */
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        
        if (!refreshToken) {
            throw new Error('Aucun refresh token disponible');
        }

        try {
            const response = await axios.post('/api/auth/refresh', {}, {
                headers: {
                    'Authorization': `Bearer ${refreshToken}`
                }
            });

            const { access_token } = response.data;
            this.setTokens(access_token);
            
            return access_token;
        } catch (error) {
            // Le refresh token est probablement expiré
            this.clearTokens();
            throw error;
        }
    }

    /**
     * Gère l'échec de l'authentification
     */
    handleAuthenticationFailure() {
        this.clearTokens();
        
        // Rediriger vers la page de login si on n'y est pas déjà
        if (!window.location.pathname.includes('/login')) {
            // Sauvegarder l'URL actuelle pour redirection après login
            localStorage.setItem('redirect_after_login', window.location.pathname);
            window.location.href = '/login';
        }
    }

    /**
     * Vérifie si l'utilisateur est connecté
     */
    isAuthenticated() {
        return !!this.getAccessToken();
    }

    /**
     * Configure le refresh automatique des tokens
     */
    setupTokenRefresh() {
        // Vérifier et renouveler le token toutes les 25 minutes (token expire après 30 min)
        setInterval(async () => {
            if (this.isAuthenticated()) {
                try {
                    await this.refreshAccessToken();
                    console.log('Token renouvelé automatiquement');
                } catch (error) {
                    console.log('Échec du renouvellement automatique du token');
                    this.handleAuthenticationFailure();
                }
            }
        }, 25 * 60 * 1000); // 25 minutes
    }

    /**
     * Décode un JWT token (sans vérification de signature)
     */
    decodeToken(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));

            return JSON.parse(jsonPayload);
        } catch (error) {
            return null;
        }
    }

    /**
     * Vérifie si un token est expiré
     */
    isTokenExpired(token) {
        const decoded = this.decodeToken(token);
        if (!decoded || !decoded.exp) {
            return true;
        }

        const currentTime = Date.now() / 1000;
        return decoded.exp < currentTime;
    }

    /**
     * Récupère les informations utilisateur depuis le token
     */
    getUserFromToken() {
        const token = this.getAccessToken();
        if (!token) {
            return null;
        }

        const decoded = this.decodeToken(token);
        return decoded ? {
            id: decoded.sub,
            email: decoded.email,
            is_premium: decoded.is_premium
        } : null;
    }

    /**
     * Effectue une déconnexion complète
     */
    async logout() {
        try {
            // Appeler l'endpoint de déconnexion
            await axios.post('/api/auth/logout');
        } catch (error) {
            // Continuer même si l'appel API échoue
            console.error('Erreur lors de la déconnexion:', error);
        } finally {
            this.clearTokens();
            window.location.href = '/login';
        }
    }

    /**
     * Protège une page en vérifiant l'authentification
     */
    protectPage() {
        if (!this.isAuthenticated()) {
            this.handleAuthenticationFailure();
            return false;
        }

        // Vérifier si le token n'est pas expiré
        const token = this.getAccessToken();
        if (this.isTokenExpired(token)) {
            this.refreshAccessToken().catch(() => {
                this.handleAuthenticationFailure();
            });
        }

        return true;
    }

    /**
     * Redirige vers la page sauvegardée après login
     */
    redirectAfterLogin() {
        const redirectUrl = localStorage.getItem('redirect_after_login');
        localStorage.removeItem('redirect_after_login');
        
        if (redirectUrl && redirectUrl !== '/login') {
            window.location.href = redirectUrl;
        } else {
            window.location.href = '/dashboard/';
        }
    }
}

// Initialiser le middleware d'authentification
const authMiddleware = new AuthMiddleware();

// Rendre le middleware disponible globalement
window.authMiddleware = authMiddleware;

// Fonctions utilitaires globales
window.logout = () => authMiddleware.logout();
window.isAuthenticated = () => authMiddleware.isAuthenticated();
window.protectPage = () => authMiddleware.protectPage();

// Auto-initialisation pour les pages protégées
document.addEventListener('DOMContentLoaded', function() {
    // Protéger automatiquement les pages du dashboard
    if (window.location.pathname.startsWith('/dashboard/')) {
        authMiddleware.protectPage();
    }
    
    // Rediriger automatiquement si déjà connecté sur les pages d'auth
    if (window.location.pathname === '/login' || window.location.pathname === '/register') {
        if (authMiddleware.isAuthenticated()) {
            authMiddleware.redirectAfterLogin();
        }
    }
});

console.log('Auth Middleware initialisé');