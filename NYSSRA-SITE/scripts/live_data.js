Navbar.LoadExtraHTML();

var prev_data = null;
var interval = null;
var isLive = null;

function getRaceStatus(header) {
    if (header.header.live) return { class: "live", text: "Live" };

    const raceDate = new Date(header.header_timestamp);
    const now = new Date();
    const diffDays = (now - raceDate) / (1000 * 60 * 60 * 24);

    if (diffDays <= 3) return { class: "recent", text: "Recent" };
    return { class: "finished", text: "Finished" };
}

function formatTime(secondsTotal) {
    const hours = Math.floor(secondsTotal / 3600);
    const minutes = Math.floor((secondsTotal % 3600) / 60);
    const seconds = Math.floor(secondsTotal % 60);
    const tenths = Math.floor((secondsTotal - Math.floor(secondsTotal)) * 10);

    if (hours > 0) {
        const minuteStr = minutes.toString().padStart(2, "0");
        const secondStr = seconds.toString().padStart(2, "0");
        return `${hours}:${minuteStr}:${secondStr}.${tenths}`;
    } else {
        const minuteStr = minutes.toString().padStart(2, "0");
        const secondStr = seconds.toString().padStart(2, "0");
        return `:${minuteStr}:${secondStr}.${tenths}`;
    }
}
async function updateRaceData(urlParam) {
    let data = await Navbar.loadRaceData(urlParam.get("race_filename"));
    if (data == prev_data) return;
    const header = data[0];
    document.getElementById("race-name").innerText =
        header.header.headers.race_name;
    document.getElementById("race-location").innerText =
        header.header.headers.race_location;
    document.getElementById("race-start-time").innerText =
        header.header_timestamp;

    const statusInfo = getRaceStatus(header);
    const statusDot = document.getElementById("race-status");
    const statusText = document.getElementById("race-status-text");

    statusDot.className = `status-dot ${statusInfo.class}`;
    statusText.innerText = statusInfo.text;
    document.getElementById("race-results-body").innerHTML = "";
    const racers = data
        .slice(1)
        .map((r) => r.data)
        .sort(
            (a, b) =>
                a.timing_data.corrected_time - b.timing_data.corrected_time
        );

    racers.forEach((r, index) => {
        const place = index + 1;
        const points = (index + 1).toFixed(2);

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${place}</td>
            <td>${r.bib_num}</td>
            <td>${r.first_name} ${r.last_name}</td>
            <td>${r.team}</td>
            <td>${formatTime(r.timing_data.corrected_time)}</td>
            <td>${points}</td>
        `;
        document.getElementById("race-results-body").appendChild(row);
    });

    prev_data = data;
}

document.addEventListener("DOMContentLoaded", async () => {
    const url_params = new URLSearchParams(window.location.search);
    const loadingContainer = document.getElementById("loading");
    const failedToLoadContainer = document.getElementById("failed-to-load");
    const actualDataContainer = document.getElementById("actual-data");
    let data = await Navbar.loadRaceData(url_params.get("race_filename"));
    loadingContainer.style.display = "none";
    if (data.length == 0) {
        failedToLoadContainer.classList.remove("d-none");
        failedToLoadContainer.classList.add("d-block");
    } else {
        actualDataContainer.classList.add("d-flex");
        actualDataContainer.classList.remove("d-none");
        if (data[0].header.live) {
            setInterval(async function () {
                await updateRaceData(url_params);
            }, 1000);
        }
        if (Object.keys(data[0].header.headers).length > 2) {
            document
                .getElementById("additional-race-headers")
                .classList.remove("d-none");
            delete data[0].header.headers.race_name;
            delete data[0].header.headers.race_location;
            Object.entries(data[0].header.headers).forEach((e) => {
                document.getElementById(
                    "additional-race-headers-container"
                ).innerHTML += `<li><i>${e[0]}</i>:&nbsp;&nbsp;${e[1]}</li>`;
            });
        }
        updateRaceData(url_params);
    }
});
function getTableData() {
    const rows = [];
    document.querySelectorAll("#race-results-body tr").forEach((tr) => {
        const cells = Array.from(tr.children).map((td) => td.innerText.trim());
        rows.push(cells);
    });
    return rows;
}

document.getElementById("save_csv").addEventListener("click", () => {
    const headers = ["Place", "BIB", "Name", "Team", "Time", "Points"];
    const data = getTableData();
    const csvRows = [headers.join(","), ...data.map((r) => r.join(","))];
    const blob = new Blob([csvRows.join("\n")], {
        type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "race_results.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
});

document.getElementById("save_xlsx").addEventListener("click", () => {
    const ws = XLSX.utils.aoa_to_sheet([
        ["Place", "BIB", "Name", "Team", "Time", "Points"],
        ...getTableData(),
    ]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Race Results");
    XLSX.writeFile(wb, "race_results.xlsx");
});

document.getElementById("save_pdf").addEventListener("click", () => {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const raceName = document.getElementById("race-name").innerText;
    const raceLocation = document.getElementById("race-location").innerText;
    const raceTime = document.getElementById("race-start-time").innerText;
    doc.setFontSize(16);
    doc.text(`Race Results: ${raceName}`, 14, 20);
    doc.setFontSize(12);
    doc.text(`Location: ${raceLocation}`, 14, 28);
    doc.text(`Start Time: ${raceTime}`, 14, 36);

    const headers = [["PL", "BIB", "Name", "Team", "Time", "PTS"]];
    const data = getTableData();

    doc.autoTable({
        startY: 44,
        head: headers,
        body: data,
        theme: "grid",
        headStyles: { fillColor: [40, 116, 240], textColor: 255 },
        styles: { fontSize: 10 },
    });

    doc.save(`${raceName.replace(/\s+/g, "_")}_results.pdf`);
});
