(async () => {
    await Navbar.LoadExtraHTML();
    if (!Navbar.isAdmin()) {
        window.location.href = "/404.html";
    }
})();

document.addEventListener("DOMContentLoaded", async () => {
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

    const simplemde = new SimpleMDE(Navbar.simpleMDEParameters);

    const imageInput = document.getElementById("image-upload");
    const previewContainer = document.getElementById("image-preview-container");
    const postNameInput = document.getElementById("post-name");
    const tagsInput = document.getElementById("post-tags");
    const postButton = document.getElementById("post_button");
    let uploadedFiles = [];

    imageInput.addEventListener("change", () => {
        const files = Array.from(imageInput.files);
        const postName = postNameInput.value.trim().toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9\-]/g, "");

        if (!postName) {
            alert("Please enter a valid post name before uploading files.");
            imageInput.value = "";
            return;
        }

        files.forEach((file) => {
            if (file.size > MAX_FILE_SIZE) {
                alert(`File "${file.name}" is too large. Maximum size is 5 MB.`);
                return;
            }

            const reader = new FileReader();
            const index = uploadedFiles.length;
            uploadedFiles.push(file);

            reader.onload = (e) => {
                const wrapper = document.createElement("div");
                wrapper.className = "position-relative d-inline-block me-2";

                if (file.type.startsWith("image/")) {
                    const img = document.createElement("img");
                    img.src = e.target.result;
                    img.className = "img-thumbnail";
                    img.style.maxHeight = "100px";
                    img.style.cursor = "pointer";

                    img.addEventListener("click", () => {
                        const ext = file.name.split(".").pop().toLowerCase();
                        const markdown = `<img src="${Navbar.url}/static/${postName}/${index}.${ext}" class="md_pulled_image">`;
                        simplemde.codemirror.replaceRange(markdown, simplemde.codemirror.getCursor());
                    });

                    wrapper.appendChild(img);
                } else {
                    const icon = document.createElement("div");
                    icon.className = "d-flex flex-column align-items-center justify-content-center border p-2 rounded bg-light text-center";
                    icon.style.width = "80px";
                    icon.style.height = "100px";
                    icon.style.cursor = "pointer";
                    icon.innerHTML = `<i class="bi bi-file-earmark" style="font-size: 1.5rem;"></i><small class="text-break">${file.name}</small>`;

                    icon.addEventListener("click", () => {
                        const ext = file.name.split(".").pop().toLowerCase();
                        const markdown = `[${file.name}](${Navbar.url}/static/${postName}/${index}.${ext})`;
                        simplemde.codemirror.replaceRange(markdown, simplemde.codemirror.getCursor());
                    });

                    wrapper.appendChild(icon);
                }

                const removeBtn = document.createElement("button");
                removeBtn.type = "button";
                removeBtn.innerHTML = "&times;";
                removeBtn.className = "btn btn-sm btn-danger btn-remove position-absolute top-0 end-0";
                removeBtn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    wrapper.remove();
                    uploadedFiles[index] = null;
                });

                wrapper.appendChild(removeBtn);
                previewContainer.appendChild(wrapper);
            };

            reader.readAsDataURL(file);
        });
    });

    const toggle = document.getElementById("is-event-toggle");
    const advancedContainer = document.getElementById("advanced-event-container");
    const advancedBtn = document.getElementById("advanced-event-button");
    const advancedFields = document.getElementById("advanced-event-fields");

    const dateContainer = document.getElementById("event-date-container");
    toggle.checked = false;
    advancedContainer.classList.add("d-none");
    advancedFields.classList.add("d-none");
    toggle.addEventListener("change", () => {
        if (toggle.checked) {
            dateContainer.classList.remove("d-none");
            advancedContainer.classList.remove("d-none");
        } else {
            dateContainer.classList.add("d-none");
            advancedContainer.classList.add("d-none");
            advancedFields.classList.add("d-none");
        }
    });

    advancedBtn.addEventListener("click", () => {
        advancedFields.classList.toggle("d-none");

        if (advancedFields.classList.contains("d-none")) {
            advancedBtn.innerHTML = "Advanced Event Config";
        } else {
            advancedBtn.innerHTML = "Hide Advanced Event Config";
        }
    });

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].forEach((el) => new bootstrap.Tooltip(el));

    postButton.addEventListener("click", () => {
        const postNameRaw = postNameInput.value.trim();
        const tagsRaw = tagsInput.value.trim();
        const markdownRaw = simplemde.value().trim();

        const tags = tagsRaw.split(",").map((t) => t.trim()).filter(Boolean);
        const slug = postNameRaw.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9\-]/g, "");

        postNameInput.classList.remove("is-invalid");
        tagsInput.classList.remove("is-invalid");
        document.querySelector(".editor-toolbar").classList.remove("is-invalid");

        let hasError = false;

        if (!postNameRaw) {
            postNameInput.classList.add("is-invalid");
            hasError = true;
        }

        if (!tags.length) {
            tagsInput.classList.add("is-invalid");
            hasError = true;
        }

        if (!markdownRaw) {
            document.querySelector(".editor-toolbar").classList.add("is-invalid");
            hasError = true;
        }

        if (hasError) return;

        const validFiles = uploadedFiles.filter(Boolean);
        const formData = new FormData();
        formData.append("postName", slug);
        formData.append("postNameRaw", postNameRaw);
        formData.append("markdown", markdownRaw);
        formData.append("tags", tags.join(","));
        formData.append("token", Navbar.login_token);
        formData.append("eventData", JSON.stringify({
            isEvent: +toggle.checked,
            eventDate: document.getElementById("event-date").value
        }));
        formData.append("advancedEventData", JSON.stringify({
            eventLocation: document.getElementById('event-location').value || 0,
            eventDescription: document.getElementById('event-description').value || 0,
            eventRecurrence: document.getElementById('event-recurrence').value || 0,
            eventStartHour: document.getElementById('event-start-hour').value || 0,
            eventLength: document.getElementById('event-length').value || 0            
        }))

        validFiles.forEach((file) => {
            formData.append("files", file);
        });

        fetch(`${Navbar.url}/create-post`, {
            method: "POST",
            body: formData,
        })
            .then((res) => {
                if (!res.ok) throw new Error("Failed to save post.");
                return res.text();
            })
            .then((data) => {
                alert("Post created successfully!");
                window.location.href = `/article.html?article=${data.replaceAll('"', '')}`;
            })
            .catch((err) => {
                console.error(err);
                alert("There was an error creating the post.");
            });
    });
});
