Navbar.LoadExtraHTML()
var showdownInstance = new showdown.Converter()
(async () => {
    var mdContentDiv = document.getElementById('md-content')
    var html = showdownInstance.makeHtml(await Navbar.loadPageFromURL())
    mdContentDiv.innerHTML = html
})
