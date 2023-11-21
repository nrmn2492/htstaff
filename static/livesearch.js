let searchTimeout;

// Function to perform delayed live search
function delayedLiveSearch() {
    // Clear previous timeout, if any
    clearTimeout(searchTimeout);

    // Set a new timeout for 1.5 seconds after the user stops typing
    searchTimeout = setTimeout(function () {
        const searchInput = document.getElementById('searchInput').value.toLowerCase();
        const tableBody = document.getElementById('hotWheelsTableBody');

        if (searchInput.length >= 4) {
            fetch('/get_all_hot_wheels_data') // Módosított lekérdezési útvonal
                .then(response => response.json())
                .then(data => {
                    // Filter data based on the search input
                    const filteredData = data.data.filter(row => row.model_name.toLowerCase().includes(searchInput));

                    // Clear existing rows
                    tableBody.innerHTML = '';

                    // Append new rows with filtered data and checkboxes
                    filteredData.forEach(row => {
                        const newRow = document.createElement('tr');
                        newRow.innerHTML = `
                            <td>${row.toy_number}</td>
                            <td>${row.collection_number}</td>
                            <td>${row.model_name}</td>
                            <td>${row.series}</td>
                            <td>${row.series_number}</td>
                            <td>${row.photo}</td>
                            <td><label><input type="checkbox" class="filled-in" /><span></span></label></td>
                        `;
                        tableBody.appendChild(newRow);
                    });
                })
                .catch(error => console.error('Error fetching Hot Wheels data:', error));
        }
    }, 1500); // 1.5 seconds delay
}