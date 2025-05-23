Navbar.LoadExtraHTML()
let currentSort = 'date-desc';
let allRaces = [];

async function fetchRaces() {
    try {
        const response = await fetch('http://nyssra.pythonanywhere.com/all_races');
        const data = await response.json();
        allRaces = data;
        console.log(data)
        sortAndDisplayRaces();
    } catch (error) {
        console.error('Failed to fetch race data:', error);
    }
}

function sortAndDisplayRaces() {
    const container = document.getElementById('raceList');
    container.innerHTML = '';
    const now = new Date();
    let races = [...allRaces];

    switch (currentSort) {
        case 'date-desc':
            races.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            break;
        case 'date-asc':
            races.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            break;
        case 'name-asc':
            races.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'name-desc':
            races.sort((a, b) => b.name.localeCompare(a.name));
            break;
        case 'place-asc':
            races.sort((a, b) => a.place.localeCompare(b.place));
            break;
        case 'place-desc':
            races.sort((a, b) => b.place.localeCompare(a.place));
            break;
        case 'live':
            races = races.filter(race => race.header?.live === true);
            break;
    }

    races.forEach(race => {
        const raceTime = new Date(race.timestamp);
        const minutesSinceRace = (now - raceTime) / (1000 * 60);
        const isLive = race.live === true;
        console.log(race)
        let statusLabel = 'Finished';
        let statusColor = 'red';

        if (isLive) {
            statusLabel = 'Live!';
            statusColor = 'green';
        } else if (minutesSinceRace <= 1440) {
            statusLabel = 'Recent';
            statusColor = 'blue';
        }

        const dateString = raceTime.toLocaleString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });

        const div = document.createElement('div');
        div.className = 'list-group-item race-entry';
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center" onclick="handleRaceEntryClick(event)" race-url="${race.filename}">
                <div class="flex-grow-1 px-3">
                    <div class="race-title">${race.name}</div>
                    <div class="race-place">${race.place}</div>
                </div>
                <div class="px-3 text-end">
                    <div class="text-muted">${dateString}</div>
                    <div class="status-indicator" title="${statusLabel}">
                        <b>${statusLabel}</b>
                        <span class="status-dot" style="background-color: ${statusColor};"></span>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(div);
    });
}

function handleRaceEntryClick(ev) {
    const clickableDiv = ev.target.closest('[race-url]');
    if (!clickableDiv) return;
    const filename = clickableDiv.getAttribute('race-url');
    window.location.replace(`/race_viewer.html?race_url=${filename}`);
}

document.addEventListener('DOMContentLoaded', function () {
    fetchRaces();

    document.querySelectorAll('.sort-option').forEach(option => {
        option.addEventListener('click', function () {
            document.querySelectorAll('.sort-option').forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            currentSort = this.dataset.sort;
            sortAndDisplayRaces();
        });
    });

    document.querySelector(`.sort-option[data-sort="${currentSort}"]`).classList.add('active');


    document.getElementById('search_races').addEventListener('keyup', ev => {
        const searchTerm = ev.target.value.toLowerCase().trim();
        const raceEntries = document.querySelectorAll('.race-entry');
        raceEntries.forEach(entry => {
            const raceName = entry.querySelector('.race-title').textContent.toLowerCase();
            entry.style.display = raceName.includes(searchTerm) ? '' : 'none';
        });
    });

    setInterval(fetchRaces, 15000);
});
