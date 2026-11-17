# Servidor

import os
import sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "movesafe.db")
CHAVE = os.environ.get("MOVESAFE_KEY", "chave-de-teste")
ZONAS = {"segura", "limite", "sobrecarga"}
CAMPOS = ["sessao_id", "timestamp", "temperatura", "fc", "rmssd",
          "emg_rms", "fadiga_pct", "zona", "alerta_ativo"]


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def iniciar_bd():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS doentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_clinico TEXT, idade INTEGER, patologia TEXT, protocolo TEXT
    );
    CREATE TABLE IF NOT EXISTS sessoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doente_id INTEGER REFERENCES doentes(id),
        data TEXT, hora_inicio TEXT, duracao_min INTEGER, profissional TEXT
    );
    CREATE TABLE IF NOT EXISTS registos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sessao_id INTEGER REFERENCES sessoes(id),
        timestamp TEXT, temperatura REAL, fc INTEGER, rmssd REAL,
        emg_rms REAL, fadiga_pct REAL, zona TEXT, alerta_ativo INTEGER
    );
    """)
    # dados de teste (só se a BD estiver vazia)
    if con.execute("SELECT COUNT(*) FROM doentes").fetchone()[0] == 0:
        con.execute("INSERT INTO doentes (codigo_clinico, idade, patologia, protocolo) "
                    "VALUES ('DOENTE-TESTE', 60, 'Teste', 'Protocolo de teste')")
        con.execute("INSERT INTO sessoes (doente_id, data, hora_inicio, duracao_min, profissional) "
                    "VALUES (1, date('now'), time('now'), 0, 'Profissional Teste')")
    con.commit()
    con.close()


iniciar_bd()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/saude")
def saude():
    return jsonify(estado="online")


@app.route("/api/dados", methods=["POST"])
def receber():
    if request.headers.get("X-API-Key") != CHAVE:
        return jsonify(erro="não autorizado"), 401

    d = request.get_json(silent=True)
    if not d:
        return jsonify(erro="JSON inválido"), 400

    em_falta = [c for c in CAMPOS if c not in d]
    if em_falta:
        return jsonify(erro="campos em falta", campos=em_falta), 400
    if d["zona"] not in ZONAS:
        return jsonify(erro="zona inválida"), 400

    con = db()
    con.execute(
        "INSERT INTO registos (sessao_id, timestamp, temperatura, fc, rmssd, "
        "emg_rms, fadiga_pct, zona, alerta_ativo) VALUES (?,?,?,?,?,?,?,?,?)",
        (d["sessao_id"], d["timestamp"], d["temperatura"], d["fc"], d["rmssd"],
         d["emg_rms"], d["fadiga_pct"], d["zona"], int(bool(d["alerta_ativo"]))))
    con.commit()
    con.close()
    return jsonify(ok=True), 201


@app.route("/api/ultimos/<int:sessao_id>")
def ultimos(sessao_id):
    con = db()
    linhas = con.execute(
        "SELECT * FROM registos WHERE sessao_id=? ORDER BY id DESC LIMIT 60",
        (sessao_id,)).fetchall()
    con.close()
    return jsonify([dict(l) for l in linhas][::-1])


if __name__ == "__main__":
    app.run(debug=True)