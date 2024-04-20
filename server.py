from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_hashing import Hashing

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace 'your_secret_key' with a real secret key
hashing = Hashing(app)

# In-memory "database" to store user data
users = {}

@app.route("/")
def landing_page():
    # Check if user is logged in
    if 'username' in session:
        # Redirect to table choice page
        return redirect(url_for('choose_table'))
    # Show the login page
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pwd']
        # Check if username already exists
        if username in users:
            flash('Username already exists!')
            return redirect(url_for('register_page'))
        # Hash the password before storing it
        hashed_password = hashing.hash_value(password, salt='abc')
        users[username] = hashed_password
        flash('User successfully registered!')
        return redirect(url_for('landing_page'))
    return render_template("register.html")

@app.route("/login", methods=['POST'])
def login():
    username = request.form['uname']
    password = request.form['pwd']
    # Validate user credentials
    if username in users and hashing.check_value(users[username], password, salt='abc'):
        session['username'] = username
        return redirect(url_for('choose_table'))
    flash('Invalid username or password!')
    return redirect(url_for('landing_page'))

@app.route("/choose_table")
def choose_table():
    if 'username' not in session:
        # Redirect to login page if not logged in
        return redirect(url_for('landing_page'))
    # Render the table choice page
    return render_template("choose_table.html", username=session['username'])

@app.route("/logout")
def logout():
    # Remove the user session
    session.pop('username', None)
    return redirect(url_for('landing_page'))

if __name__ == "__main__":
    app.run(debug=True)
