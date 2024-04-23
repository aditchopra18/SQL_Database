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
        df = run_statement("SELECT * FROM criminals;")
        criminals = []
        for index, row in df.iterrows():
            criminals.append(row)
    return render_template('criminals.html', criminals=criminals)


@app.route('/add_criminal', methods=['GET', 'POST'])
def add_criminal():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure the user is logged in

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        violent = request.form['violent'] == 'Yes'
        probation = request.form['probation'] == 'Yes'
        aliases = request.form.getlist('aliases[]')
        phones = request.form.getlist('phones[]')

        # Insert data into database
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO criminals (Name, Address, Violent_Offender_Status, Probation_Status) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (name, address, violent, probation))
        criminal_id = cursor.lastrowid  # Get the last inserted id

        # Insert aliases
        alias_sql = "INSERT INTO criminal_alias (Criminal_ID, Alias) VALUES (%s, %s)"
        for alias in aliases:
            if alias:  # Ensure alias is not empty
                cursor.execute(alias_sql, (criminal_id, alias))

        # Insert phone numbers
        phone_sql = "INSERT INTO criminal_phonenumber (Criminal_ID, Phone_Number) VALUES (%s, %s)"
        for phone in phones:
            if phone:  # Ensure phone number is not empty
                cursor.execute(phone_sql, (criminal_id, phone))

        mysql.connection.commit()
        cursor.close()
        flash('Criminal added successfully with aliases and phone numbers!')
        return redirect(url_for('criminals'))

    return render_template('add_criminal.html')

@app.route('/edit_criminal/<int:criminal_id>', methods=['GET', 'POST'])
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


@app.route('/delete_criminal/<int:criminal_id>', methods=['GET', 'POST'])
def delete_criminal(criminal_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if request.method == 'POST':
        query = "DELETE FROM criminals WHERE Criminal_ID = %s"
        run_statement(query, (criminal_id,))
        flash('Criminal deleted successfully!')
        return redirect(url_for('criminals'))

@app.route('/search_criminals', methods=['GET', 'POST'])
def search_criminals():
    search_results = None  # Initialize the search results variable
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure the user is logged in

    if request.method == 'POST':
        search_name = request.form['search_name']
        cursor = mysql.connection.cursor()
        like_string = f"%{search_name}%"
        cursor.execute("SELECT * FROM Criminals WHERE Name LIKE %s", (like_string,))
        search_results = cursor.fetchall()
        cursor.close()

    # Render the same template whether it's a GET or POST request
    return render_template('search_criminals.html', search_results=search_results)

@app.route('/crimes', methods=['GET', 'POST'])
def crimes():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if request.method == 'POST':
        search_query = request.form['search']
        query = "SELECT * FROM crimes WHERE Crime_ID LIKE %s"
        search_string = f'%{search_query}%'
        crimes_data = run_statement(query, [search_string, search_string])
    else:
        df = run_statement("SELECT * FROM crimes;")
        crimes = []
        for index, row in df.iterrows():
            crimes.append(row)
    return render_template('crimes.html', crimes=crimes)

@app.route('/add_crimes', methods=['GET', 'POST'])
def add_crimes():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure the user is logged in
    if request.method == 'POST':
        classification = request.form['classification']
        date_charged = request.form['date_charged']
        appeal_status = request.form['appeal_status']
        hearing_date = request.form['hearing_date']

        # Insert data into database
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO crimes (Classification, Date_Charged, Appeal_Status, Hearing_Date) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (classification, date_charged, appeal_status, hearing_date))
        crime_id = cursor.lastrowid  # Get the last inserted id

        mysql.connection.commit()
        cursor.close()
        flash('Crime added successfully!')
        return redirect(url_for('crimes'))

    return render_template('add_crimes.html')

@app.route('/edit_crimes/<int:crime_id>', methods=['GET', 'POST'])
def edit_crimes(crime_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if request.method == 'POST':
        classification = request.form['classification']
        date_charged = request.form['date_charged']
        appeal_status = request.form['appeal_status']
        hearing_date = request.form['hearing_date']
        query = "UPDATE crimes SET Classification=%s, Date_Charged=%s, Appeal_Status=%s, Hearing_Date=%s WHERE Crime_ID=%s"
        run_statement(query, (classification, date_charged, appeal_status, hearing_date, crime_id))
        flash('Crime updated successfully!')
        return redirect(url_for('crimes'))
    else:
        query = "SELECT * FROM crimes WHERE Crime_ID = %s"
        crime = run_statement(query, (crime_id,))
        return render_template('edit_crimes.html', crime=crime.iloc[0])


@app.route('/delete_crimes/<int:crime_id>', methods=['GET', 'POST'])
def delete_crimes(crime_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if request.method == 'POST':
        query = "DELETE FROM crimes WHERE Crime_ID = %s"
        run_statement(query, (crime_id,))
        flash('Crime deleted successfully!')
        return redirect(url_for('crimes'))

        
@app.route('/sentencings', methods=['GET', 'POST'])
def sentencings():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if request.method == 'POST':
        search_query = request.form['search']
        query = "SELECT * FROM sentencing WHERE Sentence_ID LIKE %s"
        search_string = f'%{search_query}%'
        sentencings_data = run_statement(query, [search_string, search_string])
    else:
        df = run_statement("SELECT * FROM sentencing;")
        sentencings = []
        for index, row in df.iterrows():
            sentencings.append(row)
    return render_template('sentencings.html', sentencings=sentencings)

@app.route('/add_sentencings', methods=['GET', 'POST'])
def add_sentencings():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure the user is logged in
    if request.method == 'POST':
        # Retrieve data from the form
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        num_violations = request.form['num_violations']
        sentence_type = request.form['sentence_type']

        # Insert data into database
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO sentencing (Start_Date, End_Date, Number_of_Violations, Type_of_Sentence) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (start_date, end_date, num_violations, sentence_type))
        mysql.connection.commit()
        cursor.close()
        
        flash('Sentencing record added successfully!')
        return redirect(url_for('sentencings'))

    return render_template('add_sentencings.html')


@app.route('/edit_sentencings/<int:sentence_id>', methods=['GET', 'POST'])
def edit_sentencings(sentence_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if request.method == 'POST':
        # Retrieve data from the form
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        num_violations = request.form['num_violations']
        sentence_type = request.form['sentence_type']

        # Update data in the database
        cursor = mysql.connection.cursor()
        sql = "UPDATE sentencing SET Start_Date=%s, End_Date=%s, Number_of_Violations=%s, Type_of_Sentence=%s WHERE Sentence_ID=%s"
        cursor.execute(sql, (start_date, end_date, num_violations, sentence_type, sentence_id))
        mysql.connection.commit()
        cursor.close()
        
        flash('Sentencing record updated successfully!')
        return redirect(url_for('sentencings'))
    else:
        query = "SELECT * FROM sentencing WHERE Sentence_ID = %s"
        sentencing = run_statement(query, (sentence_id,))
        return render_template('edit_sentencings.html', sentencing=sentencing.iloc[0])

@app.route('/delete_sentencings/<int:sentence_id>', methods=['GET', 'POST'])
def delete_sentencings(sentence_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    query = "DELETE FROM sentencing WHERE Sentence_ID = %s"
    run_statement(query, (sentence_id,))
    flash('Sentencing record deleted successfully!')
    return redirect(url_for('sentencings'))

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