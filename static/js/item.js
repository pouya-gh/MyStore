function load_current_user_provider_profiles_into_selector() {
    const request = fetch("/current_user_provider_profiles.json");
    request.then(async (response) => {
        if (!response.ok) { return; }

        const response_body = await response.json();
        const profiles = response_body["providers_list"];
        const selector = document.getElementById("id_provider");

        const selected_node_value = document.querySelector("option[selected='']").value;
        selector.innerHTML = "";

        if (selected_node_value == "") {
            const def_option = document.createElement("option");
            def_option.value = "";
            def_option.selected = ""
            def_option.appendChild(document.createTextNode("-----"));
            selector.appendChild(def_option);
        }

        for (let p of profiles) {
            const option = document.createElement("option");
            option.value = p['id'];
            if (selected_node_value == p['id']) {
                option.selected = "";
            }
            
            const node = document.createTextNode(p["name"]);
            option.appendChild(node);

            selector.appendChild(option);
        }

        selector.value = selected_node_value;
    });
    
}