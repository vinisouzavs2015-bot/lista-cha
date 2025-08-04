from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "sua_senha_secreta"

# Sessão salva em arquivo
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Caminho absoluto do banco
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados.db")

# Inicializa o banco se ele não existir
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
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

# Obter todos os itens
def obter_itens():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, nome FROM itens")
    itens = c.fetchall()
    conn.close()
    return itens

# Rota pública (sem login)
@app.route("/")
def home():
    itens = obter_itens()
    return render_template("index.html", itens=itens, admin=False)

# Rota do painel admin (com login)
@app.route("/admin")
def admin():
    if not session.get("logado"):
        return redirect(url_for("login"))
    itens = obter_itens()
    return render_template("index.html", itens=itens, admin=True)

# Login admin
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == "admin" and senha == "1234":
            session["logado"] = True
            return redirect(url_for("admin"))
        else:
            erro = "Usuário ou senha inválidos"
    return render_template("login.html", erro=erro)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Adicionar item (apenas logado)
@app.route("/add", methods=["POST"])
def adicionar():
    if not session.get("logado"):
        return redirect(url_for("login"))
    nome = request.form.get("item")
    if nome:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO itens (nome) VALUES (?)", (nome,))
        conn.commit()
        conn.close()
    return redirect(url_for("admin"))

# Remover item (apenas logado)
@app.route("/remove/<int:item_id>", methods=["POST"])
def remover(item_id):
    if not session.get("logado"):
        return redirect(url_for("login"))
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM itens WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

# Rodar localmente
if __name__ == "__main__":
    app.run(debug=True)
