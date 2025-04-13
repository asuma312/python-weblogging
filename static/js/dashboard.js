const Dashboard = {

    urlUtils: {

        updateUrlParam: (paramName, value) => {
            const url = new URL(window.location.href);
            const params = url.searchParams;

            if (value && value !== '') {
                params.set(paramName, value);
            } else {
                params.delete(paramName);
            }

            url.search = params.toString();
            window.location.href = url.toString();
        },

        getUrlParam: (paramName) => {
            return new URL(window.location.href).searchParams.get(paramName);
        }
    },

    navigation: {
        selectLog: (selectObj) => {
            Dashboard.urlUtils.updateUrlParam("log", selectObj.value.trim());
        },

        gotoNextPage: () => {
            const actualPage = parseInt(document.getElementById("actualPage").innerText) + 1;
            Dashboard.urlUtils.updateUrlParam("page", actualPage);
            localStorage.setItem("scrollToLocButtons", "true");
        },

        gotoPrevPage: () => {
            const actualPage = parseInt(document.getElementById("actualPage").innerText) - 1;
            Dashboard.urlUtils.updateUrlParam("page", actualPage);
            localStorage.setItem("scrollToLocButtons", "true");
        }
    },

    filterManager: {

        init: () => {
            const dropdownBtn = document.getElementById('type-dropdown-btn');
            const dropdown = document.getElementById('type-dropdown');
            const selectedTypesContainer = document.getElementById('selected-types');

            if (dropdownBtn) {
                dropdownBtn.addEventListener('click', () => {
                    dropdown.classList.toggle('hidden');
                });
            }

            document.addEventListener('click', (event) => {
                if (!event.target.closest('#type-dropdown') && 
                    !event.target.closest('#type-dropdown-btn') && 
                    dropdown) {
                    dropdown.classList.add('hidden');
                }
            });

            if (dropdown) {
                dropdown.addEventListener('click', (event) => {
                    const option = event.target.closest('.type-option');
                    if (option) {
                        const value = option.getAttribute('data-value');
                        Dashboard.filterManager.addTypeTag(value);
                        dropdown.classList.add('hidden');
                    }
                });
            }

            if (selectedTypesContainer) {
                selectedTypesContainer.addEventListener('click', (event) => {
                    if (event.target.closest('button')) {
                        const tag = event.target.closest('.type-tag');
                        if (tag) {
                            tag.remove();
                            Dashboard.filterManager.updateHiddenSelect();
                        }
                    }
                });
            }

            Dashboard.filterManager.initializeSelectedTypes();
        },

        initializeSelectedTypes: () => {
            const types = Dashboard.urlUtils.getUrlParam('types');

            if (types) {
                const typeArray = types.split(',');
                typeArray.forEach(type => {
                    Dashboard.filterManager.addTypeTag(type, false);
                });
            }
        },

        addTypeTag: (value, updateSelect = true) => {
            const selectedTypesContainer = document.getElementById('selected-types');
            const typesSelect = document.getElementById('typesSelect');

            if (value === 'all') {

                while (selectedTypesContainer.firstChild) {
                    selectedTypesContainer.removeChild(selectedTypesContainer.firstChild);
                }

                if (typesSelect) {
                    Array.from(typesSelect.options).forEach(option => {
                        if (option.value !== 'all') {
                            Dashboard.filterManager.addTypeTag(option.value, false);
                        }
                    });
                }

                if (updateSelect) {
                    Dashboard.filterManager.updateHiddenSelect();
                }

                return;
            }

            if (document.querySelector(`.type-tag[data-value="${value}"]`)) {
                return;
            }

            const tagColors = {
                'info': 'bg-blue-100 text-blue-800',
                'warning': 'bg-yellow-100 text-yellow-800',
                'error': 'bg-red-100 text-red-800',
                'debug': 'bg-gray-100 text-gray-800',
                'critical': 'bg-purple-100 text-purple-800',
                'success': 'bg-green-100 text-green-800',
                'failure': 'bg-orange-100 text-orange-800',
                'all': 'bg-indigo-100 text-indigo-800'
            };

            const colorClass = tagColors[value] || 'bg-gray-100 text-gray-800';

            const tag = document.createElement('div');
            tag.className = `type-tag ${colorClass} rounded-full py-1 px-3 text-sm flex items-center`;
            tag.setAttribute('data-value', value);
            tag.innerHTML = `
                ${value}
                <button type="button" class="ml-1 text-xs font-medium">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            `;

            selectedTypesContainer.appendChild(tag);

            if (updateSelect) {
                Dashboard.filterManager.updateHiddenSelect();
            }
        },

        updateHiddenSelect: () => {
            const typesSelect = document.getElementById('typesSelect');
            const selectedTypesContainer = document.getElementById('selected-types');

            if (!typesSelect) return;

            Array.from(typesSelect.options).forEach(option => {
                option.selected = false;
            });

            const tags = selectedTypesContainer.querySelectorAll('.type-tag');
            tags.forEach(tag => {
                const value = tag.getAttribute('data-value');
                const option = Array.from(typesSelect.options).find(opt => opt.value === value);
                if (option) {
                    option.selected = true;
                }
            });
        },

        applyFilters: () => {
            const url = new URL(window.location.href);
            const params = url.searchParams;

            const selectedTags = document.querySelectorAll('.type-tag');
            const selectedTypes = Array.from(selectedTags).map(tag => tag.getAttribute('data-value'));

            if (selectedTypes.length > 0) {
                params.set("types", selectedTypes.join(','));
            } else {
                params.delete("types");
            }

            const functionName = document.getElementById("functionNameInput").value.trim();
            functionName ? params.set("function_name", functionName) : params.delete("function_name");

            const dataStart = document.getElementById("dataStartInput").value;
            dataStart ? params.set("data_start", dataStart.replace('T', ' ')) : params.delete("data_start");

            const dataEnd = document.getElementById("dataEndInput").value;
            dataEnd ? params.set("data_end", dataEnd.replace('T', ' ')) : params.delete("data_end");

            url.search = params.toString();
            window.location.href = url.toString();
        },

        resetFilters: () => {
            const url = new URL(window.location.href);
            const params = url.searchParams;

            params.set("types", "all");

            params.delete("function_name");
            params.delete("data_start");
            params.delete("data_end");

            const log = params.get("log");
            const page = params.get("page");

            url.search = "";

            url.searchParams.set("types", "all");

            if (log) {
                url.searchParams.set("log", log);
            }

            if (page) {
                url.searchParams.set("page", page);
            }

            window.location.href = url.toString();
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    Dashboard.filterManager.init();
     if (localStorage.getItem("scrollToLocButtons") === "true") {
        localStorage.removeItem("scrollToLocButtons");
        const locButtons = document.getElementById("loc-buttons");
        if (locButtons) {
            setTimeout(() => {
                locButtons.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 20);
        }
    }
    localStorage.removeItem("scrollToLocButtons");
});

window.selectLog = Dashboard.navigation.selectLog;
window.gotoNextPage = Dashboard.navigation.gotoNextPage;
window.gotoPrevPage = Dashboard.navigation.gotoPrevPage;
window.applyFilter = Dashboard.filterManager.applyFilters;
window.resetFilters = Dashboard.filterManager.resetFilters;