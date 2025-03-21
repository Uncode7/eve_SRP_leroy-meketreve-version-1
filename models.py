from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from app import db, bcrypt  # Importa o bcrypt já inicializado do app.py
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # user, admin ou manager

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @staticmethod
    def create_admin():
        """Cria a conta de admin se ela ainda não existir."""
        if not User.query.filter_by(role="admin").first():
            admin = User(username="admin", role="admin")
            admin.set_password("admin123")  # Você pode mudar isso depois
            db.session.add(admin)
            db.session.commit()
# MODELOS DE NAVES

class Ship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('order.user_id'), nullable=False)
    ship_name = db.Column(db.Integer, db.ForeignKey('order.ship_id'), nullable=False)
    quantity = db.Column(db.Integer, db.ForeignKey('order.quantity'), nullable=False)

    #user = db.relationship('User', backref=db.backref('orders', lazy=True))
    #ship = db.relationship('Ship', backref=db.backref('orders', lazy=True))
    

    def __init__(self, user_id, ship_id, quantity=1):
        self.user_id = user_id
        self.ship_id = ship_id
        self.quantity = quantity

