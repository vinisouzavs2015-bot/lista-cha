from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "sua_senha_secreta"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Hash da senha admin (mude "1234" para sua senha segura)
SENHA_HASH = generate_password_hash("1234")

# Inicializa o banco
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

# Decorador para rotas que precisam de login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logado"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Função para obter itens do banco
def obter_itens():
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("SELECT id, nome FROM itens")
    itens = c.fetchall()
    conn.close()
    return itens

# Página principal (visualização pública)
@app.route("/")
def home():
    itens = obter_itens()
    return render_template("index.html", itens=itens, admin=False)

# Página admin (com login)
@app.route("/admin")
@login_required
def admin():
    itens = obter_itens()
    return render_template("index.html", itens=itens, admin=True)

# Login
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

# Logout via POST
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.pop("logado", None)
    return redirect(url_for("home"))

# Adicionar item
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

# Remover item
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
