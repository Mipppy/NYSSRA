Navbar.LoadExtraHTML()
var showdownInstance = new showdown.Converter()
var mdContentDiv = document.getElementById('md-content')
async function loadPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const article = urlParams.get("article")
    if (!article || article === '' || article === null) {
        alert('Invalid article.')
        location.replace('/')
        return
    }
    const md_request = await fetch(`${Navbar.url}/pages/${article}.md`)
    const md_text = await md_request.text()
    const new_html = showdownInstance.makeHtml(md_text)
    mdContentDiv.innerHTML = new_html
}
loadPage()