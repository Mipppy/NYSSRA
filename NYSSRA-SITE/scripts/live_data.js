Navbar.LoadExtraHTML()

var prev_data = null

function getRaceStatus(header) {
    if (header.live) return { class: "live", text: "Live" };

    const raceDate = new Date(header.header_timestamp);
    const now = new Date();
    const diffDays = (now - raceDate) / (1000 * 60 * 60 * 24);

    if (diffDays <= 3) return { class: "recent", text: "Recent" };
    return { class: "finished", text: "Finished" };
}

async function updateRaceData(urlParam) {
    let data = await Navbar.loadRaceData(urlParam.get('race_filename'));
    if (data == prev_data) return;

    const header = data[0];
    document.getElementById('race-name').innerText = header.header.name;
    document.getElementById('race-location').innerText = header.header.place;
    document.getElementById('race-start-time').innerText = header.header_timestamp;

    const statusInfo = getRaceStatus(header);
    const statusDot = document.getElementById('race-status');
    const statusText = document.getElementById('race-status-text');

    statusDot.className = `status-dot ${statusInfo.class}`;
    statusText.innerText = statusInfo.text;

    prev_data = data;
}

document.addEventListener('DOMContentLoaded', async () => {
    const url_params = new URLSearchParams(window.location.search)
    const loadingContainer = document.getElementById('loading')
    const failedToLoadContainer = document.getElementById('failed-to-load')
    const actualDataContainer = document.getElementById('actual-data')
    let data = await Navbar.loadRaceData(url_params.get('race_filename'))
    loadingContainer.style.display = 'none'
    if (data.length == 0) {
        failedToLoadContainer.classList.remove('d-none')
        failedToLoadContainer.classList.add('d-block')
    } else {
        actualDataContainer.classList.add('d-flex')
        actualDataContainer.classList.remove('d-none')
        if (data[0].header.live) {
            setInterval(async function () {
                await updateRaceData(url_params)
            }, 500)
        }
        updateRaceData(url_params)
    }
})