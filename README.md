# 🌡️ Estação Meteorológica IoT — ESP8266 + Arduino Mega

Pipeline completo de aquisição, transmissão, persistência e visualização de
dados ambientais em tempo real, usando hardware embarcado, Wi-Fi, banco de
dados local e um dashboard interativo.

## Arquitetura

```
DHT11 (sensor)
   ↓
Arduino Mega (leitura + Serial3)
   ↓
ESP8266 (Wi-Fi + servidor HTTP/JSON)
   ↓
Python (coletor via requests)
   ↓
SQLite (persistência local)
   ↓
Streamlit + Plotly (dashboard)
   ↓ (opcional)
Adafruit IO (sincronização em nuvem)
```

## Hardware

- Arduino Mega 2560 (RobotDyn, com ESP8266 integrado)
- Sensor DHT11 (temperatura e umidade)

## Software

- Firmware: Arduino IDE 2.x, C++
- Coletor: Python 3, `requests`, `python-dotenv`
- Persistência: SQLite3
- Visualização: Streamlit, Plotly, Pandas

## Como rodar

### 1. Firmware do ESP8266 e Arduino Mega
1. Copie `config.h.example` para `config.h` e preencha com seu SSID/senha do Wi-Fi.
2. Grave `mega_dht11_serial3.ino` no Arduino Mega (DIP switch: modo de gravação do ATmega).
3. Grave `esp8266_servidor_dht.ino` no ESP8266 (DIP switch: modo de gravação do ESP8266).
4. Ajuste o DIP switch para o modo de operação conjunta (Mega + ESP8266 comunicando via Serial3).

### 2. Coletor Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edite o .env com a URL do seu ESP8266 e (opcional) credenciais da Adafruit IO

python3 salvar_dados.py
```

### 3. Dashboard
```bash
streamlit run dashboard.py
```

## Destaques técnicos

- Validação de sanidade em múltiplas camadas (firmware, coletor e dashboard)
  para descartar leituras corrompidas por reboot/ruído de boot.
- Comunicação Mega↔ESP8266 via UART física (Serial3), com dados servidos
  em JSON via HTTP — desacoplando o coletor do barramento serial.
- Dashboard com filtro de período, métricas em tempo real e médias diárias.

## Licença

MIT
