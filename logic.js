function Calculate(){
    document.write(document.getElementById("age").value)
}

//window.onload = function() {
//    const urlParams = new URLSearchParams(window.location.search);
//    const selectedEra = urlParams.get('era'); // This retrieves the selected era from the URL
//    if (selectedEra) {
//        document.getElementById('eraDisplay').innerText = `You chose: ${selectedEra}`;
//    }
//};


window.onload = function() {
    const eras = document.querySelectorAll('.era');

    // Add click event to each era section
    eras.forEach(era => {
        era.addEventListener('click', function() {
            const selectedEra = era.getAttribute('data-era');
            // Redirect to the next page with the selected era
            window.location.href = `health-input-form.html?era=${selectedEra}`;
        });
    });
};

