function fetchEvents() {
    fetch('/events')
        .then(res => res.json())
        .then(data => {
            const eventsDiv = document.getElementById('events');
            eventsDiv.innerHTML = '';
            data.forEach(message => {
                const el = document.createElement('div');
                el.className = 'event';
                el.textContent = message;
                eventsDiv.appendChild(el);
            });
        });
}

setInterval(fetchEvents, 15000);
window.onload = fetchEvents;
