(function () {
    const searchForm = document.querySelector("[data-youtube-search-form]");

    if (!searchForm) {
        return;
    }

    const resultsContainer = document.querySelector("[data-search-results]");
    const errorBox = document.querySelector("[data-search-error]");
    const loadingBox = document.querySelector("[data-search-loading]");
    const submitButton = searchForm.querySelector("button[type='submit']");
    const csrfInput = searchForm.querySelector("input[name='csrfmiddlewaretoken']");

    function setError(message) {
        if (!errorBox) {
            return;
        }

        errorBox.textContent = message || "";
        errorBox.classList.toggle("hidden", !message);
    }

    function setLoading(isLoading) {
        if (loadingBox) {
            loadingBox.classList.toggle("hidden", !isLoading);
        }

        if (submitButton) {
            submitButton.disabled = isLoading;
            submitButton.textContent = isLoading ? "Searching..." : "Search video";
        }
    }

    function createElement(tagName, className, text) {
        const element = document.createElement(tagName);

        if (className) {
            element.className = className;
        }

        if (text) {
            element.textContent = text;
        }

        return element;
    }

    function createSelect(name, placeholder, items, labelKey) {
        const select = createElement("select", "form-control format-select");
        const emptyOption = document.createElement("option");

        select.name = name;
        select.required = name === "format";
        emptyOption.value = "";
        emptyOption.textContent = placeholder;
        select.appendChild(emptyOption);

        items.forEach((item) => {
            const option = document.createElement("option");
            option.value = item.id;
            option.textContent = item[labelKey];
            select.appendChild(option);
        });

        return select;
    }

    function createAddForm(video, formats, categories, index) {
        const form = createElement("form", "site-form search-add-form");
        form.method = "post";

        if (csrfInput) {
            const csrfClone = document.createElement("input");
            csrfClone.type = "hidden";
            csrfClone.name = "csrfmiddlewaretoken";
            csrfClone.value = csrfInput.value;
            form.appendChild(csrfClone);
        }

        [
            ["form_type", "download"],
            ["title", video.title],
            ["youtube_url", video.youtube_url],
        ].forEach(([name, value]) => {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = name;
            input.value = value;
            form.appendChild(input);
        });

        form.appendChild(createSelect("format", "Choose format", formats, "label"));
        form.appendChild(createSelect("category", "Choose category", categories, "name"));

        const rights = createElement("div", "rights-checkbox compact-rights");
        const checkbox = document.createElement("input");
        const label = document.createElement("label");
        const checkboxId = "rights_ajax_" + index;

        checkbox.type = "checkbox";
        checkbox.name = "rights_confirmed";
        checkbox.id = checkboxId;
        checkbox.className = "rights-input";
        checkbox.required = true;

        label.htmlFor = checkboxId;
        label.textContent = "I confirm that I have the right to download this video";

        rights.appendChild(checkbox);
        rights.appendChild(label);
        form.appendChild(rights);

        const button = createElement("button", "", "Add and convert");
        button.type = "submit";
        form.appendChild(button);

        return form;
    }

    function createResultCard(video, formats, categories, index) {
        const card = createElement("div", "search-result-card");

        if (video.thumbnail) {
            const imageLink = createElement("a", "search-thumb-link");
            const image = document.createElement("img");

            imageLink.href = video.youtube_url;
            imageLink.target = "_blank";
            imageLink.rel = "noopener noreferrer";
            image.src = video.thumbnail;
            image.alt = video.title;
            image.className = "search-result-image";

            imageLink.appendChild(image);
            card.appendChild(imageLink);
        } else {
            card.appendChild(createElement("div", "product-image-placeholder", "No image"));
        }

        const content = createElement("div", "search-result-content");
        const title = createElement("h3", "", video.title);
        const meta = createElement("div", "search-result-meta");
        const link = createElement("a", "video-link", "Open on YouTube");

        if (video.channel) {
            meta.appendChild(createElement("span", "", video.channel));
        }

        if (video.duration) {
            meta.appendChild(createElement("span", "", video.duration));
        }

        link.href = video.youtube_url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";

        content.appendChild(title);
        content.appendChild(meta);
        content.appendChild(link);
        content.appendChild(createAddForm(video, formats, categories, index));
        card.appendChild(content);

        return card;
    }

    function renderResults(payload) {
        resultsContainer.replaceChildren();

        if (!payload.results || payload.results.length === 0) {
            resultsContainer.appendChild(createElement("div", "empty-search", "No videos found. Try another search."));
            return;
        }

        payload.results.forEach((video, index) => {
            resultsContainer.appendChild(createResultCard(
                video,
                payload.formats || [],
                payload.categories || [],
                index + 1
            ));
        });
    }

    searchForm.addEventListener("submit", function (event) {
        event.preventDefault();
        setError("");
        setLoading(true);

        fetch(searchForm.dataset.searchUrl, {
            method: "POST",
            body: new FormData(searchForm),
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
            .then((response) => response.json())
            .then((payload) => {
                if (!payload.ok) {
                    throw new Error(payload.error || "Could not search YouTube right now.");
                }

                renderResults(payload);
            })
            .catch((error) => {
                resultsContainer.replaceChildren();
                setError(error.message);
            })
            .finally(() => {
                setLoading(false);
            });
    });
}());
