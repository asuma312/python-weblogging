document.addEventListener('DOMContentLoaded', () => {
    const notificationBtn = document.getElementById("notification-btn");
    const notificationContainer = document.getElementById("notification-container");

    notificationBtn.addEventListener("click", () => {
        notificationContainer.classList.toggle("hidden");
    });

    const socket = io();

    window.sendNotification = function(message) {
        socket.emit('notification', { message: message });
    }

    socket.on('notification_response', (data) => {
        notificationContainer.innerHTML = `<div class="p-4">${data.message}</div>`;
        notificationContainer.classList.remove("hidden");
    });

    // Nova função para obter o "uh" via HTTP GET
    fetch('/api/v1/frontend/get_uh')
        .then(response => response.json())
        .then(data => {
            console.log("User Hash:", data.uh);
        })
        .catch(error => console.error("Erro ao obter uh:", error));
});

