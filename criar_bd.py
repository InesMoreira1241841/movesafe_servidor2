import sqlite3
con = sqlite3.connect("movesafe.db")
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
con.commit()