Navbar.LoadExtraHTML();

let URLParams = null;
let searchData = null;
let articleContainer = null;

document.addEventListener("DOMContentLoaded", async () => {
    URLParams = new URLSearchParams(window.location.search);
    articleContainer = document.getElementById("article_container");

    const tags = URLParams.get('tags') || "";
    const query = URLParams.get('query') || "";

    const formData = new FormData();
    formData.append("tags", tags);
    formData.append("query", query);

    try {
        const response = await fetch(`${Navbar.url}/search`, {
            method: "POST",
            body: formData,
        });

        const json = await response.json();
        searchData = json.results || [];

        document.getElementById("articles_found").textContent = searchData.length;

        const inputTags = new Set(tags.split(',').map(t => t.trim().toLowerCase()).filter(Boolean));
        const relatedTagSet = new Set();

        for (const article of searchData) {
            const tagBadges = article.tags.map(tag => {
                const normalizedTag = tag.toLowerCase();
                if (!inputTags.has(normalizedTag)) {
                    relatedTagSet.add(tag);
                }
                return Navbar.generateTagFormat(tag)
            }).join("");
            articleContainer.innerHTML += `
                <div class="card shadow-lg border-0">
                    <div class="card-body">
                        <h5 class="card-title mb-1">${article.post_name_raw}</h5>
                        <p class="mb-1 text-muted"><i class="bi bi-calendar-event"></i> ${Navbar.turnToCorrectDate(article.post_date)}</p>
                        <p class="mb-1 text-muted"><i class="bi bi-person"></i> ${article.author}</p>
                        <div>${tagBadges}</div>
                        <a href="/article.html?article=${article.post_name}" class="btn btn-sm btn-outline-primary mt-3">Read More</a>
                    </div>
                </div>
            `;
        }

        const relatedTagsContainer = document.querySelector(".related_tags_container");
        if (relatedTagSet.size > 0) {
            relatedTagsContainer.innerHTML = [...relatedTagSet]
                .map(tag => Navbar.generateTagFormat(tag))
                .join("");
        } else {
            relatedTagsContainer.innerHTML = `<span class="text-muted">No related tags</span>`;
        }

    } catch (error) {
        console.error("Search failed:", error);
        articleContainer.innerHTML = `<div class="alert alert-danger">Error loading results.</div>`;
    }
});
