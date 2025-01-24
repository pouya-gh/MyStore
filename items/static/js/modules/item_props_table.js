export const PropsTable = (function () {
    let table;

    class PropsTable {
        constructor() {
            if (!table) {
                this.table_element = document.getElementById("props_table");
                this.last_row = this.table_element.querySelector("#props_last_row");
                this.new_prop_button = this.last_row.querySelector("#props_new_button");
                this.table_body = this.table_element.querySelector('tbody');
            }
        }

        createNewPropRow(prop_name,
                         prop_value,
                         delete_button_event, 
                         input_change_event) {
            const new_row = document.createElement("tr");
            new_row.className = "prop_row";

            const name_column = document.createElement("td");
            const name_input = document.createElement("input");
            name_input.type = 'text';
            name_input.value = prop_name;
            name_input.onchange = input_change_event;
            name_column.appendChild(name_input);
            new_row.appendChild(name_column);

            const value_column = document.createElement("td");
            const value_input = document.createElement("input");
            value_input.type = 'text';
            value_input.value = prop_value;
            value_input.onchange = input_change_event;
            value_column.appendChild(value_input);
            new_row.appendChild(value_column);

            const button_column = document.createElement("td");
            const delete_button = document.createElement("button");
            delete_button.className = "delete_prop";
            delete_button.onclick = delete_button_event;
            const text = document.createTextNode("Delete");
            delete_button.appendChild(text);
            button_column.appendChild(delete_button);
            new_row.appendChild(button_column);


            return new_row;
        }

        static getInstance() {
            if (!table) {
                table = new PropsTable();
            }

            return table;
        }
    }


    return PropsTable;
})();