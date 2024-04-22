from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

app = Flask(__name__)

# Secret key for sessions
app.secret_key = 'nyuad'  # Change to a random secret key

# Basic MySQL configurations (used for guest access)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'nyuad_crimes'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def run_statement(statement):
    cursor = mysql.connection.cursor()
    cursor.execute(statement)
    results = cursor.fetchall()
    mysql.connection.commit()
    df = ""
    if cursor.description:
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
    cursor.close()
    return df

@app.route('/')
def landing_page():
    if 'username' in session:
        return redirect(url_for('choose_table'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pwd']
        hashed_password = generate_password_hash(password)
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_exists = cursor.fetchone()
        
        if user_exists:
            flash('Username already exists!')
            return redirect(url_for('register_page'))
        
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, hashed_password))
        mysql.connection.commit()
        cursor.close()
        
        flash('User successfully registered!')
        return redirect(url_for('landing_page'))
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['uname']
    password = request.form['pwd']
    dev_password = request.form.get('dev_pwd', '')

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()

    if user and check_password_hash(user['password_hash'], password):
        session['username'] = user['username']
        session['user_role'] = 'admin' if dev_password == 'developer123' else 'guest'
        return redirect(url_for('choose_table'))
    
    flash('Invalid username or password!')
    return redirect(url_for('landing_page'))

@app.route('/choose_table')
def choose_table():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    return render_template('choose_table.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('landing_page'))

@app.route('/criminals', methods=['GET', 'POST'])
def criminals():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if request.method == 'POST':
        search_query = request.form['search']
        query = "SELECT * FROM criminals WHERE Name LIKE %s OR Criminal_ID LIKE %s"
        search_string = f'%{search_query}%'
        criminals_data = run_statement(query, [search_string, search_string])
    else:
        query = "SELECT * FROM criminals"
        criminals_data = run_statement(query)
    return render_template('criminals.html', criminals=criminals_data)

def run_statement(statement, params=None):
    cursor = mysql.connection.cursor()
    cursor.execute(statement, params or ())
    results = cursor.fetchall()
    mysql.connection.commit()
    df = ""
    if cursor.description:
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
    cursor.close()
    return df

@app.route('/add_criminal', methods=['GET', 'POST'])
def add_criminal():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        violent = request.form['violent']
        probation = request.form['probation']
        query = "INSERT INTO criminals (Name, Address, Violent_Offender_Status, Probation_Status) VALUES (%s, %s, %s, %s)"
        run_statement(query, (name, address, violent, probation))
        flash('Criminal added successfully!')
        return redirect(url_for('criminals'))
    return render_template('add_criminal.html')

@app.route('/edit_criminal>', methods=['GET', 'POST'])
def edit_criminal(criminal_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        violent = request.form['violent']
        probation = request.form['probation']
        query = "UPDATE criminals SET Name=%s, Address=%s, Violent_Offender_Status=%s, Probation_Status=%s WHERE Criminal_ID=%s"
        run_statement(query, (name, address, violent, probation, criminal_id))
        flash('Criminal updated successfully!')
        return redirect(url_for('criminals'))
    else:
        query = "SELECT * FROM criminals WHERE Criminal_ID = %s"
        criminal = run_statement(query, (criminal_id,))
        return render_template('edit_criminal.html', criminal=criminal.iloc[0])

# @app.route('/delete_criminal/>', methods=['POST'])
# def delete_criminal(criminal_id):
#     if 'username' not in session:
#         return redirect(url_for('landing_page'))
#     query = "DELETE FROM criminals WHERE Criminal_ID = %s"
#     run_statement(query, (criminal_id,))
#     flash('Criminal deleted successfully!')
#     return redirect(url_for('criminals'))

# Explicit route for the 'crimes' table
@app.route('/crimes')
def crimes():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    return render_template('crimes.html')

# Explicit route for the 'crime_codes' table
@app.route('/crime_codes')
def crime_codes():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    return render_template('crime_codes.html')

# Explicit route for the 'sentencing' table
@app.route('/sentencing')
def sentencing():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    return render_template('sentencing.html')

# Explicit route for the 'appeals' table
@app.route('/appeals')
def appeals():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    return render_template('appeals.html')

# Explicit route for the 'police_officers' table
@app.route('/police_officers')
def police_officers():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    return render_template('police_officers.html')

if __name__ == '__main__':
    app.run(port = 5000, debug = True)