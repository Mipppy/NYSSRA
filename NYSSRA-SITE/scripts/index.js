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
        ? `<a href="/calendar.html?event=${encodeURIComponent(req_data.article)}" 
             class="btn btn-primary btn-sm d-flex align-items-center gap-1">
                <i class="bi bi-calendar-event-fill"></i> View on Calendar
           </a>`
        : "";

    const newDiv = document.createElement('div');
    newDiv.classList = "col-12 mb-4";
    const tagsHTML = req_data.pd.tags.map(tag => Navbar.generateTagFormat(tag)).join('');

    newDiv.innerHTML = `
        <div class="card shadow-lg rounded-3 border-2" style="cursor:pointer;" id="loaded_article">
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
}


async function renderPosts(data) {
    const sortedPosts = data.results.sort((a, b) => new Date(b.date) - new Date(a.date));
    for (const post of sortedPosts) {
        await renderPost(post);
    }
}

function loadAndDisplayPosts(index) {
    getPostMetadataPaginated(index).then(data => renderPosts(data));
}

loadAndDisplayPosts(0);
