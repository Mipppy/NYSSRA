Navbar.LoadExtraHTML();

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("races-card-container");
    let races = [];
    let filtered = [];

    function getStatusColor(race) {
        if (race.live) return "background-color: #198754;";
        const raceDate = new Date(race.timestamp);
        const now = new Date();
        const diffDays = (now - raceDate) / (1000 * 60 * 60 * 24);
        if (diffDays <= 3) return "background-color: #0d6efd;";
        return "background-color: #dc3545;";
    }

    function updateURLParams() {
        const params = new URLSearchParams();
        const search = document.getElementById("search-box").value;
        const start = document.getElementById("date-start").value;
        const end = document.getElementById("date-end").value;
        const sort = document.getElementById("sort-select").value;

        if (search) params.set("search", search);
        if (start) params.set("start", start);
        if (end) params.set("end", end);
        if (sort) params.set("sort", sort);

        const newUrl = `${window.location.pathname}?${params.toString()}`;
        window.history.replaceState({}, "", newUrl);
    }

    function loadFromURLParams() {
        const params = new URLSearchParams(window.location.search);
        if (params.has("search"))
            document.getElementById("search-box").value = params.get("search");
        if (params.has("start"))
            document.getElementById("date-start").value = params.get("start");
        if (params.has("end"))
            document.getElementById("date-end").value = params.get("end");
        if (params.has("sort"))
            document.getElementById("sort-select").value = params.get("sort");
    }

    function applyFilters() {
        const query = document.getElementById("search-box").value.toLowerCase();
        const startDate = document.getElementById("date-start").value;
        const endDate = document.getElementById("date-end").value;

        filtered = races.filter((race) => {
            const nameMatch =
                race.name.toLowerCase().includes(query) ||
                race.place.toLowerCase().includes(query);

            const raceDate = new Date(race.timestamp);
            let inRange = true;
            if (startDate && raceDate < new Date(startDate)) inRange = false;
            if (endDate && raceDate > new Date(endDate)) inRange = false;

            return nameMatch && inRange;
        });
    }

    function renderRaces() {
        container.innerHTML = "";
        if (filtered.length === 0) {
            container.innerHTML = `<p class="text-muted">No races found.</p>`;
            return;
        }

        filtered.forEach((race) => {
            let statusClass = "finished";
            if (race.live) statusClass = "live";
            else {
                const raceDate = new Date(race.timestamp);
                const now = new Date();
                const diffDays = (now - raceDate) / (1000 * 60 * 60 * 24);
                if (diffDays <= 3) statusClass = "recent";
            }

            const card = document.createElement("div");
            card.className = "col-12 col-md-6 col-lg-4";

            card.innerHTML = `
      <div class="card h-100 shadow-sm" role="button" style="margin: 5px; border-radius: 6px;">
        <div class="card-body d-flex justify-content-between align-items-center">
          <div style="margin-right: 20px;">
            <h5 class="card-title mb-1">${race.name}</h5>
            <p class="card-text mb-0">
              <strong>Place:</strong> ${race.place}<br>
              <strong>Date:</strong> ${new Date(
                  race.timestamp
              ).toLocaleString()}
            </p>
          </div>
          <div class="status-dot ${statusClass}"></div>
        </div>
      </div>
    `;

            card.addEventListener("click", () => {
                window.location.href = `/live_data.html?race_filename=${race.filename}`;
            });

            container.appendChild(card);
        });
    }

    function sortRaces(criteria) {
        filtered.sort((a, b) => {
            switch (criteria) {
                case "timestamp_asc":
                    return new Date(a.timestamp) - new Date(b.timestamp);
                case "timestamp_desc":
                    return new Date(b.timestamp) - new Date(a.timestamp);
                case "name_asc":
                    return a.name.localeCompare(b.name);
                case "name_desc":
                    return b.name.localeCompare(a.name);
                default:
                    return 0;
            }
        });
        renderRaces();
    }

    document.addEventListener("input", (e) => {
        if (["search-box", "date-start", "date-end"].includes(e.target.id)) {
            applyFilters();
            sortRaces(document.getElementById("sort-select").value);
            updateURLParams();
        }
    });

    document.addEventListener("change", (e) => {
        if (e.target.id === "sort-select") {
            sortRaces(e.target.value);
            updateURLParams();
        }
    });

    Navbar.loadAllRaces().then((json) => {
        races = json;
        loadFromURLParams();
        applyFilters();
        sortRaces(
            document.getElementById("sort-select").value || "timestamp_desc"
        );
    });
});
