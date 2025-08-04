from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "sua_senha_secreta_aqui"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Inicial senha admin hash (começa como "1234")
senha_hash = generate_password_hash("1234")

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
    global senha_hash
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == "admin" and check_password_hash(senha_hash, senha):
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

@app.route("/alterar-senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    global senha_hash
    if request.method == "POST":
        senha_atual = request.form.get("senha_atual")
        nova_senha = request.form.get("nova_senha")
        confirma_senha = request.form.get("confirma_senha")

        if not check_password_hash(senha_hash, senha_atual):
            flash("Senha atual incorreta.", "erro")
        elif nova_senha != confirma_senha:
            flash("Nova senha e confirmação não conferem.", "erro")
        elif len(nova_senha) < 4:
            flash("Senha nova deve ter ao menos 4 caracteres.", "erro")
        else:
            senha_hash = generate_password_hash(nova_senha)
            flash("Senha alterada com sucesso!", "sucesso")
            return redirect(url_for("admin"))

    return render_template("alterar_senha.html")

if __name__ == "__main__":
    app.run(debug=True)
