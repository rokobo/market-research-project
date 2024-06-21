if (!window.dash_clientside) {
    window.dash_clientside = {};
}

const PRODUCTS = [
    "acucar", "arroz", "cafe", "farinha", "feijao", "leite", "manteiga",
    "soja", "banana", "batata", "tomate", "carne", "pao"
];
const FIELDS = ["brand", "price", "quantity", "obs"];

window.dash_clientside.clientside = {
    save_state: function(_1, _2, load_flag, name, date, establishment, observations, ...products) {
        if (load_flag === null) {return window.dash_clientside.no_update}

        let data = [];
        data.push({'first': [name, date, establishment]});
        data.push({'observations': observations});

        for (let i = 0; i < products.length; i++) {
            let product_name = PRODUCTS[i];
            let product = products[i];

            for (let row of product) {
                let row_id = row.props.id;
                let val = row.props.children;
                let vals = {};

                for (let idx = 0; idx < val.length; idx++) {
                    try {vals[idx] = val[idx].props.children.props.value} catch (error) {}
                }

                let values;
                switch (val.length) {
                    case 4:
                        values = [vals[1], vals[2], vals[3], null];
                        break;
                    case 3:
                        if (typeof vals[1] === 'string') {
                            values = [vals[1], vals[2], null, null];
                        } else {
                            values = [null, vals[1], null, vals[2]];
                        }
                        break;
                    default:
                        values = [null, null, null, null];
                }
                data.push({"container": product_name, "values": values, "row_id": row_id.split("-").slice(-1)[0]});
            }
        }
        return data;
    },
    validate_args_1: function (_1, _2, _3, ...values) {
        return values.map(v => (v !== null && v !== "" ? "correct" : "wrong"));
    },
    validate_args_2: function (_1, ...values) {
        let args = values.slice(values.length/2, values.length);
        let validations = [];
        let validations2 = [];
        let status1 = [];
        let status2 = [];

        // Individual validations
        for (var i = 0; i < args.length; i += 4) {
            let [br, pr, qn, obs] = args.slice(i, i + 4);
            let size = pr.length;

            validations.push(br.map(brand => typeof brand == 'string'));
            validations.push(pr.map(price => typeof price === 'number' && !isNaN(price)));
            validations.push(qn.map(() => true));
            validations.push(obs.map(() => true));
        };

        // Section validations
        for (let i = 0; i < validations.length; i += 4) {
            const val = validations.slice(i, i + 4);
            if (val.every(sublist => sublist.every(v => v))) {
                status1.push("Correto");
                status2.push("success");
            } else {
                status1.push("Erro");
                status2.push("danger");
            }
        };

        // Transform to appropriate classnames
        validations = validations.map(sublist => sublist.map(v => v ? "correct" : "wrong"));
        validations = validations.concat(status1).concat(status2);

        // Update save button status
        if (status1.every(v => v === "Correto")) {validations = validations.concat([false, "success"])}
        else {validations = validations.concat([true, "danger"])}
        return validations;
    },
    delete_product_row: function (...values) {
        var ctx = dash_clientside.callback_context.triggered_id;
        if (values.slice(0, PRODUCTS.length).every(sublist => sublist.every(v => typeof v === "undefined"))) {
            return window.dash_clientside.no_update;
        }

        var children_states = values.slice(PRODUCTS.length);
        var contextType = ctx.type.slice(7);
        var prop_id = `${contextType}-product-row-${ctx.index}`
        var index = PRODUCTS.indexOf(contextType);

        var patched_children = Array(PRODUCTS.length).fill(window.dash_clientside.no_update);
        var children = children_states[index];

        for (let i = 0; i < children.length; i++) {
            var child = children[i];
            // Find correct row by row index and context index
            if (child.props.id === prop_id) {
                // Remove the child at index i
                children.splice(i, 1);
                break;
            }
        }
        patched_children[index] = children;
        return patched_children;
    }
}
