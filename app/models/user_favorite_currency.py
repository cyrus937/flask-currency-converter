# app/models/user_favorite_currency.py
from app.extensions import db
from app.models.base import BaseModel


class UserFavoriteCurrency(BaseModel):
    """Modèle des devises favorites par utilisateur"""
    __tablename__ = 'user_favorite_currencies'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    currency_code = db.Column(db.String(3), nullable=False)
    order_index = db.Column(db.Integer, default=0)  # Pour l'ordre d'affichage
    
    # Contrainte d'unicité sur la combinaison user_id + currency_code
    __table_args__ = (
        db.UniqueConstraint('user_id', 'currency_code', name='unique_user_currency'),
        db.Index('idx_user_favorites', 'user_id', 'order_index'),
    )
    
    def __init__(self, user_id, currency_code, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.currency_code = currency_code.upper()
        
        # Auto-incrémente order_index
        if not self.order_index:
            last_favorite = UserFavoriteCurrency.query.filter_by(user_id=user_id)\
                                                     .order_by(UserFavoriteCurrency.order_index.desc())\
                                                     .first()
            self.order_index = (last_favorite.order_index + 1) if last_favorite else 0
    
    @classmethod
    def get_user_favorites(cls, user_id):
        """Récupère les devises favorites d'un utilisateur dans l'ordre"""
        return cls.query.filter_by(user_id=user_id)\
                       .order_by(cls.order_index).all()
    
    @classmethod
    def reorder_favorites(cls, user_id, currency_orders):
        """Réorganise l'ordre des devises favorites
        
        Args:
            user_id: ID de l'utilisateur
            currency_orders: Dict {currency_code: order_index}
        """
        for currency_code, order_index in currency_orders.items():
            favorite = cls.query.filter_by(
                user_id=user_id,
                currency_code=currency_code.upper()
            ).first()
            
            if favorite:
                favorite.order_index = order_index
        
        db.session.commit()
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'currency_code': self.currency_code,
            'order_index': self.order_index,
            'added_at': self.created_at.isoformat()
        }