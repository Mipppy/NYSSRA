Navbar.LoadExtraHTML()

let request_data = []
var showdownInstance = new showdown.Converter({ openLinksInNewWindow: true })


const MDParentDiv = document.getElementById('md_parent_div')
// Gets 10 at a time
async function getPostMetadataPaginated(index) {
    var req = await fetch(`${Navbar.url}/pages_paginated`, { method: "POST", body: index })
    var returnData = await req.json()
    request_data.push(returnData)
    return returnData
}

async function renderPost(post_data) {
    const req_data = await Navbar.loadPageFromName(post_data.post_name);
    const isEvent = req_data.pd.isEvent;
    const eventButtonHTML = isEvent
        ? `<div class="d-flex justify-content-end">
        <a href="/calendar?event=${encodeURIComponent(req_data.pd.postName)}" class="btn btn-primary btn-sm mt-2">
          View on Calendar
        </a>
     </div>`
        : "";

    const newDiv = document.createElement('div');
    newDiv.classList = "col-12 mb-4";

    newDiv.innerHTML = `
  <div class="card shadow-lg rounded-3 border-2">
    <div class="card-body">
      <h2 class="card-title mb-3">${req_data.pd.postName}</h2>
      <p class="text-muted small mb-3">
        Posted by <b>${req_data.pd.author}</b> on <i>${new Date(req_data.pd.date).toLocaleString()}</i>
      </p>
      <hr>
      <div class="markdown-body mb-2">${showdownInstance.makeHtml(req_data.md)}</div>
      ${eventButtonHTML}
    </div>
  </div>
`;

    MDParentDiv.appendChild(newDiv);
}
async function renderPosts(data) {
    const sortedPosts = data.results.sort((a, b) => {
        return new Date(b.date) - new Date(a.date);
    });

    for (let post of sortedPosts) {
        await renderPost(post);
    }
}


function loadAndDisplayPosts(index) {
    getPostMetadataPaginated(index).then(data => renderPosts(data))
}

loadAndDisplayPosts(0)
