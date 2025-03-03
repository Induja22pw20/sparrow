from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to initialize the database
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS items
                        (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price REAL, market_cap REAL)''')

# Function to fetch data from CoinGecko API and store it in the database
def fetch_and_store_data():
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
    response = requests.get(url)
    data = response.json()

    with sqlite3.connect('database.db') as conn:
        conn.execute('DELETE FROM items')  # Clear existing data
        for coin in data:
            conn.execute('INSERT INTO items (name, price, market_cap) VALUES (?, ?, ?)',
                         (coin['name'], coin['current_price'], coin['market_cap']))

# Route for sign-up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect('database.db') as conn:
            try:
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                             (username, generate_password_hash(password)))
                flash('Account created successfully!', 'success')
                return redirect(url_for('signin'))
            except sqlite3.IntegrityError:
                flash('Username already exists!', 'danger')
    
    return render_template('signup.html')

# Route for sign-in
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect('database.db') as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user and check_password_hash(user[2], password):
                session['username'] = username
                flash('You are logged in!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password!', 'danger')
    
    return render_template('signin.html')

# Route for logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('signin'))  # Redirect to the sign-in page

# Route to display all items (home page)
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('signin'))

    with sqlite3.connect('database.db') as conn:
        items = conn.execute('SELECT * FROM items').fetchall()
    return render_template('home.html', items=items)

# Route to add a new item
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'username' not in session:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        market_cap = request.form['market_cap']
        with sqlite3.connect('database.db') as conn:
            conn.execute('INSERT INTO items (name, price, market_cap) VALUES (?, ?, ?)', (name, price, market_cap))
        return redirect(url_for('home'))
    return render_template('add.html')

# Route to delete an item
@app.route('/delete/<int:item_id>')
def delete(item_id):
    if 'username' not in session:
        return redirect(url_for('signin'))

    with sqlite3.connect('database.db') as conn:
        conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    return redirect(url_for('home'))

# Route to update an item
@app.route('/update/<int:item_id>', methods=['GET', 'POST'])
def update(item_id):
    if 'username' not in session:
        return redirect(url_for('signin'))

    with sqlite3.connect('database.db') as conn:
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            market_cap = request.form['market_cap']
            conn.execute('UPDATE items SET name = ?, price = ?, market_cap = ? WHERE id = ?', (name, price, market_cap, item_id))
            return redirect(url_for('home'))
        
        item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    return render_template('update.html', item=item)

# Initialize the database and fetch data from CoinGecko API
init_db()
fetch_and_store_data()

# Redirect root URL to sign-in
@app.route('/')
def index():
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)  # Change to your desired port number