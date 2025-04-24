Navbar.LoadExtraHTML()
let currentSort = 'date-desc';
let allRaces = [];

async function fetchRaces() {
    try {
        const response = await fetch('http://nyssra.pythonanywhere.com/all_races');
        const data = await response.json();
        allRaces = data;
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
            races = races.filter(race => {
                const raceTime = new Date(race.timestamp);
                return (now - raceTime) / (1000 * 60) <= 60;
            });
            races.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            break;
        default:
            races.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    }

    races.forEach(race => {
        const raceTime = new Date(race.timestamp);
        const isLive = (now - raceTime) / (1000 * 60) <= 60;

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
                    <div class="d-flex justify-content-between align-items-center" onclick="handleRaceEntryClick(event)" race-url=${race.filename}>
                        <div class="flex-grow-1 px-3">
                            <div class="race-title">${race.name}</div>
                            <div class="race-place">${race.place}</div>
                        </div>
                        <div class=" px-3">
                            <div class="text-muted">${dateString}</div>
                            ${isLive ? '<div class="live-indicator" title="Live now"><b>Live!</b><span class="live-dot"></span></div>' : ''}
                        </div>
                    </div>
                `;

        container.appendChild(div);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    fetchRaces();

    document.querySelectorAll('.sort-option').forEach(option => {
        option.addEventListener('click', function () {
            document.querySelectorAll('.sort-option').forEach(opt => {
                opt.classList.remove('active');
            });

            this.classList.add('active');

            currentSort = this.dataset.sort;
            sortAndDisplayRaces();
        });
    });

    document.querySelector(`.sort-option[data-sort="${currentSort}"]`).classList.add('active');

    document.getElementById('refreshBtn').addEventListener('click', fetchRaces);

    document.getElementById('search_races').addEventListener("keyup" , ev=> {
        const searchTerm = ev.target.value.toLowerCase().trim();
        const container = document.getElementById('raceList');
        const raceEntries = container.querySelectorAll('.race-entry');
        
        raceEntries.forEach(entry => {
            const raceName = entry.querySelector('.race-title').textContent.toLowerCase();
            const shouldShow = raceName.includes(searchTerm);
            entry.style.display = shouldShow ? '' : 'none';
        });
    })


});

function handleRaceEntryClick(ev) {
    const clickableDiv = ev.target.closest('[race-url]');
    if (!clickableDiv) return;
    
    const filename = clickableDiv.getAttribute('race-url');
    window.location.replace(`/race_viewer.html?race_url=${filename}`);
}

setInterval(fetchRaces, 15000);