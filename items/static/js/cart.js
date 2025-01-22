function load_cart_item_count() {
    let cart_elem = document.getElementById("cart_count");
    if (cart_elem) {
        fetch("/items/my_cart_count.json").then(async (response) => {
            let res_json = await response.json();
            if (response.ok) {
                let message = res_json["count"] > 0 ? " (" + res_json["count"] + ")" : ""
                cart_elem.innerHTML = message;
            } 
        });
    }
}

function add_to_shopping_cart(event, csrf_token) {
    event.preventDefault();
    let url = event.target.action;
    let quantity = document.getElementById("id_quantity").value;
    let form_div = event.target.parentNode;
    let formData = new FormData();
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

function delete_from_shopping_cart(event, url, csrf_token) {
    let table_row = event.target.parentNode.parentNode
    let request = fetch(
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

function update_shopping_cart_item(event, csrf_token) {
    event.preventDefault();
    let url = event.target.action;
    let quantity = event.target.childNodes[1].value;
    let form_col = event.target.parentNode;
    let table_row = form_col.parentNode;
    let formData = new FormData();
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
                        table_row.querySelector("td.itemquantity").innerHTML = quantity;
                    } else {
                        form_col.innerHTML += "Something went wrong!</br>";
                    }
                },
                () => {
                    form_col.innerHTML += "Something went wrong!</br>";
                });
}