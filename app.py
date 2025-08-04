from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "sua_senha_secreta_aqui"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

SENHA_HASH = generate_password_hash("1234")  # Altere para sua senha segura

def init_db():
    if not os.path.exists("dados.db"):
        conn = sqlite3.connect("dados.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logado"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def obter_itens():
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("SELECT id, nome FROM itens")
    itens = c.fetchall()
    conn.close()
    return itens

@app.route("/")
def publico():
    itens = obter_itens()
    return render_template("index.html", itens=itens, admin=False)

@app.route("/admin")
@login_required
def admin():
    itens = obter_itens()
    return render_template("index.html", itens=itens, admin=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == "admin" and check_password_hash(SENHA_HASH, senha):
            session["logado"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", erro="Credenciais inválidas.")
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.pop("logado", None)
    return redirect(url_for("publico"))

@app.route("/add", methods=["POST"])
@login_required
def adicionar():
    item = request.form.get("item")
    if item:
        conn = sqlite3.connect("dados.db")
        c = conn.cursor()
        c.execute("INSERT INTO itens (nome) VALUES (?)", (item,))
        conn.commit()
        conn.close()
    return redirect(url_for("admin"))

@app.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remover(item_id):
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("DELETE FROM itens WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
