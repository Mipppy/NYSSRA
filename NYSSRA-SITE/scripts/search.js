Navbar.LoadExtraHTML()

var URLParams = null;

document.addEventListener("DOMContentLoaded", async () => {
    URLParams = new URLSearchParams(window.location.href)
    var data = new FormData()
    data.append("tags", URLParams.get('tags'))
    data.append("query", URLParams.get('query'))
    try {
        const response = await fetch("/search", {
            method: "POST",
            body: data,
        });
        const json = await response.json();
        console.log("Search results:", json);
    } catch (error) {
    }
})