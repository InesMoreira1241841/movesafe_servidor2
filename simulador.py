import sys
import time
import random
import requests

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000"
CHAVE = sys.argv[2] if len(sys.argv) > 2 else "chave-de-teste"

while True:
    zona = random.choice(["segura", "segura", "limite", "sobrecarga"])
    dados = {
        "sessao_id": 1,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "temperatura": round(random.uniform(35.5, 38.0), 1),
        "fc": random.randint(60, 150),
        "rmssd": round(random.uniform(10, 60), 1),
        "emg_rms": round(random.uniform(0.1, 0.9), 2),
        "fadiga_pct": round(random.uniform(0, 100), 1),
        "zona": zona,
        "alerta_ativo": zona == "sobrecarga",
    }
    r = requests.post(URL + "/api/dados", json=dados, headers={"X-API-Key": CHAVE})
    print(r.status_code, dados["zona"])
    time.sleep(1)