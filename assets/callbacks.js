if (!window.dash_clientside) {window.dash_clientside = {}}
const CFG = JSON.parse(localStorage.getItem('config'));
const groupValidations2=(lists,keys)=>lists.reduce((acc,_,i)=>{if(i%4===0&&keys[i/4]){acc[keys[i/4]]=lists.slice(i,i+4).flat()}return acc},{});

window.dash_clientside.clientside = {
clear_contents: function(click) {
    if (typeof click !== 'number') {return window.dash_clientside.no_update};
    console.log("CALL clear contents (", dash_clientside.callback_context.triggered_id, ")");
    return [];
},
close_modal: function(click) {
    if (typeof click !== 'number') {return window.dash_clientside.no_update};
    return false;
},
save_state: function(_1, load_flag, name, date, establishment, observations, ...products) {
    if (load_flag === null) {return window.dash_clientside.no_update}
    let data = [];
    data.push({'first': [name, date, establishment]});
    data.push({'observations': observations});
    for (let i = 0; i < products.length; i++) {
        let product_name = CFG.products[i];
        let product = products[i];
        for (let prod_row of product) {
            let row_id = prod_row.props.id;
            let val = prod_row.props.children;
            let vals = {};
            for (let idx = 0; idx < val.length; idx++) {
                try {vals[idx] = val[idx].props.children.props.value} catch (error) {}}
            let row = [null, null, null, null];
            switch (val.length) {
                case 4:
                    row = [vals[1], vals[2], vals[3], null];
                    break;
                case 3:
                    if (product_name == 'banana') {row = [vals[1], vals[2], null, null]}
                    else {row = [null, vals[1], null, vals[2]]}
                    break;
                default:
                    row = [null, null, null, null];
            }
            data.push({"container": product_name, "values": row, "row_id": row_id.split("-").slice(-1)[0]});
        }
    };
    console.log("CALL save data (", dash_clientside.callback_context.triggered_id, ")", data);
    return data;
},
validate_args: function (_1, name, date, est, ...vals) {
    var first_args = vals.splice(-3);
    var slice_length = vals.length - CFG.products.length;
    var second_args = vals.slice(slice_length/2 + CFG.products.length);
    var validations = [];
    var status1 = [];
    var status2 = [];
    // Individual validations
    for (var i = 0; i < second_args.length; i += 4) {
        var [br, pr, qn, obs] = second_args.slice(i, i + 4);
        validations.push(br.map(brand => typeof brand == 'string'));
        validations.push(pr.map(price => typeof price === 'number' && !isNaN(price)));
        validations.push(qn.map(() => true));
        validations.push(obs.map(() => true));
    };
    // Section validations
    for (var i = 0; i < validations.length; i += 4) {
        const val = validations.slice(i, i + 4);
        if (val.every(sublist => sublist.every(v => v))) {
            if (val[1].length >= CFG.product_rows[CFG.products[i/4]]) {
                status1.push("Completo");
                status2.push("success");
            } else {
                status1.push("Okay");
                status2.push("warning");
            }
        } else {
            status1.push("Faltando");
            status2.push("danger");
        }
    };
    // Transform to appropriate classnames
    validations = validations.map(sublist => sublist.map(v => v ? "correct" : "wrong"));
    console.log("CALL validation (", dash_clientside.callback_context.triggered_id, ")", first_args, groupValidations2(validations, CFG.products));
    validations = validations.concat(status1).concat(status2).concat(
        first_args.map(v => (v !== null && v !== "" ? "correct" : "wrong")));
    validations.push("");
    return validations;
},
delete_product_row: function (...vals) {
    var ctx = dash_clientside.callback_context.triggered_id;
    if (vals.slice(0, CFG.products.length).every(sublist => sublist.every(v => typeof v === "undefined"))) {
        return window.dash_clientside.no_update;}
    var children_states = vals.slice(CFG.products.length);
    var contextType = ctx.type.slice(7);
    var prop_id = `${contextType}-product-row-${ctx.index}`
    var index = CFG.products.indexOf(contextType);
    var patched_children = Array(CFG.products.length).fill(window.dash_clientside.no_update);
    var children = children_states[index];
    for (let i = 0; i < children.length; i++) {
        var child = children[i];
        // Find row by row index and context index, remove child at index i
        if (child.props.id === prop_id) {children.splice(i, 1);break;}}
    patched_children[index] = children;
    console.log("CALL delete row:", CFG.products[index]);
    return patched_children;
},
display_progress: function (_1, name, date, est, ...vals) {
    badges = vals.slice(0, 13);
    children = vals.slice(13).map(c => c.length);
    message = "Você tem certeza que quer enviar? Resumo do envio:\n\n";
    message += "Seções com poucos itens: " + children.filter(v => v < 3).length;
    return_vals = badges.map(v => {
        if (v === "success") {return {"color": "green"}}
        else if (v === "danger") {return {"color": "red"}}
        else {return {"color": "#FCAE1E"}}});
    // Update save button status
    if ([name, date, est].every(v => v == "correct") && badges.every(v => v != "danger")) {
        return_vals = return_vals.concat(["success", ""])}
    else {return_vals = return_vals.concat(["danger", "unclickable"])};
    console.log("CALL progress: (", dash_clientside.callback_context.triggered_id, ")", [name, date, est], badges, return_vals);
    return_vals.push(message);
    return_vals.push("");
    return return_vals;
}
}
