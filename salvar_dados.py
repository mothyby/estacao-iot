import sqlite3
import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Le variaveis do arquivo .env (nunca commitado)

URL = os.environ["ESP8266_URL"]
AIO_USERNAME = os.environ["ADAFRUIT_IO_USERNAME"]
AIO_KEY = os.environ["ADAFRUIT_IO_KEY"]

INTERVALO_SEGUNDOS = 5


def enviar_adafruit(feed, valor):
    url = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{feed}/data"
    headers = {"X-AIO-Key": AIO_KEY, "Content-Type": "application/json"}
    try:
        requests.post(url, json={"value": valor}, headers=headers, timeout=2)
    except requests.exceptions.RequestException:
        pass  # Sincronizacao com a nuvem e melhor-esforco; nao trava a coleta local


def coletar():
    conn = sqlite3.connect("estacao_climatica.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS leitura
           (id INTEGER PRIMARY KEY AUTOINCREMENT,
            humidade REAL,
            temperatura REAL,
            data DATETIME)"""
    )
    conn.commit()

    print(f"Coletando de {URL} a cada {INTERVALO_SEGUNDOS}s. Ctrl+C para parar.")

    try:
        while True:
            try:
                resp = requests.get(URL, timeout=5)
                resp.raise_for_status()
                dados = resp.json()

                h = dados.get("humidade")
                t = dados.get("temperatura")

                # Validacao de sanidade (faixa fisica plausivel do DHT11)
                if h is not None and t is not None and 0 <= h <= 100 and -40 <= t <= 80:
                    cursor.execute(
                        "INSERT INTO leitura (humidade, temperatura, data) "
                        "VALUES (?, ?, datetime('now', 'localtime'))",
                        (h, t),
                    )
                    conn.commit()
                    enviar_adafruit("temperatura", t)
                    enviar_adafruit("umidade", h)
                    print(f"-> Sucesso! H={h}% | T={t}C")
                else:
                    print(f"Dados fora da faixa plausivel, descartado: {dados}")

            except requests.exceptions.RequestException as e:
                print(f"Erro de conexao com o ESP8266 ({URL}): {e}")

            time.sleep(INTERVALO_SEGUNDOS)

    except KeyboardInterrupt:
        print("\nEncerrando coleta...")
    finally:
        conn.close()


if __name__ == "__main__":
    coletar()
