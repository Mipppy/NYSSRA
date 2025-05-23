// Y'all get HTTP requests ever 5 seconds because I AIN'T doing another websocket for your sorry ass

Navbar.LoadExtraHTML();

const livetiming_data_div = document.getElementById("livedata-div");
const lastUpdatedEl = document.getElementById("last-updated");
const pollingStatusEl = document.getElementById("polling-status");
let refreshInterval;
let lastUpdateTime = null;

function formatTimestamp() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
}

function updateStatus() {
    if (lastUpdateTime) {
        const secondsAgo = Math.floor((new Date() - lastUpdateTime) / 1000);
        lastUpdatedEl.textContent = `${formatTimestamp()} (${secondsAgo}s ago)`;
        
        if (secondsAgo > 10) {
            lastUpdatedEl.classList.add('text-danger');
            lastUpdatedEl.classList.remove('text-success');
        } else {
            lastUpdatedEl.classList.add('text-success');
            lastUpdatedEl.classList.remove('text-danger');
        }
    }
}

async function handleIncomingData() {
    try {
        const url = `${Navbar.url}/livetiming_data/${window.race_url}`;
        pollingStatusEl.textContent = "Fetching...";
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Get the response as text first
        const textData = await response.text();
        
        // Process JSONL format (each line is a separate JSON object)
        const jsonLines = textData.trim().split('\n');
        const parsedData = jsonLines.map(line => JSON.parse(line));
        
        // Format the output with syntax highlighting
        livetiming_data_div.innerHTML = parsedData
            .map(obj => `<pre class="mb-2">${JSON.stringify(obj, null, 2)}</pre>`)
            .join('<hr>');
            
        lastUpdateTime = new Date();
        updateStatus();
        pollingStatusEl.textContent = "Active";
        pollingStatusEl.classList.remove('text-danger');
        
    } catch (error) {
        console.error('Failed to fetch live timing data:', error);
        pollingStatusEl.textContent = "Error";
        pollingStatusEl.classList.add('text-danger');
    }
}

document.addEventListener('DOMContentLoaded', ev => {
    const urlParams = new URLSearchParams(window.location.search);
    const race_url = urlParams.get('race_url');
    
    if (!race_url) {
        alert("Failed to load race!");
        window.location.replace("/");
        return;
    }
    
    window.race_url = race_url;
    
    if (refreshInterval) clearInterval(refreshInterval);
    
    refreshInterval = setInterval(() => {
        handleIncomingData();
        updateStatus(); 
    }, 2000);
    
    handleIncomingData();
    
    setInterval(updateStatus, 1000);
});