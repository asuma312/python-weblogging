import logging
import requests
from enum import Enum
import traceback
import inspect
from typing import Dict, Any
from datetime import datetime

class LogType(Enum):
    INFO = "INFO"
    WARNING = "WARNING"  
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    CRITICAL = "CRITICAL"
    ALL = "ALL"

class LogSQLClient:
    def __init__(self, base_url: str, username: str = None, password: str = None, token: str = None):
        """
        Inicializa o cliente LogSQL.
        
        Args:
            base_url: URL base do servidor LogSQL (ex: "http://localhost:1234")
            username: Nome de usuário para autenticação
            password: Senha para autenticação
            token: Token de autenticação (alternativa a username/password)
        """
        self.base_url = base_url.rstrip('/')+'/api/v1'
        self.token = token
        self.username = username
        self.password = password
        
        # Autenticar se credenciais forem fornecidas e não houver token
        if not self.token and self.username and self.password:
            self.authenticate()
    
    def authenticate(self) -> bool:
        """
        Autentica o cliente e obtém o token de acesso.
        
        Returns:
            bool: True se a autenticação for bem-sucedida, False caso contrário
        """
        try:
            response = requests.post(
                f"{self.base_url}/auth/request_token",
                json={"username": self.username, "password": self.password}
            )
            
            if response.status_code == 200:
                self.token = response.json().get("token")
                return True
            else:
                raise Exception("Erro de autenticação: " + str(response.status_code))
        except Exception as e:
            raise Exception(f"Erro ao autenticar: {e}") from e
    
    def insert_log(self, full_log:str) -> Dict[str, Any]:
        """
        Insere um log no servidor.
        
        Args:
            message: Mensagem do log
            log_type: Tipo do log
            function_name: Nome da função (opcional, será detectado automaticamente se não fornecido)
            
        Returns:
            Dict: Resposta do servidor
        """
        if not self.token:
            if not self.authenticate():
                return {"status": "error", "message": "Não autenticado"}

        
        try:
            response = requests.put(
                f"{self.base_url}/logs/insert_log",
                json={"log": full_log},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            return response.json()
        except Exception as e:
            raise Exception(f"Erro ao inserir log: {e}") from e


class LogSQLHandler(logging.Handler):
    """
    Handler de logging personalizado que envia logs para o servidor LogSQL.
    """
    
    def __init__(self, client: LogSQLClient, level=logging.NOTSET):
        """
        Inicializa o handler.
        
        Args:
            client: Cliente LogSQL configurado
            level: Nível mínimo de logging a ser processado
        """
        super().__init__(level)
        self.client = client
        
    def emit(self, record):
        """
        Envia o registro de log para o servidor LogSQL.
        
        Args:
            record: Objeto LogRecord do Python logging
        """
        log_type_map = {
            logging.DEBUG: LogType.DEBUG,
            logging.INFO: LogType.INFO,
            logging.WARNING: LogType.WARNING,
            logging.ERROR: LogType.ERROR,
            logging.CRITICAL: LogType.CRITICAL
        }
        
        try:
            self.client.insert_log(
                full_log=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} - {log_type_map.get(record.levelno, LogType.ALL).value} [{record.pathname}:{record.lineno} - {record.funcName}()] - {record.getMessage()}"
            )
        except Exception as e:
            raise Exception(f"Erro ao enviar log: {e}") from e


def setup_logger(
    name: str, 
    base_url: str = "http://localhost:1234",
    username: str = None, 
    password: str = None, 
    token: str = None,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Configura e retorna um logger com o LogSQLHandler.
    
    Args:
        name: Nome do logger
        base_url: URL do servidor LogSQL
        username: Nome de usuário para autenticação
        password: Senha para autenticação
        token: Token de autenticação (alternativa a username/password)
        level: Nível de logging
        
    Returns:
        logging.Logger: O logger configurado
    """
    client = LogSQLClient(base_url=base_url, username=username, password=password, token=token)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handler = LogSQLHandler(client=client, level=level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s [%(pathname)s:%(lineno)d - %(funcName)s()] - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
