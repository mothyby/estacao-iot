import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# URLs e Chaves (com placeholders neutros)
ESP8266_URL = os.getenv("ESP8266_URL", "http://0.0.0.0/")
AIO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME", "")
AIO_KEY = os.getenv("ADAFRUIT_IO_KEY", "")

# Parâmetros Operacionais
INTERVALO_AMOSTRAGEM_SEG = float(os.getenv("INTERVALO_AMOSTRAGEM_SEG", "5.0"))
TIMEOUT_HTTP_SEG = float(os.getenv("TIMEOUT_HTTP_SEG", "5.0"))
BANCO_DADOS = os.getenv("BANCO_DADOS", "estacao_climatica.db")
LOG_FILE = os.getenv("LOG_FILE", "logs/coletor.log")

class StatusColeta(str, Enum):
    """Enumeração estrita para garantia de consistência dos KPIs de Confiabilidade."""
    OK = "OK"
    TIMEOUT = "TIMEOUT"
    HTTP_ERROR = "HTTP_ERROR"
    JSON_ERROR = "JSON_ERROR"
    INVALID_DATA = "INVALID_DATA"
    DATABASE_ERROR = "DATABASE_ERROR"