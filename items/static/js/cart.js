function load_cart_item_count() {
    const cart_elem = document.getElementById("cart_count");
    if (cart_elem) {
        fetch("/items/my_cart_count.json").then(async (response) => {
            const res_json = await response.json();
            if (response.ok) {
                cart_elem.innerHTML = res_json["count"];
            } 
        });
    }
}

function add_to_shopping_cart(event) {
    event.preventDefault();
    const csrf_token = event.target.querySelector("input[name='csrfmiddlewaretoken']").value;
    const url = event.target.action;
    const quantity = document.getElementById("id_quantity").value;
    const form_div = event.target.parentNode;
    const formData = new FormData();
    formData.append("quantity", quantity);
    let request = fetch(url, 
                    {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": csrf_token
                        },
                        body: formData
                    });
    request.then(async (response) => {
                    if (response.ok) {
                        form_div.innerHTML = "Item added to your cart!";
                        load_cart_item_count();
                    } else {
                        form_div.innerHTML += "Something went wrong!</br>";
                    }
                },
                () => {
                    form_div.innerHTML += "Something went wrong!</br>";
                });
}

function delete_from_shopping_cart(event) {
    event.preventDefault();
    const csrf_token = event.target.querySelector("input[name='csrfmiddlewaretoken']").value;
    const url = event.target.action;
    const table_row = event.target.parentNode.parentNode
    const request = fetch(
        url,
        {
            method: "POST",
            headers: {
                "X-CSRFToken": csrf_token
            }
        }
    );
    request.then(
        async (response) => {
            if (response.ok) {
                load_cart_item_count();
                table_row.remove();
            }
    });
}

function update_shopping_cart_item(event) {
    event.preventDefault();
    const csrf_token = event.target.querySelector("input[name='csrfmiddlewaretoken']").value;
    const url = event.target.action;
    const quantity = event.target.querySelector("input[name='quantity']").value;
    const form_col = event.target.parentNode;
    const table_row = form_col.parentNode;
    const formData = new FormData();
    formData.append("quantity", quantity);
    const request = fetch(url, 
                    {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": csrf_token
                        },
                        body: formData
                    });
    request.then(async (response) => {
                    if (response.ok) {
                        table_row.querySelector("td.itemquantity").innerHTML = quantity;
                    } else {
                        form_col.innerHTML += "Something went wrong!</br>";
                    }
                },
                () => {
                    form_col.innerHTML += "Something went wrong!</br>";
                });
}