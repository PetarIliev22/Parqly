const plateEl = document.getElementById("plate");
const statusText = document.getElementById("status-text");
const messageText = document.getElementById("message-text");
const totemFrame = document.getElementById("totem-frame");
const clockEl = document.getElementById("live-clock");
const dateEl = document.getElementById("live-date");
const evtSource = new EventSource("/plate/stream");

function updateInterface() {
    const now = new Date();
    clockEl.textContent = now.toLocaleTimeString('bg-BG', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Sofia' });
    
    const dateOptions = { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' };
    dateEl.textContent = now.toLocaleDateString('en-GB', dateOptions).toUpperCase();
}

updateInterface();
setInterval(updateInterface, 1000);

const chime = new Audio('../static/sounds/sound.mp3');

evtSource.onmessage = function(event) {
    try {
        const data = JSON.parse(event.data);
        if (!data.text) return;

        plateEl.innerText = data.text;

        const config = data.valid ? {
            class: "state-granted",
            msg: "The operation was successful. You may proceed.",
            status: "ACCESS GRANTED"
        } : {
            class: "state-error",
            msg: "The operation was unsuccessful. Please pay the parking fee.",
            status: "ACCESS DENIED"
        };

        totemFrame.classList.add(config.class);
        messageText.innerText = config.msg;
        statusText.innerText = config.status;
        
        chime.currentTime = 0;
        chime.play().catch(() => {});

        setTimeout(() => {
            totemFrame.classList.remove(config.class);
        }, 5000);

    } catch (e) {
        console.error("Грешка при обработка на събитието:", e);
    }
};
