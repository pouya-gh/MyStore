import { PropsTable } from "./modules/item_props_table.js";

function initialSetup() {
    const table = PropsTable.getInstance();
    const input_element = document.getElementById("id_properties");
    input_element.style.display = 'none';
    input_element.parentNode.appendChild(table.table_element);
    table.table_element.style.display = '';
    document.querySelector("#props_new_button").onclick = addPropButtonPressed;
    turnPropJsonToTable();
}

function writePropTableToJson() {
    const table = PropsTable.getInstance();
    const rows = table.table_body.querySelectorAll("tr.prop_row");
    const props_map = new Map();
    for (const row of rows) {
        const cols = row.querySelectorAll("td");
        const name = cols[0].querySelector("input").value;
        const value = cols[1].querySelector("input").value;
        if (name && value) {
            props_map.set(name, value);
        }
    }
    const result = JSON.stringify(Object.fromEntries(props_map));
    const input_element = document.getElementById("id_properties");
    input_element.value = result;
}

function turnPropJsonToTable() {
    const table = PropsTable.getInstance();

    const input_element = document.getElementById("id_properties");
    const props_json = JSON.parse(input_element.value);

    if (!props_json) {
        return;
    }

    for (let [k, v] of Object.entries(props_json)) {
        const new_row = table.createNewPropRow(k, v, removePropButtonPressed, writePropTableToJson);
        table.table_body.insertBefore(new_row, table.last_row);
    }
}

function addPropButtonPressed(evnt) {
    evnt.preventDefault();
    const table = PropsTable.getInstance();
    const new_row = table.createNewPropRow("", "", removePropButtonPressed, writePropTableToJson);
    table.table_body.insertBefore(new_row, table.last_row);
    writePropTableToJson();
}

function removePropButtonPressed(evnt) {
    evnt.preventDefault();
    evnt.target.parentNode.parentNode.remove();
    writePropTableToJson();
}


window.addEventListener("load", initialSetup);