Navbar.LoadExtraHTML();

let request_data = [];
const showdownInstance = new showdown.Converter(Navbar.showdownParameters);

const MDParentDiv = document.getElementById('md_parent_div');

async function getPostMetadataPaginated(index) {
    const req = await fetch(`${Navbar.url}/pages_paginated`, {
        method: "POST",
        body: index.toString(),
    });
    const returnData = await req.json();
    request_data.push(returnData);
    return returnData;
}
async function renderPost(post_data) {
    const req_data = await Navbar.loadPageFromName(post_data.post_name);
    const isEvent = req_data.pd.isEvent;

    const eventButtonHTML = isEvent
        ? `<div class="d-flex flex-column gap-2">  
            <a href="/calendar.html?event=${encodeURIComponent(req_data.article)}" 
               class="btn btn-sm btn-outline-secondary text-nowrap px-3"> <!-- text-nowrap prevents wrapping -->
               <i class="bi bi-calendar-event-fill me-2"></i> View on Calendar
            </a>
            <a target="_blank" id="event-google-calendar"
               class="btn btn-sm btn-outline-secondary text-nowrap px-3">     
               <i class="bi bi-google me-2"></i> Add on Google Calendar
            </a>
       </div>`
        : "";

    const newDiv = document.createElement('div');
    newDiv.classList = "col-12 mb-4";
    const tagsHTML = req_data.pd.tags.map(tag => Navbar.generateTagFormat(tag)).join('');

    newDiv.innerHTML = `
        <div class="card shadow-lg rounded-3 border-2" style="cursor:default;" article-name="${req_data.article}" id="loaded_article">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h2 class="card-title mb-0">
                        <i class="bi bi-journal-text me-2"></i>${req_data.pd.postName}
                    </h2>
                    ${eventButtonHTML}
                </div>

                <p class="text-muted small mb-3">
                    Posted by <i class="bi bi-person-fill"></i> <b>${req_data.pd.author}</b> 
                    on <i>${Navbar.turnToCorrectDate(req_data.pd.date)}</i>  
                    <i class="bi bi-calendar3 ms-1"></i> 
                </p>
                <div>
                ${tagsHTML}
                </div>
                <hr>
                <div class="markdown-body mb-2">${showdownInstance.makeHtml(req_data.md.substring(0, 1000))}</div>
                <i class="${req_data.md.length > 1000 ? 'bi bi-three-dots me-1' : ''}"></i>${req_data.md.length > 1000 ? '<br>' : ''}
                <a href="/article.html?article=${encodeURIComponent(req_data.article)}" 
                   class="btn btn-outline-primary btn-sm mt-3">
                   Read More
                </a>
            </div>
        </div>
    `;

    MDParentDiv.appendChild(newDiv);
    if (isEvent) {
        Navbar.setGoogleCalendarLink(req_data.pd, document.getElementById('event-google-calendar'))
    }

}


async function renderPosts(data) {
    const sortedPosts = data.results.sort((a, b) => new Date(b.date) - new Date(a.date));
    for (const post of sortedPosts) {
        await renderPost(post);
    }
    for (const ele of document.querySelectorAll('#loaded_article')) {
        ele.style.cursor = 'pointer';

        ele.addEventListener('click', function (eve) {
            if (!eve.target.closest('a, button')) {
                ele.style.cursor = ''
                location.href = `/article.html?article=${ele.getAttribute('article-name')}`;
            }
        });

        const interactiveChildren = ele.querySelectorAll('a, button');
        interactiveChildren.forEach(child => {
            child.style.cursor = 'auto';
        });
    }


}

function loadAndDisplayPosts(index) {
    getPostMetadataPaginated(index).then(data => renderPosts(data));
}

(async () => {
    events = await Navbar.loadAllEvents()
})()
loadAndDisplayPosts(0);

document.getElementById("calendar-frame").addEventListener("load", () => {
    const iframe = document.getElementById("calendar-frame").contentWindow;

    iframe.document.addEventListener("click", (e) => {
        let a = e.target.closest("a");
        if (!a) return;

        e.preventDefault();
        window.location.href = a.href; 
    });
});