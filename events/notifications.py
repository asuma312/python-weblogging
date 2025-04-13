from flask_socketio import emit, join_room

def register_notification_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        join_room("uh")
        emit('user_id', {'uh': 'uh'})

    @socketio.on('notification')
    def handle_notification(data):
        message = data.get('message')
        emit('notification_response', {'message': f'Notificação recebida: {message}'}, broadcast=True)

    # Função para enviar notificação ao frontend de um usuário (sala) específico.
    def notify_user(uh, message):
        socketio.emit('notification_response', {'message': message}, room=uh)

    socketio.notify_user = notify_user
