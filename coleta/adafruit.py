import requests
from coleta.config import AIO_USERNAME, AIO_KEY
from coleta.logger import logger

def enviar_adafruit(feed: str, valor: float) -> None:
    if not AIO_USERNAME or not AIO_KEY:
        return

    url = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{feed}/data"
    headers = {"X-AIO-Key": AIO_KEY, "Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, json={"value": valor}, headers=headers, timeout=2.0)
        # 8. Garante validação de erro HTTP (ex: 401, 403, 500)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Falha na sincronização do feed '{feed}' com Adafruit IO: {e}")
