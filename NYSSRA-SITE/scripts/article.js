Navbar.LoadExtraHTML()
var showdownInstance = new showdown.Converter({ openLinksInNewWindow: true })
var mdContentDiv = document.getElementById('md-content')
let article_data = null
// An async IIFE wouldn't work for this for some reason
Navbar.loadPageFromURL().then(e => {
    article_data = e
    console.log(e)
    if (e.md == '{"detail":"Not Found"}') {
        window.location.replace('/404.html')
    }
    mdContentDiv.innerHTML = showdownInstance.makeHtml(e.md)
})



