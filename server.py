from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import os

app = Flask(__name__)
POLICE_OFFICER_PASSWORD = 'nyuad'

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
    dev_password = request.form.get('dev_pwd', None)

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()

    if user and check_password_hash(user['password_hash'], password):
        session['username'] = user['username']
        session['user_role'] = 'admin' if dev_password == 'developer123' else 'guest'
        if dev_password and dev_password == POLICE_OFFICER_PASSWORD:
            session['user_role'] = 'developer'
        else:
            session['user_role'] = 'guest'
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
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('criminals'))

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
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('criminals'))
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
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('criminals'))
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
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('crimes'))

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
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('crimes'))

    if request.method == 'POST':
        classification = request.form['classification']
        date_charged = request.form['date_charged']
        appeal_status = request.form['appeal_status']
        hearing_date = request.form['hearing_date']
        amount_of_fine = request.form['amount_of_fine']
        court_fee = request.form['court_fee']
        amount_paid = request.form['amount_paid']
        payment_due_date = request.form['payment_due_date']
        charge_status = request.form['charge_status']

        query = """UPDATE crimes SET Classification=%s, Date_Charged=%s, Appeal_Status=%s, Hearing_Date=%s, 
                   Amount_Of_Fine=%s, Court_Fee=%s, Amount_Paid=%s, Payment_Due_Date=%s, Charge_Status=%s
                   WHERE Crime_ID=%s"""
        run_statement(query, (classification, date_charged, appeal_status, hearing_date, amount_of_fine, court_fee, 
                              amount_paid, payment_due_date, charge_status, crime_id))
        flash('Crime updated successfully!')
        return redirect(url_for('crimes'))
    else:
        query = "SELECT * FROM crimes WHERE Crime_ID = %s"
        crime = run_statement(query, (crime_id,))
        if crime.empty:
            flash("No crime found with the given ID.")
            return redirect(url_for('crimes'))
        return render_template('edit_crimes.html', crime=crime.iloc[0])


@app.route('/delete_crimes/<int:crime_id>', methods=['GET', 'POST'])
def delete_crimes(crime_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('crimes'))

    if request.method == 'POST':
        query = "DELETE FROM crimes WHERE Crime_ID = %s"
        run_statement(query, (crime_id,))
        flash('Crime deleted successfully!')
        return redirect(url_for('crimes'))

@app.route('/search_crimes', methods=['GET', 'POST'])
def search_crimes():
    if 'username' not in session:
        return redirect(url_for('landing_page'))

    search_results = None
    if request.method == 'POST':
        search_type = request.form['search_type']
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Crimes WHERE Classification LIKE %s"
        cursor.execute(query, ('%' + search_type + '%',))
        search_results = cursor.fetchall()
        cursor.close()

    return render_template('search_crimes.html', search_results=search_results)
        
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
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('sentencings'))

    if request.method == 'POST':
        # Retrieve data from the form
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        num_violations = request.form['num_violations']
        sentence_type = request.form['sentence_type']

        # Insert data into database
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO sentencing (Start_Date, End_Date, Number_of_Violations, Type_of_Sentence) VALUES (%s, %s, %s, %s)"
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
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('sentencings'))

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
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('sentencings'))
    query = "DELETE FROM sentencing WHERE Sentence_ID = %s"
    run_statement(query, (sentence_id,))
    flash('Sentencing record deleted successfully!')
    return redirect(url_for('sentencings'))

@app.route('/appeals')
def appeals():
    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('landing_page'))

    # Retrieve appeals data from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Appeals")
    appeals_data = cursor.fetchall()
    cursor.close()

    # Render the appeals template with the appeals data
    return render_template('appeals.html', appeals=appeals_data)

@app.route('/add_appeals', methods=['GET', 'POST'])
def add_appeals():
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('appeals'))

    if request.method == 'POST':
        filing_date = request.form['filing_date']
        hearing_date = request.form['hearing_date']
        status = request.form['status']

        # Insert data into the database
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO appeals (Appeal_Filing_Date, Appeal_Hearing_Date, Status) VALUES (%s, %s, %s)"
        cursor.execute(sql, (filing_date, hearing_date, status))
        mysql.connection.commit()
        cursor.close()
        flash('Appeal added successfully!')
        return redirect(url_for('appeals'))

    return render_template('add_appeals.html')

@app.route('/edit_appeals/<int:appeal_id>', methods=['GET', 'POST'])
def edit_appeals(appeal_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('appeals'))
    if request.method == 'POST':
        filing_date = request.form['filing_date']
        hearing_date = request.form['hearing_date']
        status = request.form['status']

        # Update the appeal in the database
        query = "UPDATE appeals SET Appeal_Filing_Date=%s, Appeal_Hearing_Date=%s, Status=%s WHERE Appeal_ID=%s"
        run_statement(query, (filing_date, hearing_date, status, appeal_id))
        flash('Appeal updated successfully!')
        return redirect(url_for('appeals'))
    else:
        query = "SELECT * FROM appeals WHERE Appeal_ID = %s"
        appeal = run_statement(query, (appeal_id,))
        return render_template('edit_appeals.html', appeal=appeal.iloc[0])

@app.route('/delete_appeals/<int:appeal_id>', methods=['POST'])
def delete_appeals(appeal_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('appeals'))
    query = "DELETE FROM appeals WHERE Appeal_ID = %s"
    run_statement(query, (appeal_id,))
    flash('Appeal deleted successfully!')
    return redirect(url_for('appeals'))

@app.route('/search_appeals', methods=['GET', 'POST'])
def search_appeals():
    search_results = None
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search_id = request.form['search_id']
        cursor = mysql.connection.cursor()
        like_string = f"%{search_id}%"
        cursor.execute("SELECT * FROM appeals WHERE Appeal_ID LIKE %s", (like_string,))
        search_results = cursor.fetchall()
        cursor.close()

    return render_template('search_appeals.html', search_results=search_results)

@app.route('/police_officers')
def police_officers():
    if 'username' not in session:
        return redirect(url_for('landing_page'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Police_Officers")
    officers = cursor.fetchall()
    cursor.close()

    return render_template('police_officers.html', police_officers=officers)

@app.route('/add_police_officers', methods=['GET', 'POST'])
def add_police_officers():
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('police_officers'))
    if request.method == 'POST':
        badge_number = request.form['badgeNumber']
        name = request.form['name']
        precinct = request.form['precinct']
        status = request.form['status']

        cursor = mysql.connection.cursor()
        insert_query = """INSERT INTO Police_Officers (Badge_Number, Name, Precinct, Status) 
                          VALUES (%s, %s, %s, %s)"""
        cursor.execute(insert_query, (badge_number, name, precinct, status))
        mysql.connection.commit()
        cursor.close()
        
        flash('Police officer added successfully!', 'success')
        return redirect(url_for('police_officers'))

    # If it's a GET request, just render the template
    return render_template('add_police_officers.html')

@app.route('/edit_police_officers/<int:badge_number>', methods=['GET', 'POST'])
def edit_police_officers(badge_number):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('police_officers'))
    
    cursor = mysql.connection.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        precinct = request.form['precinct']
        status = request.form['status']

        update_query = """UPDATE Police_Officers 
                          SET Name = %s, Precinct = %s, Status = %s 
                          WHERE Badge_Number = %s"""
        cursor.execute(update_query, (name, precinct, status, badge_number))
        mysql.connection.commit()
        flash('Police officer updated successfully!', 'success')
        return redirect(url_for('police_officers'))
    
    else:
        cursor.execute("SELECT * FROM Police_Officers WHERE Badge_Number = %s", (badge_number,))
        officer = cursor.fetchone()
        cursor.close()

        return render_template('edit_police_officers.html', officer=officer)

@app.route('/delete_police_officers/<int:badge_number>', methods=['POST'])
def delete_police_officers(badge_number):
    if 'username' not in session:
        return redirect(url_for('landing_page'))
    if 'username' not in session or session.get('user_role') != 'developer':
        flash('You do not have permission to act on this page.')
        return render_template('redirect.html', url=url_for('police_officers'))
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM Police_Officers WHERE Badge_Number = %s"
    cursor.execute(delete_query, (badge_number,))
    mysql.connection.commit()
    cursor.close()
    flash('Police officer deleted successfully!', 'success')
    return redirect(url_for('police_officers'))

@app.route('/search_police_officers', methods=['GET', 'POST'])
def search_police_officers():
    if 'username' not in session:
        return redirect(url_for('landing_page'))

    search_results = None
    if request.method == 'POST':
        search_name = request.form['search_name']
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Police_Officers WHERE Name LIKE %s"
        cursor.execute(query, ('%' + search_name + '%',))
        search_results = cursor.fetchall()
        cursor.close()

    return render_template('search_police_officers.html', search_results=search_results)

@app.route('/search_sentencings', methods=['GET', 'POST'])
def search_sentencings():
    search_results = None  # Initialize the search results variable
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure the user is logged in

    if request.method == 'POST':
        search_name = request.form['search_name']
        cursor = mysql.connection.cursor()
        like_string = f"%{search_name}%"
        cursor.execute("SELECT * FROM sentencing WHERE Type_of_Sentence LIKE %s", (like_string,))
        search_results = cursor.fetchall()
        cursor.close()

    # Render the same template whether it's a GET or POST request
    return render_template('search_sentencings.html', search_results=search_results)

if __name__ == '__main__':
    app.run(port = 5000, debug = True)