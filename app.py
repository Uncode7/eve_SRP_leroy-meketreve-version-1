from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'eve_ship_request_secret'
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


    # CRIAÇÃO MANUAL DO BANCO DE DADOS


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'admin'))
            );
            INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin', 'admin');
            INSERT OR IGNORE INTO users (username, password, role) VALUES ('user1', '123', 'user'), ('user2', '123', 'user'), ('user3', '123', 'user');
            
            CREATE TABLE IF NOT EXISTS ships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );
            INSERT OR IGNORE INTO ships (name) VALUES ('Ferox'), ('Ferox Navy Issue'), ('Caracal');
            
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ship_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (ship_id) REFERENCES ships(id)
            );
        ''')
        db.commit()


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            error = "Usuário ou senha inválidos."
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ships")
    ships = cursor.fetchall()
    return render_template('dashboard.html', ships=ships)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/order', methods=['POST'])
def order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()

    # Obtemos todos os IDs de naves cadastradas
    cursor.execute("SELECT id FROM ships")
    ships = cursor.fetchall()

    orders_created = False

    for ship in ships:
        field_name = f'ship_{ship["id"]}'
        quantity = request.form.get(field_name)
        if quantity and int(quantity) > 0:
            cursor.execute("""
                INSERT INTO orders (user_id, ship_id, quantity) 
                VALUES (?, ?, ?)
            """, (user_id, ship["id"], int(quantity)))
            orders_created = True

    if orders_created:
        db.commit()

    return redirect(url_for('dashboard'))



@app.route('/admin/orders')
def admin_orders():
    # Apenas admins podem acessar esta rota
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    # Consulta que junta informações de orders, usuários e naves
    cursor.execute('''
        SELECT orders.id as order_id, users.username, ships.name as ship_name, orders.quantity, orders.status
        FROM orders
        JOIN users ON orders.user_id = users.id
        JOIN ships ON orders.ship_id = ships.id
    ''')
    orders = cursor.fetchall()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/orders/deliver/<int:order_id>')
def deliver_order(order_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE orders SET status = 'delivered' WHERE id = ?", (order_id,))
    db.commit()
    return redirect(url_for('admin_orders'))

@app.route('/admin/orders/delete/<int:order_id>')
def delete_order(order_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    db.commit()
    return redirect(url_for('admin_orders'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)