import time
import requests
from typing import Tuple
from coleta.config import ESP8266_URL, TIMEOUT_HTTP_SEG, StatusColeta
from coleta.logger import logger
from coleta.database import salvar_leitura_processo, salvar_evento_operacional
from coleta.adafruit import enviar_adafruit

def executar_ciclo_coleta(ciclo_segundos: float) -> float:
    # 7. Alta precisão com time.perf_counter()
    inicio = time.perf_counter()
    http_code = None
    
    try:
        resp = requests.get(ESP8266_URL, timeout=TIMEOUT_HTTP_SEG)
        latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)
        http_code = resp.status_code
        resp.raise_for_status()

        # 9. Tratamento específico contra JSON inválido/corrompido
        dados = resp.json()
        h = dados.get("humidade")
        t = dados.get("temperatura")

        # Filtro de Sanidade Física
        if h is not None and t is not None and 0 <= h <= 100 and -40 <= t <= 80:
            salvar_leitura_processo(h, t)
            salvar_evento_operacional(
                duracao_ms=latencia_ms,
                ciclo_segundos=ciclo_segundos,
                status=StatusColeta.OK.value,
                http_code=http_code,
                temp=t,
                hum=h
            )
            enviar_adafruit("temperatura", t)
            enviar_adafruit("umidade", h)
            logger.info(f"Coleta OK | Latência: {latencia_ms}ms | H: {h}% | T: {t}°C")
        else:
            salvar_evento_operacional(
                duracao_ms=latencia_ms,
                ciclo_segundos=ciclo_segundos,
                status=StatusColeta.INVALID_DATA.value,
                http_code=http_code,
                erro=f"Dados fora da faixa física: {dados}"
            )
            logger.warning(f"Leitura rejeitada por sanidade física: {dados}")

    except ValueError as e: # Captura JSONDecodeError
        latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)
        salvar_evento_operacional(
            duracao_ms=latencia_ms,
            ciclo_segundos=ciclo_segundos,
            status=StatusColeta.JSON_ERROR.value,
            http_code=http_code,
            erro=f"Falha de parse do JSON: {e}"
        )
        logger.error(f"Erro ao decodificar JSON do ESP8266: {e}")

    except requests.exceptions.Timeout:
        latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)
        salvar_evento_operacional(
            duracao_ms=latencia_ms,
            ciclo_segundos=ciclo_segundos,
            status=StatusColeta.TIMEOUT.value,
            http_code=http_code,
            erro="Timeout na requisição HTTP"
        )
        logger.error(f"Timeout na conexão com ESP8266 ({ESP8266_URL})")

    except requests.exceptions.RequestException as e:
        latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)
        salvar_evento_operacional(
            duracao_ms=latencia_ms,
            ciclo_segundos=ciclo_segundos,
            status=StatusColeta.HTTP_ERROR.value,
            http_code=http_code,
            erro=str(e)
        )
        logger.error(f"Erro de comunicação com ESP8266: {e}")

    return round(time.perf_counter() - inicio, 4)
