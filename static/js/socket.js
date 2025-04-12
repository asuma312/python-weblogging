// Cliente WebSocket para interagir com o backend

class LogSQLClient {
    constructor(url) {
        this.socket = io(url);
        this.sessionId = this.generateSessionId();
        this.setupEventListeners();
    }

    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }

    setupEventListeners() {
        this.socket.on('connect', () => {
            console.log('Conectado ao servidor WebSocket');
        });

        this.socket.on('disconnect', () => {
            console.log('Desconectado do servidor WebSocket');
        });

        this.socket.on('error', (data) => {
            console.error('Erro:', data.message);
        });
    }

    // Autenticação
    createAccount(username, password, callback) {
        this.socket.emit('create_account', { username, password });
        this.socket.once('create_account_response', callback);
    }

    login(username, password, callback) {
        this.socket.emit('login', { 
            username, 
            password,
            session_id: this.sessionId 
        });
        this.socket.once('login_response', callback);
    }

    forgotPassword(username, passkey, newPassword, callback) {
        this.socket.emit('forgot_password', { 
            username, 
            passkey, 
            new_password: newPassword 
        });
        this.socket.once('forgot_password_response', callback);
    }

    logout(callback) {
        this.socket.emit('logout', { session_id: this.sessionId });
        this.socket.once('logout_response', callback);
    }

    // Operações de Logs
    insertLog(log, callback) {
        this.socket.emit('insert_log', { 
            log,
            session_id: this.sessionId
        });
        this.socket.once('insert_log_response', callback);
    }

    insertMultipleLogs(logs, callback) {
        this.socket.emit('insert_multiple_logs', { 
            logs,
            session_id: this.sessionId
        });
        this.socket.once('insert_multiple_logs_response', callback);
    }

    selectLogs(options, callback) {
        this.socket.emit('select_logs', { 
            ...options,
            session_id: this.sessionId
        });
        this.socket.once('select_logs_response', callback);
    }

    getLog(logId, callback) {
        this.socket.emit('get_log', { 
            log_id: logId,
            session_id: this.sessionId
        });
        this.socket.once('get_log_response', callback);
    }
}

// Exemplo de uso:
// const client = new LogSQLClient('http://localhost:1234');
// client.login('username', 'password', (response) => {
//     if (response.status === 'success') {
//         console.log('Login bem-sucedido!');
//         client.insertLog({...}, (response) => {
//             console.log('Log inserido:', response);
//         });
//     }
// });
