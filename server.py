from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def LandingPage():
    return render_template("index.html");

@app.route("/register")
def RegisterPage():
    return render_template("register.html");

if __name__ == "__main__":
    app.run(debug = True)