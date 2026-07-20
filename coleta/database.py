import sqlite3
from typing import Optional
from coleta.config import BANCO_DADOS
from coleta.logger import logger

def get_connection() -> sqlite3.Connection:
    # 3. Timeout de 30s para evitar "database is locked" com Streamlit
    conn = sqlite3.connect(BANCO_DADOS, timeout=30.0)
    # 4. Ativação do modo WAL (Write-Ahead Logging) para concorrência Leitura/Escrita
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def inicializar_banco() -> None:
    """Cria tabelas, índices e habilita o modo WAL no SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela Legada de Processo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leitura (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                humidade REAL,
                temperatura REAL,
                data DATETIME
            )
        """)

        # Tabela de Eventos Operacionais (Confiabilidade)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coleta_evento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_execucao DATETIME DEFAULT (datetime('now', 'localtime')),
                duracao_ms REAL,
                ciclo_segundos REAL,
                status TEXT,
                http_code INTEGER,
                erro TEXT,
                temperatura REAL,
                humidade REAL
            )
        """)

        # 13. Tabela de Health Check da Infraestrutura
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_check (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
                cpu_usage_pct REAL,
                ram_usage_pct REAL,
                disk_free_gb REAL,
                db_size_mb REAL,
                wifi_signal_dbm INTEGER,
                status TEXT
            )
        """)

        # 5. Índices Estratégicos para Alta Performance de Query no Dashboard
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leitura_data ON leitura(data);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evento_timestamp ON coleta_evento(timestamp_execucao);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evento_status ON coleta_evento(status);")

        conn.commit()
    logger.info("Banco de dados SQLite inicializado com WAL, índices e tabelas operacionais.")

def salvar_leitura_processo(humidade: float, temperatura: float) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO leitura (humidade, temperatura, data) VALUES (?, ?, datetime('now', 'localtime'))",
            (humidade, temperatura)
        )
        conn.commit()

def salvar_evento_operacional(
    duracao_ms: float,
    ciclo_segundos: float,
    status: str,
    http_code: Optional[int] = 200,
    erro: Optional[str] = None,
    temp: Optional[float] = None,
    hum: Optional[float] = None
) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO coleta_evento (duracao_ms, ciclo_segundos, status, http_code, erro, temperatura, humidade)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (duracao_ms, ciclo_segundos, status, http_code, erro, temp, hum))
        conn.commit()