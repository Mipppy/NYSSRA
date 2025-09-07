document.addEventListener('DOMContentLoaded', async () => {
    await Navbar.LoadExtraHTML();

    if (!Navbar.isAdmin()) {
        window.location.replace('/');
        return;
    }

    var eventLocationInput = document.getElementById('event-location');
    var eventDescriptionTextarea = document.getElementById('event-description');
    var eventDateInput = document.getElementById('event-date');
    var eventStartTimeInput = document.getElementById('event-start-time');
    var eventLengthInput = document.getElementById('event-length');
    var tagsContainer = document.getElementById('tags-container');
    var eventDataContainer = document.getElementById('eventdata');
    var postName = document.getElementById('post-name');
    var addTag = document.getElementById('addTag');

    Navbar.loadPageFromURL().then(article_data => {
        const simplemde = new SimpleMDE(Navbar.simpleMDEParameters);
        var tags = []; 
        simplemde.value(article_data.md);
        postName.value = article_data.pd.postName;

        article_data.pd.tags.forEach(tag => {
            var html = Navbar.generateTagFormat(tag, `<i class="bi bi-trash"></i>`);
            tags.push([tag, html]);
            tagsContainer.innerHTML += html;
        });

        addTag.addEventListener('click', function () {
            var promptData = prompt('Enter a tag...');
            if (!promptData) return; 
            var html = Navbar.generateTagFormat(promptData, `<i class="bi bi-trash"></i>`);
            tags.push([promptData, html]);
            tagsContainer.innerHTML += html;
        });

        tagsContainer.addEventListener('click', function(e) {
            const ele = e.target.closest('a#tag');
            if (!ele) return;

            e.preventDefault()

            const _tag = ele.getAttribute('_tag');
            const index = tags.findIndex(t => t[0] === _tag);
            if (index !== -1) tags.splice(index, 1);

            ele.remove();
        });

        if (article_data.pd.isEvent) {
            eventDateInput.value = article_data.pd.eventDate;
            eventDescriptionTextarea.value = article_data.pd.advancedEventData.eventDescription;
            eventLocationInput.value = article_data.pd.advancedEventData.eventLocation;
            eventStartTimeInput.value = parseInt(article_data.pd.advancedEventData.eventStartHour);
            eventLengthInput.value = parseInt(article_data.pd.advancedEventData.eventLength);
            eventDataContainer.classList.remove('d-none');
        }

        document.getElementById("save_post_button").addEventListener("click", () => {

            var data = {
                newMarkdown: simplemde.value(),
                postName: postName.value,
                tags: tags.map(subArr => subArr[0]),
                eventDate: eventDateInput.value,
                event: {
                    eventDescription: eventDescriptionTextarea.value,
                    eventLocation: eventLocationInput.value,
                    eventStartHour: eventStartTimeInput.value,
                    eventLength: eventLengthInput.value
                }
            };
            console.log(data)
            // window.location.replace(`/article.html?article=${article_data.article}`);
        });
    });
});
