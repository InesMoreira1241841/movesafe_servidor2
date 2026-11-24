# Servidor

import os
import time
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, static_folder="public", static_url_path="")

DATABASE_URL = os.environ.get("DATABASE_URL")
CHAVE = os.environ.get("MOVESAFE_KEY", "chave-de-teste")
ZONAS = {"segura", "limite", "sobrecarga"}
CAMPOS = ["sessao_id", "timestamp", "temperatura", "fc", "rmssd",
          "emg_rms", "fadiga_pct", "zona", "alerta_ativo"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS doentes (
    id SERIAL PRIMARY KEY,
    codigo_clinico TEXT, idade INTEGER, patologia TEXT, protocolo TEXT
);
CREATE TABLE IF NOT EXISTS sessoes (
    id SERIAL PRIMARY KEY,
    doente_id INTEGER REFERENCES doentes(id),
    data TEXT, hora_inicio TEXT, duracao_min INTEGER, profissional TEXT
);
CREATE TABLE IF NOT EXISTS registos (
    id SERIAL PRIMARY KEY,
    sessao_id INTEGER REFERENCES sessoes(id),
    timestamp TEXT, temperatura REAL, fc INTEGER, rmssd REAL,
    emg_rms REAL, fadiga_pct REAL, zona TEXT, alerta_ativo BOOLEAN
);
"""


def executar(sql, params=(), fetch=False):
    con = psycopg2.connect(DATABASE_URL)
    try:
        with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            resultado = cur.fetchall() if fetch else None
        con.commit()
        return resultado
    finally:
        con.close()


def iniciar_bd():
    executar(SCHEMA)
    n = executar("SELECT COUNT(*) AS n FROM doentes", fetch=True)[0]["n"]
    if n == 0:
        executar("INSERT INTO doentes (codigo_clinico, idade, patologia, protocolo) "
                 "VALUES (%s, %s, %s, %s)",
                 ("DOENTE-TESTE", 60, "Teste", "Protocolo de teste"))
        executar("INSERT INTO sessoes (doente_id, data, hora_inicio, duracao_min, profissional) "
                 "VALUES (%s, %s, %s, %s, %s)",
                 (1, time.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"), 0, "Profissional Teste"))


_bd_pronta = False


@app.before_request
def garantir_bd():
    # cria as tabelas na primeira chamada (só se já houver base de dados ligada)
    global _bd_pronta
    if not _bd_pronta and DATABASE_URL:
        iniciar_bd()
        _bd_pronta = True


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/saude")
def saude():
    return jsonify(estado="online", base_de_dados=bool(DATABASE_URL))


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

    executar(
        "INSERT INTO registos (sessao_id, timestamp, temperatura, fc, rmssd, "
        "emg_rms, fadiga_pct, zona, alerta_ativo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (d["sessao_id"], d["timestamp"], d["temperatura"], d["fc"], d["rmssd"],
         d["emg_rms"], d["fadiga_pct"], d["zona"], bool(d["alerta_ativo"])))
    return jsonify(ok=True), 201


@app.route("/api/ultimos/<int:sessao_id>")
def ultimos(sessao_id):
    linhas = executar(
        "SELECT * FROM registos WHERE sessao_id=%s ORDER BY id DESC LIMIT 60",
        (sessao_id,), fetch=True)
    return jsonify(linhas[::-1])


if __name__ == "__main__":
    app.run(debug=True)