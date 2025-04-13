import logging
import sys
import os

import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyweblog.SDK_WS.main import setup_ws_logger

logger = setup_ws_logger(
    name="exemplo_app_ws",
    username="test2",
    password="test",
    level=logging.DEBUG
)
if __name__ == '__main__':
    logger.debug("Isto é uma mensagem de debug via WebSocket")
    time.sleep(1)
    logger.info("Aplicação iniciada via WebSocket")
    time.sleep(1)
    logger.warning("Aviso: recurso está quase esgotado (WebSocket)")
    time.sleep(1)
    logger.error("Erro ao processar arquivo (WebSocket)")
    time.sleep(1)


