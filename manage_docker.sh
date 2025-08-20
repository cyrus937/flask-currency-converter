#!/bin/bash
# manage_db.sh - Script pour gérer les migrations Flask

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier que Docker Compose est disponible
check_docker() {
    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    if ! docker compose ps &> /dev/null; then
        print_warning "Aucun service Docker Compose détecté"
    fi
}

# Démarrer les services de base de données
start_db() {
    print_info "Démarrage de PostgreSQL et Redis..."
    docker compose up -d db redis
    
    print_info "Attente que la base de données soit prête..."
    sleep 5
    
    # Vérifier que la base est accessible
    until docker compose exec db pg_isready -U postgres; do
        print_info "En attente de PostgreSQL..."
        sleep 2
    done
    
    print_success "Base de données prête!"
}

# Initialiser le système de migrations (première fois seulement)
init_migrations() {
    if [ -d "migrations" ]; then
        print_warning "Le dossier migrations/ existe déjà"
        read -p "Voulez-vous le supprimer et réinitialiser ? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf migrations/
            print_info "Dossier migrations supprimé"
        else
            print_info "Annulation de l'initialisation"
            return
        fi
    fi
    
    print_info "Initialisation du système de migrations..."
    docker compose run --rm web flask db init
    print_success "Système de migrations initialisé"
}

# Créer une nouvelle migration
create_migration() {
    local message="$1"
    if [ -z "$message" ]; then
        read -p "Description de la migration: " message
    fi
    
    if [ -z "$message" ]; then
        print_error "Description de migration requise"
        exit 1
    fi
    
    print_info "Création de la migration: $message"
    docker compose run --rm web flask db migrate -m "$message"
    print_success "Migration créée"
}

# Appliquer les migrations
upgrade_db() {
    print_info "Application des migrations..."
    docker compose run --rm web flask db upgrade
    print_success "Migrations appliquées"
}

# Voir l'état des migrations
status_migrations() {
    print_info "État actuel des migrations:"
    echo "=== Migration actuelle ==="
    docker compose run --rm web flask db current
    echo
    echo "=== Historique des migrations ==="
    docker compose run --rm web flask db history
}

# Revenir en arrière
downgrade_db() {
    print_warning "Attention: Cette opération peut supprimer des données!"
    read -p "Êtes-vous sûr de vouloir revenir en arrière ? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Retour à la migration précédente..."
        docker compose run --rm web flask db downgrade
        print_success "Migration annulée"
    else
        print_info "Opération annulée"
    fi
}

# Initialiser avec des données de test
init_data() {
    print_info "Initialisation avec des données de test..."
    docker compose run --rm web flask init-db
    print_success "Données de test créées"
}

# Réinitialiser complètement la base
reset_db() {
    print_error "ATTENTION: Cette opération supprimera TOUTES les données!"
    read -p "Tapez 'RESET' pour confirmer: " confirm
    
    if [ "$confirm" = "RESET" ]; then
        print_info "Réinitialisation de la base de données..."
        docker compose run --rm web flask reset-db
        print_success "Base de données réinitialisée"
    else
        print_info "Opération annulée"
    fi
}

# Sauvegarder la base de données
backup_db() {
    local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    print_info "Sauvegarde de la base de données..."
    docker compose exec db pg_dump -U postgres flask_auth_currency > "$backup_file"
    print_success "Sauvegarde créée: $backup_file"
}

# Restaurer la base de données
restore_db() {
    read -p "Chemin du fichier de sauvegarde: " backup_file
    
    if [ ! -f "$backup_file" ]; then
        print_error "Fichier de sauvegarde introuvable: $backup_file"
        exit 1
    fi
    
    print_warning "Cette opération remplacera toutes les données actuelles!"
    read -p "Continuer ? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Restauration de la base de données..."
        docker compose exec -T db psql -U postgres flask_auth_currency < "$backup_file"
        print_success "Base de données restaurée"
    else
        print_info "Opération annulée"
    fi
}

# Installation complète pour nouveau projet
full_setup() {
    print_info "🚀 Installation complète d'un nouveau projet"
    
    # 1. Vérifications
    check_docker
    
    # 2. Démarrer la base
    start_db
    
    # 3. Construire l'application
    print_info "Construction de l'image de l'application..."
    docker compose build web
    
    # 4. Initialiser les migrations
    init_migrations
    
    # 5. Créer la première migration
    create_migration "Initial migration"
    
    # 6. Appliquer les migrations
    upgrade_db
    
    # 7. Initialiser les données
    init_data
    
    print_success "🎉 Installation terminée!"
    print_info "Vous pouvez maintenant démarrer l'application avec:"
    print_info "docker compose up"
}

# Déploiement en production
deploy() {
    print_info "🚀 Déploiement en production"
    
    # Sauvegarder avant le déploiement
    backup_db
    
    # Arrêter les services
    print_info "Arrêt des services..."
    docker compose down
    
    # Reconstruire
    print_info "Reconstruction des images..."
    docker compose build
    
    # Démarrer la base
    start_db
    
    # Appliquer les migrations
    upgrade_db
    
    # Redémarrer tous les services
    print_info "Redémarrage des services..."
    docker compose up -d
    
    print_success "✅ Déploiement terminé!"
}

# Menu d'aide
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commandes disponibles:"
    echo "  setup          Installation complète (nouveau projet)"
    echo "  start-db       Démarrer PostgreSQL et Redis"
    echo "  init           Initialiser le système de migrations"
    echo "  migrate [msg]  Créer une nouvelle migration"
    echo "  upgrade        Appliquer les migrations"
    echo "  status         Voir l'état des migrations"
    echo "  downgrade      Revenir à la migration précédente"
    echo "  init-data      Créer des données de test"
    echo "  reset          Réinitialiser complètement la base"
    echo "  backup         Sauvegarder la base de données"
    echo "  restore        Restaurer la base de données"
    echo "  deploy         Déploiement en production"
    echo "  help           Afficher cette aide"
    echo
    echo "Exemples:"
    echo "  $0 setup                           # Installation complète"
    echo "  $0 migrate \"Add user phone\"        # Nouvelle migration"
    echo "  $0 upgrade                         # Appliquer les migrations"
    echo "  $0 status                          # Voir l'état"
}

# Menu principal
case "${1:-help}" in
    setup)
        full_setup
        ;;
    start-db)
        check_docker
        start_db
        ;;
    init)
        check_docker
        start_db
        init_migrations
        ;;
    migrate)
        check_docker
        create_migration "$2"
        ;;
    upgrade)
        check_docker
        upgrade_db
        ;;
    status)
        check_docker
        status_migrations
        ;;
    downgrade)
        check_docker
        downgrade_db
        ;;
    init-data)
        check_docker
        init_data
        ;;
    reset)
        check_docker
        reset_db
        ;;
    backup)
        check_docker
        backup_db
        ;;
    restore)
        check_docker
        restore_db
        ;;
    deploy)
        check_docker
        deploy
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Commande inconnue: $1"
        show_help
        exit 1
        ;;
esac