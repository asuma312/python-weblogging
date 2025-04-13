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
