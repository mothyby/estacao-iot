import time
from coleta.config import INTERVALO_AMOSTRAGEM_SEG
from coleta.logger import logger
from coleta.database import inicializar_banco
from coleta.collector import executar_ciclo_coleta

def main() -> None:
    logger.info("==================================================")
    logger.info("Iniciando Gateway de Coleta e Confiabilidade IoT")
    logger.info("==================================================")
    
    inicializar_banco()

    ultimo_inicio = time.perf_counter()

    try:
        while True:
            inicio_ciclo = time.perf_counter()
            ciclo_real_decorrido = round(inicio_ciclo - ultimo_inicio, 3)
            
            # 12. Envia a medição do intervalo real entre ciclos para persistência
            duracao_execucao = executar_ciclo_coleta(
                ciclo_segundos=ciclo_real_decorrido if ciclo_real_decorrido < 100 else INTERVALO_AMOSTRAGEM_SEG
            )
            
            ultimo_inicio = inicio_ciclo

            # Algoritmo de Compensação Monotônica de Tempo
            tempo_espera = INTERVALO_AMOSTRAGEM_SEG - duracao_execucao
            if tempo_espera > 0:
                time.sleep(tempo_espera)
            else:
                logger.warning(f"Ciclo estourou o intervalo amostragem! Duração da coleta: {duracao_execucao:.2f}s")

    except KeyboardInterrupt:
        logger.info("Encerrando gateway de coleta via comando do usuário (Ctrl+C)...")

if __name__ == "__main__":
    main()
