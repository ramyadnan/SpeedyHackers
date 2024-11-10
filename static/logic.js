function Calculate() {
    document.write(document.getElementById("age").value)
}

window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const selectedEra = urlParams.get('era'); // This retrieves the selected era from the URL
    if (selectedEra) {
        document.getElementById('eraDisplay').innerText = `You chose: ${selectedEra}`;
    }
};

