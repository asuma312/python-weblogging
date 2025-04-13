import logging
import socketio
import time
from enum import Enum
import uuid
from datetime import datetime
from typing import Dict, Any

class LogType(Enum):
    INFO = "INFO"
    WARNING = "WARNING"  
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    CRITICAL = "CRITICAL"
    ALL = "ALL"

class LogSQLWSClient:
    def __init__(self, server_url: str, username: str = None, password: str = None, token: str = None, log_name = 'default'):
        """
        Inicializa o cliente WebSocket para LogSQL.
        
        Args:
            server_url: URL do servidor LogSQL (ex: "http://localhost:1234")
            username: Nome de usuário para autenticação
            password: Senha para autenticação
            token: Token de autenticação (alternativa a username/password)
        """
        self.server_url = server_url.rstrip('/')
        self.token = token
        self.username = username
        self.password = password
        self.log_name = log_name
        self.session_id = str(uuid.uuid4())
        
        self.sio = socketio.Client()
        self.connected = False
        self.responses = {}
        
        self._register_handlers()
        
        try:
            self.sio.connect(self.server_url)
            self.connected = True
            
            if not self.token and self.username and self.password:
                self.authenticate()
                
        except Exception as e:
            raise Exception(f"Erro ao conectar ao servidor: {e}")

    def _register_handlers(self):
        """Registra os manipuladores de eventos Socket.IO"""
        
        @self.sio.on('connect')
        def on_connect():
            print(f"Conectado ao servidor {self.server_url}")
            self.connected = True
            
        @self.sio.on('disconnect')
        def on_disconnect():
            print("Desconectado do servidor")
            self.connected = False
            
        @self.sio.on('login_response')
        def on_login_response(data):
            self.responses['login'] = data
            if data.get('status') == 'success':
                self.token = data.get('token')
            
        @self.sio.on('create_account_response')
        def on_create_account_response(data):
            self.responses['create_account'] = data
            
        @self.sio.on('insert_log_response')
        def on_insert_log_response(data):
            self.responses['insert_log'] = data
            
        @self.sio.on('insert_multiple_logs_response')
        def on_insert_multiple_logs_response(data):
            self.responses['insert_multiple_logs'] = data
            
        @self.sio.on('select_logs_response')
        def on_select_logs_response(data):
            self.responses['select_logs'] = data
            
        @self.sio.on('get_log_response')
        def on_get_log_response(data):
            self.responses['get_log'] = data
            
    def _wait_for_response(self, event_name: str, timeout: int = 5) -> Dict[str, Any]:
        """
        Aguarda a resposta de um evento específico.
        
        Args:
            event_name: Nome do evento para aguardar resposta
            timeout: Tempo máximo de espera em segundos
            
        Returns:
            Dict: Dados de resposta do evento
        """
        start_time = time.time()
        while event_name not in self.responses and time.time() - start_time < timeout:
            time.sleep(0.1)
            
        if event_name not in self.responses:
            return {"status": "error", "message": f"Timeout esperando resposta para {event_name}"}
            
        response = self.responses[event_name]
        del self.responses[event_name]
        return response
    
    def create_account(self, username: str, password: str) -> Dict[str, Any]:
        """
        Cria uma nova conta de usuário.
        
        Args:
            username: Nome de usuário
            password: Senha
            
        Returns:
            Dict: Resposta do servidor
        """
        if not self.connected:
            return {"status": "error", "message": "Não conectado ao servidor"}
        
        self.sio.emit('create_account', {
            'username': username,
            'password': password
        })
        
        return self._wait_for_response('create_account')
    
    def authenticate(self) -> bool:
        """
        Autentica o cliente e obtém o token de acesso.
        
        Returns:
            bool: True se a autenticação for bem-sucedida, False caso contrário
        """
        if not self.connected:
            return False
            
        if not self.username or not self.password:
            return False
            
        self.sio.emit('login', {
            'username': self.username,
            'password': self.password,
            'session_id': self.session_id
        })
        
        response = self._wait_for_response('login')
        if response.get('status') == 'success':
            self.token = response.get('token')
            return True
        raise Exception("Falha na autenticação")
    
    def logout(self) -> Dict[str, Any]:
        """
        Desconecta o usuário atual.
        
        Returns:
            Dict: Resposta do servidor
        """
        if not self.connected:
            return {"status": "error", "message": "Não conectado ao servidor"}
            
        self.sio.emit('logout', {'session_id': self.session_id})
        
        # Limpar credenciais
        self.token = None
        
        return {"status": "success", "message": "Logout realizado"}
    
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
        if not self.connected:
            return {"status": "error", "message": "Não conectado ao servidor"}
            
        if not self.token:
            if not self.authenticate():
                return {"status": "error", "message": "Não autenticado"}
                

        self.sio.emit('insert_log', {
            'session_id': self.session_id,
            'log': full_log,
            'log_name': self.log_name,
        })
        
        r = self._wait_for_response('insert_log')
        return r


    
    def disconnect(self):
        """Desconecta do servidor"""
        if self.connected:
            self.sio.disconnect()
            self.connected = False

    #fazer logout ao dar exit
    def __del__(self):
        """Desconecta do servidor ao deletar o objeto"""
        if self.connected:
            self.logout()
            self.sio.disconnect()
            self.connected = False


class LogSQLWSHandler(logging.Handler):
    """
    Handler de logging personalizado que envia logs para o servidor LogSQL via WebSocket.
    """
    
    def __init__(self, client: LogSQLWSClient, level=logging.NOTSET):
        """
        Inicializa o handler.
        
        Args:
            client: Cliente LogSQLWS configurado
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
            raise Exception(f"Erro ao enviar log para o servidor: {e}")


def setup_ws_logger(
    name: str, 
    server_url: str = "https://pythonweblog.com",
    username: str = None, 
    password: str = None, 
    token: str = None,
    level: int = logging.INFO,
        log_name:str = 'default'
) -> logging.Logger:
    """
    Configura e retorna um logger com o LogSQLWSHandler.
    
    Args:
        name: Nome do logger
        server_url: URL do servidor LogSQL
        username: Nome de usuário para autenticação
        password: Senha para autenticação
        token: Token de autenticação (alternativa a username/password)
        level: Nível de logging
        
    Returns:
        logging.Logger: O logger configurado
    """
    client = LogSQLWSClient(server_url=server_url, username=username, password=password, token=token, log_name=log_name)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handler = LogSQLWSHandler(client=client, level=level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
