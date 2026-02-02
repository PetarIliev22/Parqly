const plateEl = document.getElementById("plate");
const statusText = document.getElementById("status-text");
const totemFrame = document.getElementById("totem-frame");
const clockEl = document.getElementById("live-clock");
const dateEl = document.getElementById("live-date");

function updateInterface() {
    const now = new Date();
    clockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const dateOptions = { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' };
    dateEl.textContent = now.toLocaleDateString('en-GB', dateOptions).toUpperCase();
}

updateInterface();
setInterval(updateInterface, 1000);

const evtSource = new EventSource("/plate/stream");

evtSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
 
    if (data.text && data.text !== "") {
        plateEl.innerText = data.text;

        if (data.valid) {
            totemFrame.classList.add("state-granted");
            statusText.innerText = "ACCESS GRANTED";
            new Audio('../static/access.mp3').play().catch(() => {});

            setTimeout(() => {
                totemFrame.classList.remove("state-granted");
                setTimeout(() => {
                    plateEl.innerText = "SCANNING";
                    statusText.innerText = "WAITING...";
                }, 600);
            }, 5000);
        } else {
            totemFrame.classList.add("state-error");
            statusText.innerText = "ACCESS DENIED";
            setTimeout(() => totemFrame.classList.remove("state-error"), 5000);
        }
    }
};