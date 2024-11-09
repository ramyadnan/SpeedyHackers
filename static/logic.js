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

// script.js

// Era display mappings
const eraInfo = {
    egypt: {
        name: "Ancient Egypt",
        description: "In Ancient Egypt, life expectancy was influenced by diet, climate, and access to medicine.",
        imageUrl: "images/ancient-egypt.jpg"
    },
    medieval: {
        name: "Medieval Europe",
        description: "Medieval Europe was marked by plagues and limited medical knowledge, affecting longevity.",
        imageUrl: "images/medieval-europe.jpg"
    },
    "world-war": {
        name: "World War Times",
        description: "Health during the world wars was affected by scarcity, stress, and wartime injuries.",
        imageUrl: "images/world-war.jpg"
    },
    "present-day": {
        name: "Present Day",
        description: "Modern medicine has greatly increased life expectancy compared to the past.",
        imageUrl: "images/present-day.jpg"
    }
};

// Get the selected era from the URL query parameters
const params = new URLSearchParams(window.location.search);
const selectedEra = params.get("era");

// Display era information if it matches a known era
if (selectedEra && eraInfo[selectedEra]) {
    document.getElementById("eraName").textContent = eraInfo[selectedEra].name;
    document.getElementById("era-description").textContent = eraInfo[selectedEra].description;
    document.getElementById("era-image").src = eraInfo[selectedEra].imageUrl;
    document.getElementById("era-image").alt = eraInfo[selectedEra].name;
} else {
    document.getElementById("eraName").textContent = "Unknown Era";
}


