from app import create_app
from app.extensions import db
from app.models.user import User
import getpass


def create_admin_user():
    """Crée un utilisateur administrateur"""
    
    app = create_app()
    
    with app.app_context():
        print("Création d'un utilisateur administrateur")
        print("-" * 40)
        
        email = input("Email: ")
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.find_by_email(email)
        if existing_user:
            print(f"Un utilisateur avec l'email {email} existe déjà!")
            return
        
        password = getpass.getpass("Mot de passe: ")
        password_confirm = getpass.getpass("Confirmer le mot de passe: ")
        
        if password != password_confirm:
            print("Les mots de passe ne correspondent pas!")
            return
        
        first_name = input("Prénom: ")
        last_name = input("Nom: ")
        
        try:
            user = User.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Marquer comme premium et vérifié
            user.is_premium = True
            user.is_verified = True
            user.save()
            
            print(f"\nUtilisateur administrateur créé avec succès!")
            print(f"Email: {user.email}")
            print(f"ID: {user.id}")
            
        except Exception as e:
            print(f"Erreur lors de la création: {e}")


if __name__ == '__main__':
    create_admin_user()