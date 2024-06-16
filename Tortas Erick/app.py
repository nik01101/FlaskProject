from flask import Flask, request, render_template, redirect, url_for, session
import pyodbc

app = Flask(__name__)
app.secret_key = 'your_secret_key'

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=NIKO;'
    'DATABASE=UserDB;'
    'Trusted_Connection=yes;'
)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Username = ? AND Password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return "Invalid username or password"

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
