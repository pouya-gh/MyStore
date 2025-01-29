function _createNewFilterRow(key = "", value = "") {
    const parent_div = document.createElement("div");
    parent_div.className = "row";

    const div1 = document.createElement("div");
    div1.className = "col-md-3";
    const input1 = document.createElement("input");
    input1.type = 'text';
    input1.value = key;
    input1.classList.add("form-control", "filter-key");
    input1.placeholder = "Key";
    div1.appendChild(input1);
    parent_div.appendChild(div1);

    const div2 = document.createElement("div");
    div2.className = "col-md-3";
    const input2 = document.createElement("input");
    input2.type = 'text';
    input2.value = value;
    input2.classList.add("form-control", "filter-value");
    input2.placeholder = "Value";
    div2.appendChild(input2);
    parent_div.appendChild(div2);


    const div3 = document.createElement("div");
    div3.className = "col-auto";
    const addButton = document.createElement("button");
    addButton.type = 'button';
    addButton.classList.add("btn", "btn-danger", "remove-filter");
    addButton.innerHTML = "Remove";
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

    const urlParams = new URLSearchParams(window.location.search);
    const filters = JSON.parse(urlParams.get("filters"));
    const searchQ = urlParams.get("q");
    const categoryId = urlParams.get("category");
    if (filters) {
        const filtersSection = document.getElementById('filters_section'); 
        filtersSection.classList.add("show");
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

        return true;
    });
});