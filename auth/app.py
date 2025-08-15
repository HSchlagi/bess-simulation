
from flask import Flask, render_template, request, redirect, session
from supabase import create_client, Client
import sqlite3, os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecret")

# Supabase-Initialisierung
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQLite: Verbindung zu lokaler BESS-Datenbank
def get_db_connection():
    conn = sqlite3.connect("bess_simulation.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session["user"] = result.user.email
            return redirect("/dashboard")
        except Exception as e:
            return f"Login fehlgeschlagen: {str(e)}", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    conn = get_db_connection()
    cur = conn.execute("SELECT * FROM simulation_results LIMIT 10")
    results = cur.fetchall()
    return render_template("dashboard.html", user=session["user"], results=results)

if __name__ == "__main__":
    app.run(debug=True)
