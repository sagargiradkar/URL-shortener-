from flask import Flask, render_template, request, redirect, flash
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['original_url']
    if not original_url.startswith('http://') and not original_url.startswith('https://'):
        original_url = 'http://' + original_url
    
    short_url = generate_short_url()
    
    with sqlite3.connect('db.sqlite') as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
        connection.commit()
    
    flash(f'Shortened URL: {request.host}/{short_url}', 'success')
    return redirect('/')

@app.route('/<short_url>')
def redirect_to_original(short_url):
    with sqlite3.connect('db.sqlite') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT original_url FROM urls WHERE short_url = ?', (short_url,))
        result = cursor.fetchone()
    
    if result:
        original_url = result[0]
        return redirect(original_url)
    else:
        flash('URL not found', 'danger')
        return redirect('/')

def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

if __name__ == '__main__':
    with sqlite3.connect('db.sqlite') as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY AUTOINCREMENT, original_url TEXT, short_url TEXT)')

    app.run(debug=True)
