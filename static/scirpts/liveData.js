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

const sound = new Audio('../static/sounds/sound.mp3');

evtSource.onmessage = function(event) {
    try {
        const data = JSON.parse(event.data);
        if (!data.text) return;

        plateEl.innerText = data.text;

        if (!data.text || data.valid !== true) {
            plateEl.innerText = data.text || "UNKNOWN";
            totemFrame.classList.add("state-error");
            messageText.innerText = "The operation was unsuccessful. Please pay the parking fee.";
            statusText.innerText = "ACCESS DENIED";

            sound.currentTime = 0;
            sound.play().catch(() => {});

            setTimeout(() => {
                totemFrame.classList.remove("state-error");
            }, 5000);

            return;
        }

        plateEl.innerText = data.text;
        totemFrame.classList.add("state-granted");
        messageText.innerText = "The operation was successful. You may proceed.";
        statusText.innerText = "ACCESS GRANTED";

        sound.currentTime = 0;
        sound.play().catch(() => {});

        setTimeout(() => {
            totemFrame.classList.remove("state-granted");
        }, 5000);

    } catch (e) {
        console.error("Грешка при обработка на събитието:", e);
    }
};
