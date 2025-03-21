from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, bcrypt
from models import User, Ship, Order

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login inválido!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Verifica se o usuário já existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nome de usuário já está em uso. Escolha outro.', 'danger')
            return redirect(url_for('register'))

        # Cria um novo usuário com senha hashada
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/dashboard')
@login_required
def dashboard():
    ships = Ship.query.all()
    orders = Order.query.all()
    users = None
    if current_user.role == 'user':
        orders = Order.query.filter_by(user_id=current_user.id).all()
    if current_user.role in ['manager', 'admin']:
        users = User.query.all()
    return render_template('dashboard.html', ships=ships, orders=orders, users=users)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/ships')
@login_required
def list_ships():
    ships = Ship.query.all()
    return render_template('ships.html', ships=ships)

