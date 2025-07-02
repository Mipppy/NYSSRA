window.displayCalendar = (json_events) => {
  const calendarEl = document.getElementById('calendar');
  const searchInput = document.getElementById('event-search');

  const events = json_events.map(event => ({
    title: event.post_name,
    start: event.event_date,
    url: `/article.html?article=${event.txt_path.replace('.txt', '')}`,
    txtPath: event.txt_path.replace('.txt', ''),
    allDay: true
  }));

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    events: events
  });

  calendar.render();

  let matchedEvents = [];
  let matchIndex = 0;

  const urlParams = new URLSearchParams(window.location.search);
  const targetEvent = urlParams.get("event");
  if (targetEvent) {
    const match = events.find(ev => ev.txtPath === targetEvent);
    if (match) {
      calendar.gotoDate(match.start);
    }
  }

  searchInput.addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    matchedEvents = events.filter(ev => ev.title.toLowerCase().includes(query));
    matchIndex = 0;
  });

  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && matchedEvents.length > 0) {
      const event = matchedEvents[matchIndex];
      calendar.gotoDate(event.start);
      matchIndex = (matchIndex + 1) % matchedEvents.length;
    }
  });

  document.getElementById('export-pdf-btn').addEventListener('click', () => {
    const calendarTableEle = calendarEl.querySelector('table.fc-scrollgrid');
    html2canvas(calendarTableEle, { scale: 2 }).then(canvas => {
      const imgData = canvas.toDataURL('image/png');
      const { jsPDF } = window.jspdf;
      const pdf = new jsPDF('landscape', 'pt', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
      const imgScaledWidth = imgWidth * ratio;
      const imgScaledHeight = imgHeight * ratio;
      const x = (pdfWidth - imgScaledWidth) / 2;
      const y = (pdfHeight - imgScaledHeight) / 2;
      pdf.addImage(imgData, 'PNG', x, y, imgScaledWidth, imgScaledHeight);
      pdf.save('calendar.pdf');
    });
  });
};
