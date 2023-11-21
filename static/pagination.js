document.addEventListener('DOMContentLoaded', function () {
    // Változók a lapozás kezeléséhez
    let currentPage = 1;  // Az aktuális oldalszám
    const itemsPerPage = 15;  // Oldalankénti találatok száma

    // Függvény az oldal frissítéséhez adataink alapján
    function updatePage() {
        fetch(`/get_hot_wheels_data?page=${currentPage}&per_page=${itemsPerPage}`)
            .then(response => response.json())
            .then(data => {
                const tableBody = document.getElementById('hotWheelsTableBody');

                // Clear existing rows
                tableBody.innerHTML = '';

                // Append new rows with data and checkboxes
                data.data.forEach(row => {
                    const newRow = document.createElement('tr');
                    newRow.innerHTML = `
                    <td>${row.toy_number}</td>
                    <td>${row.collection_number}</td>
                    <td>${row.release_year}</td>
                    <td>${row.model_name}</td>
                    <td>${row.series}</td>
                    <td>${row.series_number}</td>
                    <td><a data-fancybox href="${row.photo_url}"><img src="${row.photo_url}" alt="Hot Wheels Photo" /></a></td>
                    <td><label><input type="checkbox" class="filled-in" /><span></span></label></td>
                    `;
                    tableBody.appendChild(newRow);
                });

                // Frissítse az oldalszámot
                const currentPageSpan = document.getElementById('currentPage');
                currentPageSpan.textContent = `Oldal: ${currentPage}`;
            })
            .catch(error => console.error('Error fetching Hot Wheels data:', error));
    }

    // Kattintásesemények kezelése az oldalváltáshoz
    document.getElementById('previousPageBtn').addEventListener('click', goToPreviousPage);
    document.getElementById('nextPageBtn').addEventListener('click', goToNextPage);

    // Függvény az előző oldalra lépéshez
    function goToPreviousPage() {
        if (currentPage > 1) {
            currentPage--;
            updatePage(); // Frissítse az oldalt az új oldalszámra
        }
    }

    // Függvény a következő oldalra lépéshez
    function goToNextPage() {
        currentPage++;
        updatePage(); // Refresh the page with the new page number
    }

    // Hívja meg az 'updatePage' függvényt az inicializáláshoz
    updatePage();
});
