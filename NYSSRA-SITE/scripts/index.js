Navbar.LoadExtraHTML()

var showdowner = new showdown.Converter()
var posts_ele = document.getElementById('posts')
window.onload = async () => {
    try {
        const response = await fetch(`${Navbar.url}/get_recent_posts?page=0`, { method: 'GET' });
        const post_json = await response.json();
        // Author, Text, Date, Event?, Event_date, Category, Header
        for (let post of post_json) {
            let builtHTML = `
        <div class="border rounded" style="background-color: rgb(135, 142, 151); width:85%; padding: 10px; margin-left: 40px;">
            <div class="d-flex align-items-center justify-content-between">
                <h1 class="mb-0">${post[6]}</h1>
                <div>
                    <span class="ms-3 text-muted"> Posted: <strong>${post[2]}</strong></span>
                    <br>
                    <span class="ms-3 text-muted">by <strong>${post[0]}</strong></span> 
                </div>
            </div>
            <hr>
            ${showdowner.makeHtml(post[1])}
            </div>`
            posts_ele.innerHTML += builtHTML
        }
    } catch (error) {
        console.error("Error fetching posts:", error);
    }
};