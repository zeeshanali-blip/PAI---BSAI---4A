function searchVehicle() {
    const vehicle = document.getElementById('vehicleInput').value;
    if (!vehicle) return;
    document.getElementById('loading').style.display = 'block';
    fetch('/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({vehicle: vehicle})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';
        if (data.error) {
            resultsDiv.innerHTML = `<p>${data.error}</p>`;
        } else if (data.results) {
            data.results.forEach(vehicle => {
                resultsDiv.innerHTML += `<div class="card"><h3>${vehicle.make} ${vehicle.model}</h3></div>`;
            });
        } else {
            resultsDiv.innerHTML = `<p>${data.message}</p>`;
        }
    });
}