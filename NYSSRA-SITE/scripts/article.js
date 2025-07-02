document.addEventListener("DOMContentLoaded", () => {
    Navbar.LoadExtraHTML();

    var showdownInstance = new showdown.Converter({ openLinksInNewWindow: true });
    var mdContentDiv = document.getElementById('md-content');
    var articleTitleEle = document.getElementById('article_title');
    var articleDateEle = document.getElementById('article_date');
    var articleAuthorEle = document.getElementById('article_author');
    var articleEventDateEle = document.getElementById('article_event_date');
    var articleEventContainer = document.getElementById('event_container');
    var articleTagsContainer = document.getElementById('article_tags');
    var articleEventCalendarLink = document.getElementById('event_calendar_link');
    let article_data = null;

    Navbar.loadPageFromURL().then(e => {
        article_data = e;
        if (e.md == '{"detail":"Not Found"}') {
            window.location.replace('/404.html');
        }
        articleTitleEle.innerText = e.pd.postName;
        articleDateEle.innerText = Navbar.turnToCorrectDate(e.pd.date).trim();
        articleAuthorEle.innerText = e.pd.author.trim();

        if (e.pd.isEvent) {
            articleEventContainer.classList.remove('d-none');
            articleEventContainer.classList.add('d-flex');
            articleEventDateEle.innerText = e.pd.eventDate;

            // Ensure this element exists before setting href
            if (articleEventCalendarLink) {
                articleEventCalendarLink.href = `/calendar.html?event=${e.article}`;
            }
        }

        articleTagsContainer.innerHTML = '';
        e.pd.tags.forEach(tag => articleTagsContainer.innerHTML += Navbar.generateTagFormat(tag));

        mdContentDiv.innerHTML = showdownInstance.makeHtml(e.md);
    });
});
