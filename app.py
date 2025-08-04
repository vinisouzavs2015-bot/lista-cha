from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "sua_senha_secreta"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Inicializa o banco (somente se não existir)
def init_db():
    if not os.path.exists("dados.db"):
        conn = sqlite3.connect("dados.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS itens (id INTEGER PRIMARY KEY, nome TEXT)")
        conn.commit()
        conn.close()

# Chamada única ao iniciar o app
init_db()

# Função para obter os itens do banco
def obter_itens():
    conn = sqlite3.connect("dados.db")
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

# Rota protegida (requer login)
@app.route("/admin")
def admin():
    if not session.get("logado"):
        return redirect(url_for("login"))
    itens = obter_itens()
    return render_template("index.html", itens=itens, admin=True)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "").strip()
        if usuario == "admin" and senha == "1234":
            session["logado"] = True
            return redirect(url_for("admin"))
        else:
            erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)

# Logout
@app.route("/logout")
def logout():
    session.pop("logado", None)
    return redirect(url_for("home"))

# Adicionar item
@app.route("/add", methods=["POST"])
def adicionar():
    if not session.get("logado"):
        return redirect(url_for("login"))
    item = request.form.get("item", "").strip()
    if item:
        conn = sqlite3.connect("dados.db")
        c = conn.cursor()
        c.execute("INSERT INTO itens (nome) VALUES (?)", (item,))
        conn.commit()
        conn.close()
    return redirect(url_for("admin"))

# Remover item
@app.route("/remove/<int:item_id>", methods=["POST"])
def remover(item_id):
    if not session.get("logado"):
        return redirect(url_for("login"))
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("DELETE FROM itens WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

# Roda o app localmente
if __name__ == "__main__":
    app.run(debug=True)
