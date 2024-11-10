

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
            
            window.location.href =`/health-input?era=${selectedEra}`;  // Flask route handling the era param
        });
    });
};


// script.js

// Era display mappings

const eraInfo = {
    "egypt": {
        name: "Ancient Egypt",
        description: "In Ancient Egypt, life expectancy was influenced by diet, climate, and access to medicine.",
        imageUrl: "images/ancient-egypt.jpg"
    },
    "medieval": {
        name: "Medieval Europe",
        description: "Medieval Europe was marked by plagues and limited medical knowledge, affecting longevity.",
        imageUrl: "images/medieval-europe.jpg"
    },
    "world-war": {
        name: "World War Times",
        description: "Health during the world wars was affected by scarcity, stress, and wartime injuries.",
        imageUrl: "images/war.jpg"
    },
    "present-day": {
        name: "Present Day",
        description: "Modern medicine has greatly increased life expectancy compared to the past.",
        imageUrl: "images/present.jpg"
    }
};

// Display era information if a known era is selected
if (selectedEra && eraInfo[selectedEra]) {
    // Display the era name
    const eraName = eraInfo[selectedEra].name;

    document.getElementById("eraName").textContent = eraName;
    document.getElementById("eraDisplayInput").value = eraName; // Update hidden input value
    
} else {
    document.getElementById("eraName").textContent = "Unknown Era";
}

