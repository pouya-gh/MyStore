function _createNewFilterRow(key = "", value = "") {
    const parent_div = document.createElement("div");
    parent_div.className = "p-2 d-flex w-100 align-items-center justify-content-between";

    const div1 = document.createElement("div");
    div1.className = "col";
    const input1 = document.createElement("input");
    input1.type = 'text';
    input1.value = key;
    input1.classList.add("form-control", "filter-key");
    input1.placeholder = gettext('Key');
    div1.appendChild(input1);
    parent_div.appendChild(div1);

    const div2 = document.createElement("div");
    div2.className = "col";
    const input2 = document.createElement("input");
    input2.type = 'text';
    input2.value = value;
    input2.classList.add("form-control", "filter-value");
    input2.placeholder = gettext("Value");
    div2.appendChild(input2);
    parent_div.appendChild(div2);


    const div3 = document.createElement("div");
    div3.className = "col-auto";
    const addButton = document.createElement("button");
    addButton.type = 'button';
    addButton.classList.add("btn", "btn-danger", "remove-filter");
    const icon = document.createElement("i");
    icon.classList.add("bi", "bi-x-circle", "remove-filter");
    addButton.appendChild(icon);
    // addButton.innerHTML = '<i class="bi-x-circle me-1"></i>';
    div3.appendChild(addButton);
    parent_div.appendChild(div3);

    return parent_div;
}

document.addEventListener('DOMContentLoaded', function () {
    const filtersContainer = document.getElementById('filtersContainer');
    const addFilterButton = document.getElementById('addFilter');
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('search_query');
    const categoryDropdown = document.getElementById("categories_dropdown");
    const minPriceInput = document.getElementById("min-price");
    const maxPriceInput = document.getElementById("max-price");

    const urlParams = new URLSearchParams(window.location.search);
    const filters = JSON.parse(urlParams.get("filters"));
    const searchQ = urlParams.get("q");
    const categoryId = urlParams.get("category");
    const minPrice = urlParams.get("min_price");
    const maxPrice = urlParams.get("max_price");

    if (minPrice || maxPrice) {
        const filtersSection = document.getElementById('price-range-collapse');
        filtersSection.classList.add("show");
        document.getElementById('price-range-button').setAttribute("aria-expanded", "true");

        minPriceInput.value = minPrice;
        maxPriceInput.value = maxPrice;
    }

    if (filters) {
        const filtersSection = document.getElementById('more-options-collapse');
        filtersSection.classList.add("show");
        document.getElementById('filters-button').setAttribute("aria-expanded", "true");
        for (f of filters) {
            const filterPair = document.createElement('div');
            filterPair.classList.add('filter-pair', 'mb-3');
            filterPair.appendChild(_createNewFilterRow(f[0], f[1]));
            filtersContainer.appendChild(filterPair);
        }
    }
    if (searchQ) searchInput.value = searchQ;
    if (categoryId) categoryDropdown.value = categoryId;


    // Add Filter
    addFilterButton.addEventListener('click', function () {
        const filterPair = document.createElement('div');
        filterPair.classList.add('filter-pair', 'mb-3');
        filterPair.appendChild(_createNewFilterRow());
        filtersContainer.appendChild(filterPair);
    });

    // Remove Filter
    filtersContainer.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-filter')) {
            e.target.closest('.filter-pair').remove();
        }
    });

    // Form Submission
    searchForm.addEventListener('submit', function (e) {
        const filters = [];

      // Collect Filters
        document.querySelectorAll('.filter-pair').forEach(pair => {
            const key = pair.querySelector('.filter-key').value;
            const value = pair.querySelector('.filter-value').value;
            if (key && value) {
                filters.push([key, value]);
            }
        });

        if (filters.length > 0) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "filters";
            input.value = JSON.stringify(filters);
            e.target.appendChild(input);
        }

        if (minPriceInput.value) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "min_price";
            input.value = minPriceInput.value;
            e.target.appendChild(input);
        }

        if (maxPriceInput.value) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "max_price";
            input.value = maxPriceInput.value;
            e.target.appendChild(input);
        }

        return true;
    });
});