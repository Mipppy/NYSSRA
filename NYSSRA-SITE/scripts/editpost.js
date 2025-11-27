document.addEventListener("DOMContentLoaded", async () => {
    await Navbar.LoadExtraHTML();

    if (!Navbar.isAdmin()) {
        window.location.replace("/");
        return;
    }

    var eventLocationInput = document.getElementById("event-location");
    var eventDescriptionTextarea = document.getElementById("event-description");
    var eventDateInput = document.getElementById("event-date");
    var eventStartTimeInput = document.getElementById("event-start-time");
    var eventLengthInput = document.getElementById("event-length");
    var tagsContainer = document.getElementById("tags-container");
    var eventDataContainer = document.getElementById("eventdata");
    var postName = document.getElementById("post-name");
    var addTag = document.getElementById("addTag");

    Navbar.loadPageFromURL().then((article_data) => {
        const simplemde = new SimpleMDE(Navbar.simpleMDEParameters);
        var tags = [];
        simplemde.value(article_data.md);
        postName.value = article_data.pd.postName;

        article_data.pd.tags.forEach((tag) => {
            var html = Navbar.generateTagFormat(
                tag,
                `<i class="bi bi-trash"></i>`
            );
            tags.push([tag, html]);
            tagsContainer.innerHTML += html;
        });

        addTag.addEventListener("click", function () {
            var promptData = prompt("Enter a tag...");
            if (!promptData) return;
            var html = Navbar.generateTagFormat(
                promptData,
                `<i class="bi bi-trash"></i>`
            );
            tags.push([promptData, html]);
            tagsContainer.innerHTML += html;
        });

        tagsContainer.addEventListener("click", function (e) {
            const ele = e.target.closest("a#tag");
            if (!ele) return;

            e.preventDefault();

            const _tag = ele.getAttribute("_tag");
            const index = tags.findIndex((t) => t[0] === _tag);
            if (index !== -1) tags.splice(index, 1);

            ele.remove();
        });

        if (article_data.pd.isEvent) {
            eventDateInput.value = article_data.pd.eventDate.trim();
            eventDescriptionTextarea.value =
                article_data.pd.advancedEventData.eventDescription;
            eventLocationInput.value =
                article_data.pd.advancedEventData.eventLocation;
            eventStartTimeInput.value = parseInt(
                article_data.pd.advancedEventData.eventStartHour
            );
            eventLengthInput.value = parseInt(
                article_data.pd.advancedEventData.eventLength
            );
            eventDataContainer.classList.remove("d-none");
        }

        document
            .getElementById("save_post_button")
            .addEventListener("click", () => {
                var payload = {
                    originalPostName: article_data.pd.postName.trim(),
                    postName: postName.value,
                    markdown: simplemde.value(),
                    tags: tags.map((t) => t[0]),
                    eventData: article_data.pd.eventData || {},
                    advancedEventData: article_data.pd.advancedEventData || {},
                };

                const form = new FormData();
                form.append("primary_data", JSON.stringify(payload));
                form.append("token", Navbar.login_token);

                fetch(`${Navbar.url}/editpost`, {
                    method: "POST",
                    body: form,
                    headers: {
                        Authorization: `Bearer ${Navbar.login_token}`,
                    },
                })
                    .then(async (res) => {
                        const json = await res.json();
                        if (json.status === "success") {
                            const urlParams = new URLSearchParams(
                                window.location.search
                            );
                            const article = urlParams.get("article");
                            location.replace(
                                `/article.html?article=${postName.value}`
                            );
                        }
                    })
                    .then(console.log)
                    .catch(console.error);
            });
    });
});
