(async () => {
  await Navbar.LoadExtraHTML();
  if (!Navbar.isAdmin()) {
    window.location.href = '/404.html'
  }
})();



document.addEventListener("DOMContentLoaded", () => {
  const simplemde = new SimpleMDE({
    element: document.getElementById("markdown-editor"),
    spellChecker: true,
    placeholder: "Write your Markdown content here...",
    showIcons: ["code", "table"],

  });

  const imageInput = document.getElementById("image-upload");
  const previewContainer = document.getElementById("image-preview-container");
  const postNameInput = document.getElementById("post-name");
  const tagsInput = document.getElementById("post-tags");
  const postButton = document.getElementById("post_button");

  let uploadedImages = [];

  imageInput.addEventListener("change", () => {
    const files = Array.from(imageInput.files);
    const postName = postNameInput.value.trim().toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9\-]/g, "");

    if (!postName) {
      alert("Please enter a valid post name before uploading images.");
      imageInput.value = "";
      return;
    }

    files.forEach((file) => {
      if (!file.type.startsWith("image/")) return;

      const reader = new FileReader();

      reader.onload = (e) => {
        const wrapper = document.createElement("div");
        wrapper.className = "position-relative d-inline-block";

        const index = uploadedImages.length;
        uploadedImages.push(file);

        const img = document.createElement("img");
        img.src = e.target.result;
        img.className = "img-thumbnail";
        img.style.maxHeight = "100px";
        img.style.cursor = "pointer";

        img.addEventListener("click", () => {
          const fileExt = file.name.split('.').pop().toLowerCase();
          const safeExt = ['png', 'jpg', 'jpeg', 'gif'].includes(fileExt) ? fileExt : 'png';
          const markdown = `<img src="${Navbar.url}/static/${postName}/${index}.${safeExt}" class="md_pulled_image">`;

          const cm = simplemde.codemirror;
          const cursor = cm.getCursor();
          cm.replaceRange(markdown, cursor);
        });

        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.innerHTML = "&times;";
        removeBtn.className = "btn btn-sm btn-danger btn-remove position-absolute top-0 end-0";
        removeBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          wrapper.remove();
          uploadedImages[index] = null;
        });

        wrapper.appendChild(img);
        wrapper.appendChild(removeBtn);
        previewContainer.appendChild(wrapper);
      };

      reader.readAsDataURL(file);
    });
  });

  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  [...tooltipTriggerList].forEach(el => new bootstrap.Tooltip(el));

  postButton.addEventListener("click", () => {
    const postNameRaw = postNameInput.value.trim();
    const tagsRaw = tagsInput.value.trim();
    const markdownRaw = simplemde.value().trim();

    const tags = tagsRaw.split(",").map(t => t.trim()).filter(Boolean);
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

    if (hasError) {
      return;
    }

    const validImages = uploadedImages.filter(Boolean);

    const formData = new FormData();
    let tag_str = ''
    for (let tag of tags) {
      tag_str += `${tag},`
    }
    formData.append("postName", slug);
    formData.append("postNameRaw", postNameRaw)
    formData.append("markdown", markdownRaw);
    formData.append("tags", tag_str);
    formData.append("token", Navbar.login_token)
    formData.append("eventData", JSON.stringify({
      isEvent: document.getElementById('is-event-toggle').checked,
      eventDate: document.getElementById('event-date').value
    })); validImages.forEach((file) => {
      formData.append("files", file);
    });


    fetch(`${Navbar.url}/create-post`, {
      method: "POST",
      body: formData,
    })
      .then(response => {
        if (!response.ok) throw new Error("Failed to save post.");
        return response.text();
      })
      .then(data => {
        alert("Post created successfully!");
        window.location.href = `/article.html?article=${data.replaceAll('"', '')}`
      })
      .catch(err => {
        console.error(err);
        alert("There was an error creating the post.");
      });
  });

});

/*
This will need:
Post Body   !
Name   !
Tags   !
Author
Date  !
Calender
Option to add to calender
Image upload.    !
*/