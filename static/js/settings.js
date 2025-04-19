function deleteLogDB(dbName) {
        if (!dbName) {
            showErrorModal("Select a database to delete.", "Warning");
            return;
        }

        showConfirmModal(
            `Are you sure you want to delete the database "${dbName}"? This action cannot be undone.`,
            () => {
                fetch(`/api/v1/logs/delete_logdb`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        log_name: dbName
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showSuccessModal('Database successfully deleted!');
                        const selectElement = document.getElementById('logDbSelect');
                        for (let i = 0; i < selectElement.options.length; i++) {
                            if (selectElement.options[i].value === dbName) {
                                selectElement.remove(i);
                                break;
                            }
                        }
                        selectElement.selectedIndex = 0;
                    } else {
                        showErrorModal(`Error deleting: ${data.message || 'An unknown error occurred'}`);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showErrorModal('An error occurred while trying to delete the database.');
                });
            },
            null,
            "Delete Confirmation"
        );
    }

    document.addEventListener('DOMContentLoaded', function() {

        document.getElementById('emailForm').style.display = 'none';
        initNotificationDropdown();
        updateAddEmailButtonState();
    });

    function showAddEmailForm() {
        const form = document.getElementById('emailForm');
        const formTitle = document.getElementById('emailFormTitle');
        const submitBtnText = document.getElementById('submitBtnText');
        const emailInput = document.getElementById('emailInput');

        document.getElementById('oldEmail').value = '';
        emailInput.value = '';

        const selectedNotifications = document.getElementById('selected-notifications');
        selectedNotifications.innerHTML = '';
        const hiddenSelect = document.getElementById('notificationsSelect');
        for (let i = 0; i < hiddenSelect.options.length; i++) {
             hiddenSelect.options[i].selected = false;
        }

        formTitle.textContent = 'Add New Email';
        submitBtnText.textContent = 'Add Email';

        form.style.display = 'block';
        emailInput.focus();
    }

    function getNotificationTagClass(notification) {
        switch(notification.toLowerCase()) {
            case 'error': return 'bg-red-100 text-red-800 text-xs px-2 py-0.5 rounded-full cursor-pointer';
            default: return 'bg-gray-100 text-gray-800 text-xs px-2 py-0.5 rounded-full cursor-pointer';
        }
    }

    function showEditEmailForm(email, notifications) {
        const form = document.getElementById('emailForm');
        const formTitle = document.getElementById('emailFormTitle');
        const submitBtnText = document.getElementById('submitBtnText');
        const emailInput = document.getElementById('emailInput');
        const oldEmail = document.getElementById('oldEmail');

        emailInput.value = email;
        oldEmail.value = email;

        formTitle.textContent = 'Edit Email Address';
        submitBtnText.textContent = 'Save Changes';

        const selectedContainer = document.getElementById('selected-notifications');
        selectedContainer.innerHTML = '';
                console.log('Notifications:', notifications);

        if (notifications) {
            notifications.split(',').forEach(n => {
                n = n.trim();
                if (n) {
                    const tag = document.createElement('span');
                    tag.dataset.value = n;
                    tag.className = getNotificationTagClass(n);
                    tag.textContent = n;
                    tag.addEventListener('click', function() {
                        this.remove();
                        const hiddenSelect = document.getElementById('notificationsSelect');
                        const tags = selectedContainer.querySelectorAll('[data-value]');
                        const selectedValues = Array.from(tags).map(t => t.dataset.value);
                        Array.from(hiddenSelect.options).forEach(opt => {
                            opt.selected = selectedValues.includes(opt.value);
                        });
                    });
                    selectedContainer.appendChild(tag);
                }
            });

            const hiddenSelect = document.getElementById('notificationsSelect');
            const tags = selectedContainer.querySelectorAll('[data-value]');
            const selectedValues = Array.from(tags).map(t => t.dataset.value);
            Array.from(hiddenSelect.options).forEach(opt => {
                opt.selected = selectedValues.includes(opt.value);
            });
        }

        form.style.display = 'block';
        emailInput.focus();
    }

    function cancelEmailForm() {
        document.getElementById('emailForm').style.display = 'none';
    }

    function submitEmail() {
        const emailInput = document.getElementById('emailInput');
        const oldEmail = document.getElementById('oldEmail').value;
        const newEmail = emailInput.value.trim();

        if (!newEmail) {
            showErrorModal("Email address cannot be empty.", "Validation Error");
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(newEmail)) {
            showErrorModal("Please enter a valid email address.", "Validation Error");
            return;
        }

        if (!oldEmail) {
            const existingEmail = document.querySelector(`[data-email="${newEmail}"]`);
            if (existingEmail) {
                showErrorModal("O email já está cadastrado.", "Atenção");
                return;
            }
        }

        const hiddenSelect = document.getElementById('notificationsSelect');
        const notifications = Array.from(hiddenSelect.options)
                                  .filter(option => option.selected)
                                  .map(option => option.value);

        if (oldEmail) {
            editEmailRequest(oldEmail, newEmail, notifications);
        } else {
            addEmailRequest(newEmail, notifications);
        }
    }

    function addEmailRequest(email, notifications) {
        fetch(`/api/v1/frontend/add_email`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email, notifications: notifications })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showSuccessModal('Email successfully added!');

                const emailList = document.getElementById('emailList');

                if (emailList.innerHTML.includes('No emails added')) {
                    emailList.innerHTML = '';
                }

                const emailElement = document.createElement('div');
                emailElement.className = 'p-3 flex justify-between items-center hover:bg-gray-50';
                emailElement.dataset.email = email;
                emailElement.innerHTML = `
                    <span class="text-gray-700">${email}</span>
                    <div class="flex space-x-2">
                        <button onclick="showEditEmailForm('${email}', '${notifications.join(",")}')" class="text-blue-600 hover:text-blue-800">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                        </button>
                        <button onclick="deleteEmail('${email}')" class="text-red-600 hover:text-red-800">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    </div>
                `;

                emailList.appendChild(emailElement);

                cancelEmailForm();
                updateAddEmailButtonState();
            } else {
                showErrorModal(`Error adding email: ${data.message || 'An unknown error occurred'}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorModal('An error occurred while trying to add the email.');
        });
    }

    function editEmailRequest(oldEmail, newEmail, notifications) {
        fetch(`/api/v1/frontend/edit_email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                old_email: oldEmail,
                new_email: newEmail,
                notifications: notifications
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showSuccessModal('Email successfully updated!');

                const emailElements = document.querySelectorAll(`[data-email="${oldEmail}"]`);
                emailElements.forEach(el => {
                    el.dataset.email = newEmail;

                    el.querySelector('span').textContent = newEmail;

                    el.dataset.notifications = notifications.join(',');

                    const [editBtn, deleteBtn] = el.querySelectorAll('button');
                    editBtn.setAttribute('onclick', `showEditEmailForm('${newEmail}', '${notifications.join(",")}')`);
                    deleteBtn.setAttribute('onclick', `deleteEmail('${newEmail}')`);

                    const notifContainer = el.querySelector('div.flex.flex-wrap');
                    if (notifContainer) {
                        notifContainer.innerHTML = '';
                        notifications.forEach(n => {
                            const tag = document.createElement('span');
                            tag.className = getNotificationTagClass(n);
                            tag.textContent = n;
                            notifContainer.appendChild(tag);
                        });
                    }
                });

                cancelEmailForm();
            } else {
                showErrorModal(`Error updating email: ${data.message || 'An unknown error occurred'}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorModal('An error occurred while trying to update the email.');
        });
    }

    function deleteEmail(email) {
        showConfirmModal(
            `Are you sure you want to delete the email "${email}"?`,
            () => {
                fetch(`/api/v1/frontend/delete_email`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email: email })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showSuccessModal('Email successfully deleted!');

                        const emailElements = document.querySelectorAll(`[data-email="${email}"]`);
                        emailElements.forEach(el => {
                            el.remove();
                        });

                        const emailList = document.getElementById('emailList');
                        if (emailList.children.length === 0) {
                            emailList.innerHTML = '<div class="p-4 text-center text-gray-500">No emails added</div>';
                        }
                        updateAddEmailButtonState();
                    } else {
                        showErrorModal(`Error deleting email: ${data.message || 'An unknown error occurred'}`);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showErrorModal('An error occurred while trying to delete the email.');
                });
            },
            null,
            "Delete Confirmation"
        );
    }

    function initNotificationDropdown() {
        const dropdownBtn = document.getElementById('notification-dropdown-btn');
        const dropdown = document.getElementById('notification-dropdown');
        const selectedContainer = document.getElementById('selected-notifications');
        const hiddenSelect = document.getElementById('notificationsSelect');

        dropdownBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdown.classList.toggle('hidden');
        });

        const notificationOptions = dropdown.querySelectorAll('.notification-option');
        notificationOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const value = this.dataset.value;

                if (!selectedContainer.querySelector(`[data-value="${value}"]`)) {
                    const tag = document.createElement('span');
                    tag.dataset.value = value;
                    tag.className = getNotificationTagClass(value);
                    tag.textContent = value;
                    tag.addEventListener('click', function() {
                        this.remove();
                        updateHiddenSelect();
                    });
                    selectedContainer.appendChild(tag);
                }
                updateHiddenSelect();
                dropdown.classList.add('hidden');
            });
        });

        function updateHiddenSelect() {
            const tags = selectedContainer.querySelectorAll('[data-value]');
            const selectedValues = Array.from(tags).map(tag => tag.dataset.value);
            Array.from(hiddenSelect.options).forEach(opt => {
                opt.selected = selectedValues.includes(opt.value);
            });
        }

        document.addEventListener('click', function(event) {
            if(!dropdown.contains(event.target) && event.target !== dropdownBtn) {
                dropdown.classList.add('hidden');
            }
        });
    }

    function updateAddEmailButtonState() {
        const emailList = document.getElementById('emailList');
        const addEmailBtn = document.getElementById('addEmailBtn');
        const emails = emailList.querySelectorAll('[data-email]');
        if(emails.length >= 2){
            addEmailBtn.disabled = true;
            addEmailBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
            addEmailBtn.classList.add('bg-gray-400', 'cursor-not-allowed');
        } else {
            addEmailBtn.disabled = false;
            addEmailBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
            addEmailBtn.classList.add('bg-green-600', 'hover:bg-green-700');
        }
    }