let unreadMessages = [];
let uh;

document.addEventListener('DOMContentLoaded', () => {
    const notificationBtn = document.getElementById("notification-btn");
    const notificationContainer = document.getElementById("notification-container");
    const notificationCountBadge = document.getElementById("notification-count");
    let notificationCount = 0;
    const socket = io();

    const updateNotificationBadge = () => {
        notificationCountBadge.innerText = notificationCount;
        if (notificationCount > 0) {
            notificationCountBadge.classList.remove("hidden");
        } else {
            notificationCountBadge.classList.add("hidden");
        }
    };

    function formatDate(dateStr) {
        const d = new Date(dateStr.replace(/-/g, '/'));
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const year = d.getFullYear().toString().slice(-2);
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        return `${month}/${day}/${year} ${hours}:${minutes}:${seconds}`;
    }

    const addNotificationMessage = (message, priority, date) => {
        const noNotElem = document.getElementById("no-notifications");
        if (noNotElem) {
            noNotElem.remove();
        }
        let bgColor = 'bg-green-500';
        let borderColor = 'border-green-700';
        if (priority === 'yellow') {
            bgColor = 'bg-yellow-500';
            borderColor = 'border-yellow-700';
        } else if (priority === 'red') {
            bgColor = 'bg-red-500';
            borderColor = 'border-red-700';
        } else if (priority == 'grey'){
            bgColor = 'bg-gray-500';
            borderColor = 'border-gray-700';
        }
        if(date){
            const formattedDate = formatDate(date);
            message += `<br/><small>${formattedDate}</small>`;
        }
        const messageContainer = document.createElement('div');
        messageContainer.className = `p-4 border-b ${borderColor} ${bgColor} text-white`;
        messageContainer.innerHTML = message;
        notificationContainer.insertBefore(messageContainer, notificationContainer.firstChild);
    };

    const handleNotificationBtnClick = () => {
        notificationCount = 0;
        updateNotificationBadge();
        notificationContainer.classList.toggle("hidden");
        if (!notificationContainer.classList.contains("hidden") && notificationContainer.childElementCount === 0) {
            let placeholder = document.createElement('div');
            placeholder.id = "no-notifications";
            placeholder.className = "p-4 text-gray-500";
            placeholder.innerHTML = "No notifications until now";
            notificationContainer.appendChild(placeholder);
        } else if (notificationContainer.classList.contains("hidden")) {
            const messages = notificationContainer.querySelectorAll('.bg-green-500, .bg-yellow-500, .bg-red-500');
            messages.forEach((message) => {
                message.classList.remove('bg-green-500', 'bg-yellow-500', 'bg-red-500');
                message.classList.add('bg-gray-500');
                message.classList.remove('border-green-700', 'border-yellow-700', 'border-red-700');
                message.classList.add('border-gray-700');
            })
        };

        window.sendReadMessages();
    };
    notificationBtn.addEventListener("click", handleNotificationBtnClick);

    const initSocket = async () => {
        socket.on('connect', async () => {
            // Reset da área de notificações e variáveis para evitar duplicação
            notificationContainer.innerHTML = "";
            unreadMessages = [];
            notificationCount = 0;
            updateNotificationBadge();

            try {
                const response = await fetch('/api/v1/frontend/get_uh');
                const data = await response.json();
                uh = data.uh;
                socket.emit('join_room', { uh: data.uh });
                console.log("User Hash:", data.uh);
            } catch (error) {
                console.error("Erro ao obter uh:", error);
            }
        });

        socket.on('notification_response', (data) => {
            notificationCount++;
            updateNotificationBadge();
            addNotificationMessage(data.message, data.priority || 'green', data.date);
            unreadMessages.push(data.id);
        });
        socket.on('silent_notification', (data) => {
            addNotificationMessage(data.message, data.priority || 'green', data.date);
        });
    };

    window.sendNotification = (message) => {
        socket.emit('notification', { message });
    };

    window.sendReadMessages = () => {
    if (unreadMessages.length > 0) {
            socket.emit('read_messages', { messages: unreadMessages, uh });
            unreadMessages = [];
            notificationCount = 0;
            updateNotificationBadge();
        }
    }

    initSocket();
});

