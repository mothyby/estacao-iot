# 🌡️ Estação Meteorológica IoT

Sistema IoT para monitoramento ambiental desenvolvido com **Arduino Mega**, **ESP8266**, **Python** e **SQLite**, capaz de adquirir dados de sensores em tempo real, disponibilizá-los via HTTP/JSON, armazená-los localmente e apresentá-los em um dashboard interativo, com sincronização opcional para a nuvem utilizando **Adafruit IO**.

---

## 📌 Principais funcionalidades

- 🌡️ Aquisição de temperatura e umidade com sensor DHT11
- 🔌 Comunicação entre Arduino Mega e ESP8266 via Serial3 (UART)
- 🌐 Servidor HTTP embarcado no ESP8266
- 📦 API REST simples utilizando JSON
- 🐍 Coletor desenvolvido em Python
- 🗄️ Persistência dos dados em SQLite
- 📊 Dashboard interativo utilizando Streamlit + Plotly
- ☁️ Sincronização opcional com Adafruit IO
- ✅ Validação automática de leituras inválidas
- 🔄 Arquitetura desacoplada entre hardware e software

---

# 🏗 Arquitetura

```text
                 DHT11
                   │
                   ▼
           Arduino Mega 2560
             (Leitura do Sensor)
                   │
               UART (Serial3)
                   │
                   ▼
              ESP8266 Wi-Fi
         HTTP Server + JSON API
             │             │
             │             └──────────────► Adafruit IO
             │
             ▼
      Python Data Collector
             │
             ▼
           SQLite
             │
             ▼
    Streamlit + Plotly Dashboard
```

---

# 🛠 Tecnologias

## Hardware

- Arduino Mega 2560
- ESP8266 (RobotDyn integrado)
- Sensor DHT11

## Software

### Firmware

- Arduino IDE 2.x
- C++

### Backend

- Python 3
- Requests
- SQLite3
- Pandas

### Visualização

- Streamlit
- Plotly

### Sistema Operacional

- Ubuntu Linux
- VS Code

---

# 🚀 Como executar

## 1. Firmware

Clone o repositório

```bash
git clone https://github.com/mothyby/estacao-iot.git
cd estacao-iot
```

Copie o arquivo de configuração

```bash
cp config.h.example config.h
```

Configure:

- SSID
- Senha Wi-Fi
- Credenciais da Adafruit (opcional)

Grave:

- `mega_dht11_serial3.ino`
- `esp8266_servidor_dht.ino`

Configure os DIP Switches para comunicação Mega ↔ ESP8266.

---

## 2. Ambiente Python

```bash
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

Configure o ambiente

```bash
cp .env.example .env
```

Edite:

```
ESP8266_URL=

ADAFRUIT_USER=

ADAFRUIT_KEY=
```

Execute o coletor

```bash
python salvar_dados.py
```

---

## 3. Dashboard

```bash
streamlit run dashboard.py
```

Abra:

```
http://localhost:8501
```

---

<<<<<<< HEAD
# 📂 Estrutura do projeto

```text
estacao-iot/

├── firmware/
│   ├── mega_dht11_serial3.ino
│   └── esp8266_servidor_dht.ino
│
├── python/
│   ├── salvar_dados.py
│   ├── dashboard.py
│   └── requirements.txt
│
├── database/
│   └── estacao_climatica.db
│
├── docs/
│   ├── arquitetura.png
│   ├── dashboard.png
│   └── diario_engenharia.md
│
├── .env.example
├── config.h.example
└── README.md
```

---

# 📊 Dashboard

O sistema apresenta em tempo real:

- Temperatura atual
- Umidade atual
- Última leitura
- Histórico temporal
- Estatísticas do período
- Filtro de datas
- Descarte automático de leituras inválidas

---

# 🔍 Principais desafios resolvidos

Durante o desenvolvimento foram solucionados diversos problemas de integração:

- Comunicação Serial entre Mega e ESP8266
- Configuração dos DIP Switches RobotDyn
- Migração da arquitetura Serial para HTTP/JSON
- Sincronização entre firmware e coletor Python
- Tratamento de leituras inválidas
- Persistência em SQLite
- Integração com Adafruit IO
- Construção do dashboard em Streamlit

---

# 📈 Roadmap

## ✔ Versão 1.0

- [x] Comunicação Serial
- [x] HTTP/JSON
- [x] SQLite
- [x] Dashboard
- [x] Adafruit IO

## 🚧 Próximas versões

- [ ] MQTT
- [ ] Docker
- [ ] PostgreSQL
- [ ] FastAPI
- [ ] Testes automatizados
- [ ] CI/CD (GitHub Actions)
- [ ] Alertas via Telegram
- [ ] Deploy em Raspberry Pi

---

# 📄 Licença

Este projeto está licenciado sob a licença opensource

---

# 👨‍💻 Autor

**Cleber Gonçalves de Jesus**

Graduando em Engenharia de Controle e Automação.

Projeto desenvolvido como estudo prático de IoT, Sistemas Embarcados, Automação Industrial e Engenharia de Dados.
=======
Nenhuma licença aplicada 
(alteracao de licenca no README)
