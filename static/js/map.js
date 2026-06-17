// GridGuard AI - Map & Chatbot Logic

let map;
let currentZones = [];

function initMap() {
    map = L.map('map').setView([40.7128, -74.0060], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors'
    }).addTo(map);

    fetchRiskData();
}

function fetchRiskData() {
    fetch('/risk-map-data/')
        .then(response => response.json())
        .then(data => {
            currentZones = data.zones;
            data.zones.forEach(zone => {
                let color = zone.risk > 0.7 ? '#d62828' : (zone.risk > 0.4 ? '#f77f00' : '#2a9d8f');
                let radius = 500 + (zone.risk * 500); // dynamic radius based on risk
                let circle = L.circle([zone.lat, zone.lon], {
                    color: color,
                    weight: 2,
                    fillColor: color,
                    fillOpacity: 0.5,
                    radius: radius
                }).addTo(map);

                let infraHtml = '';
                if (zone.infrastructure.length > 0) {
                    infraHtml = '<ul style="margin:5px 0 0 15px">';
                    zone.infrastructure.forEach(i => {
                        infraHtml += `<li><strong>${i.name}</strong> (${i.type})<br>📞 ${i.phone || 'N/A'}</li>`;
                    });
                    infraHtml += '</ul>';
                } else {
                    infraHtml = '<em>No critical infrastructure listed</em>';
                }

                circle.bindPopup(`
                    <b style="font-size:1.1rem">${zone.name}</b><br>
                    ⚡ Outage risk: <b>${(zone.risk * 100).toFixed(1)}%</b><br>
                    🎯 Priority score: ${zone.priority}<br>
                    🏥 Critical infrastructure:<br>${infraHtml}
                `);
            });
        })
        .catch(err => console.error('Error loading risk data:', err));
}

function sendMessage() {
    let input = document.getElementById('chatInput');
    let msg = input.value.trim();
    if (msg === '') return;

    let chatDiv = document.getElementById('chatMessages');
    // Add user message
    let userMsgDiv = document.createElement('div');
    userMsgDiv.innerHTML = `🧑‍💻 You: ${escapeHtml(msg)}`;
    chatDiv.appendChild(userMsgDiv);

    // Clear input and scroll
    input.value = '';
    chatDiv.scrollTop = chatDiv.scrollHeight;

    // Call backend chatbot API
    fetch('/chatbot-api/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
    })
    .then(res => res.json())
    .then(data => {
        let botMsgDiv = document.createElement('div');
        botMsgDiv.innerHTML = `🤖 AEGIS: ${escapeHtml(data.reply)}`;
        chatDiv.appendChild(botMsgDiv);
        chatDiv.scrollTop = chatDiv.scrollHeight;
    })
    .catch(err => {
        let errDiv = document.createElement('div');
        errDiv.innerHTML = `🤖 AEGIS: Sorry, I'm having trouble. Please try again.`;
        chatDiv.appendChild(errDiv);
        console.error(err);
    });
}

// Helper to prevent XSS
function escapeHtml(str) {
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

// Allow pressing Enter to send
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    let inputField = document.getElementById('chatInput');
    if (inputField) {
        inputField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    }
});