from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
bcrypt.init_app(app)  # Conecta o bcrypt ao Flask
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.login_view = "login"

from routes import *

from models import User  # Importe a classe User

with app.app_context():
    db.create_all()
    User.create_admin()  # Garante que o admin é criado se não existir


if __name__ == '__main__':
    app.run(debug=True)
