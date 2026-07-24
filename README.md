Aqui está o conteúdo do **`README.md`** completo e atualizado dentro de uma caixa de código para que você possa copiar e colar diretamente no seu arquivo:

```markdown
# 🌡️ Estação Meteorológica & Gateway IoT de Confiabilidade V2

Sistema IoT de nível industrial para monitoramento ambiental e análise de confiabilidade de dados operacionais. Desenvolvido com **Arduino Mega**, **ESP8266**, **Python 3 (Arquitetura Modular)**, **SQLite (modo WAL)** e **Adafruit IO**, o sistema realiza aquisição em tempo real, tratamento de sanidade física, persistência otimizada, tagueamento de eventos operacionais e visualização executiva.

---

## 📌 Principais Funcionalidades

- 🌡️ **Aquisição Térmica e Higrométrica:** Leitura precisa de temperatura e umidade via sensor DHT11.
- 🔌 **Barramento Serial Integrado:** Comunicação robusta Arduino Mega ↔ ESP8266 via `Serial3` (UART).
- 🌐 **Edge HTTP/JSON Server:** Microservidor embarcado no ESP8266 expondo API REST padronizada.
- ⚙️ **Gateway Modular em Python (V2):** Arquitetura desacoplada por responsabilidades (`config`, `logger`, `database`, `collector`, `adafruit`).
- ⏱️ **Compensação Monotônica de Tempo:** Algoritmo no loop principal com `time.perf_counter()` para amostragem isoespaçada rigorosa.
- 🗄️ **SQLite de Alta Concorrência:** Banco configurado com suporte a modo **WAL (Write-Ahead Logging)**, timeouts de travamento e índices estratégicos de query.
- 📐 **Confiabilidade & Métricas Operacionais:** Registro de latência ($ms$), status HTTP, falhas de parse JSON e tagueamento por enums estritos (`StatusColeta`).
- 📝 **Log Rotativo Pré-configurado:** Handlers com retenção controlada de logs (`RotatingFileHandler`) para prevenção de saturação de disco.
- ☁️ **Sincronização em Nuvem:** Envio assíncrono/tolerante a falhas para o **Adafruit IO**.
- 📊 **Dashboard Industrial:** Visualização interativa e KPIs de processo via Streamlit + Plotly.

---

## 🏗 Arquitetura do Sistema

```text
                     DHT11 (Sensor)
                           │
                           ▼
                   Arduino Mega 2560
               (Processamento e Leitura)
                           │
                     UART (Serial3)
                           │
                           ▼
                    ESP8266 Wi-Fi
               (HTTP Server + JSON API)
                    │             │
                    │             └──────────────► Adafruit IO (Cloud)
                    │
                    ▼
          Python IoT Gateway (V2)
      ┌─────────────────────────────────┐
      │  main.py (Orquestrador)         │
      │  ├── coleta.config (Enums/.env) │
      │  ├── coleta.logger (Rotativo)   │
      │  ├── coleta.database (WAL)      │
      │  ├── coleta.collector (Loop)    │
      │  └── coleta.adafruit (API)      │
      └─────────────────────────────────┘
                    │
                    ▼
             SQLite (WAL + Índices)
                    │
                    ▼
          Streamlit + Plotly Dashboard

```

---

## 🛠 Stack Tecnológico

* **Hardware & Firmware:** Arduino Mega 2560, ESP8266 (RobotDyn integrado), DHT11, C/C++ (Arduino IDE 2.x).
* **Backend & Coleta (V2):** Python 3.11+, Requests, Python-Dotenv, Logging Nativo.
* **Banco de Dados:** SQLite3 (PRAGMA WAL, Indexes em `data`, `timestamp` e `status`).
* **Visualização & Analytics:** Streamlit, Plotly, Pandas.
* **Ambiente Executivo:** Ubuntu Linux, VS Code, Git/GitHub.

---

## 🛡️ Segurança e Gestão de Segredos (DevSecOps)

O repositório foi construído seguindo os padrões de segurança em desenvolvimento. **Nenhum dado sensível ou credencial de rede/API é versionado.**

### Arquivos Protegidos pelo `.gitignore`:

* `config.h` (Credenciais Wi-Fi do ESP8266)
* `.env` (Credenciais Adafruit IO e URLs locais)
* `*.db`, `*.db-wal`, `*.db-shm` (Bancos SQLite)
* `logs/` (Arquivos rotativos de log)
* `venv/` (Ambiente virtual Python)

---

## 📂 Estrutura do Repositório

```text
estacao-iot/
├── coleta/                     # Pacote Modular do Gateway Python (V2)
│   ├── __init__.py
│   ├── adafruit.py             # Sincronização e API Adafruit IO
│   ├── collector.py            # Execução de ciclos e validação física
│   ├── config.py               # Enumerações de status e variáveis de ambiente
│   ├── database.py             # DDL, DML, inicialização WAL e conexão SQLite
│   └── logger.py               # Handler de Logs Rotativos (Console + Arquivo)
├── logs/                       # Logs operacionais do Gateway (Ignorado pelo Git)
├── .env.example                # Template neutro para variáveis de ambiente
├── .gitignore                  # Regras estritas de segurança de código/dados
├── config.h.example            # Template neutro para Wi-Fi do C++
├── dashboard.py                # Dashboard executivo em Streamlit + Plotly
├── esp8266_servidor_dht.ino   # Firmware HTTP Server no ESP8266
├── mega_dht11_serial3.ino     # Firmware de leitura e envio UART no Arduino Mega
├── main.py                     # Entrypoint do Gateway IoT
├── README.md                   # Documentação oficial
└── requirements.txt            # Dependências das bibliotecas Python

```

---

## 🚀 Como Executar o Projeto

### 1. Firmware (C++)

1. Clone o repositório:
```bash
git clone [https://github.com/mothyby/estacao-iot.git](https://github.com/mothyby/estacao-iot.git)
cd estacao-iot

```


2. Crie o arquivo de credenciais da placa a partir do modelo:
```bash
cp config.h.example config.h

```


3. Abra e configure seu `SSID` e `PASSWORD` dentro do `config.h`.
4. Compile e grave os arquivos `.ino` em suas respectivas placas (Arduino Mega e ESP8266), atentando-se para a chave dos DIP Switches RobotDyn.

---

### 2. Backend / Gateway de Coleta (Python V2)

1. Crie e ative o ambiente virtual no Ubuntu:
```bash
python3 -m venv venv
source venv/bin/activate

```


2. Instale as dependências:
```bash
pip install -r requirements.txt

```


3. Configure as variáveis de ambiente:
```bash
cp .env.example .env

```


*Edite o `.env` preenchendo o IP atribuído ao seu ESP8266 e suas chaves do Adafruit IO.*
4. Inicie o Gateway de Coleta:
```bash
python main.py

```



---

### 3. Dashboard Interativo

Em outro terminal (com o `venv` ativo):

```bash
streamlit run dashboard.py

```

Acesse no seu navegador: `http://localhost:8501`

---

## 📈 Roadmap do Projeto

* [x] Arquitetura desacoplada Serial/UART ↔ HTTP/JSON
* [x] Refatoração Modular Python V2
* [x] Tolerância a falhas, Enums estritos e logs rotativos
* [x] Otimização SQLite (Modo WAL e Índices de consulta)
* [ ] Dashboard Interativo Streamlit
* [ ] Módulo de cálculo de MTBF e MTTR automatizado para o Dashboard
* [ ] Containerização da aplicação com Docker / Docker Compose
* [ ] Migração do protocolo HTTP para Broker MQTT local (Mosquitto)
* [ ] Alertas automatizados de desvio térmico via Telegram Bot API

---

## 👨‍💻 Autor
## Atividade de programação realizada por IA 

**Cleber Gonçalves de Jesus**

*Graduando em Engenharia de Controle e Automação*

*Graduando em Gestão da Produção Industrial*


```

```
