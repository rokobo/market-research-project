if (!window.dash_clientside) {window.dash_clientside = {}}
const CFG = JSON.parse(localStorage.getItem('config'));
const groupValidations2=(lists,keys)=>lists.reduce((acc,_,i)=>{if(i%4===0&&keys[i/4]){acc[keys[i/4]]=lists.slice(i,i+4).flat()}return acc},{});

window.dash_clientside.clientside = {
clear_contents: function(clk) {
    if (typeof clk !== 'number') {return window.dash_clientside.no_update};
    console.log("CALL clear contents (",dash_clientside.callback_context.triggered_id,")");
    return [];
},
close_modal:function(clk){if(typeof clk!=='number'){return window.dash_clientside.no_update};return false},
save_state: function(_1, load, name, date, estab, obs, ...prdc) {
    if (load === null) {return window.dash_clientside.no_update}
    let data = [];data.push({'first':[name,date,estab]});data.push({'observations':obs});
    for (let i = 0; i < prdc.length; i++) {
        let product_name = CFG.products[i];
        let product = prdc[i];
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
            data.push({"container":product_name,"values":row,"row_id":row_id.split("-").slice(-1)[0]});
        }
    };
    console.log("CALL save data (",dash_clientside.callback_context.triggered_id,")",data);
    return data;
},
validate_args: function (_1, name, date, est, ...vals) {
    var firsts = vals.splice(-3);
    var seconds = vals.slice((vals.length - CFG.products.length)/2 + CFG.products.length);
    var valids = [];
    var status1 = [];
    var status2 = [];
    // Individual validations
    for (var i = 0; i < seconds.length; i += 4) {
        var [br, pr, qn, obs] = seconds.slice(i, i + 4);
        valids.push(br.map(brand => typeof brand == 'string'));
        valids.push(pr.map(price => typeof price === 'number' && !isNaN(price)));
        valids.push(qn.map(() => true));
        valids.push(obs.map(() => true));
    };
    // Section validations
    for (var i = 0; i < valids.length; i += 4) {
        const val = valids.slice(i, i + 4);
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
    valids=valids.map(sublist=>sublist.map(v=>v?"correct":"wrong"));
    console.log("CALL validation (",dash_clientside.callback_context.triggered_id,")",firsts,groupValidations2(valids,CFG.products));
    valids=valids.concat(status1).concat(status2).concat(firsts.map(v=>(v!==null&&v!==""?"correct":"wrong")));
    valids.push("");
    // Add scroll on focus event listeners
    document.querySelectorAll('.form-control').forEach(function(input) {
        if (!input.hasEventListener) {
            input.addEventListener('focus', function() {
                input.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
            input.hasEventListener = true;
        }
    })
    return valids;
},
delete_product_row: function (...vals) {
    var ctx = dash_clientside.callback_context.triggered_id;
    if (vals.slice(0, CFG.products.length).every(sublist => sublist.every(v => typeof v === "undefined"))) {
        return window.dash_clientside.no_update;}
    var states = vals.slice(CFG.products.length);
    var ctxType = ctx.type.slice(7);
    var prop_id = `${ctxType}-product-row-${ctx.index}`
    var index = CFG.products.indexOf(ctxType);
    var patch = Array(CFG.products.length).fill(window.dash_clientside.no_update);
    var children = states[index];
    for (let i = 0; i < children.length; i++) {
        var child = children[i];
        // Find row by row index and context index, remove child at index i
        if (child.props.id === prop_id) {children.splice(i, 1);break;}}
    patch[index] = children;
    console.log("CALL delete row:",CFG.products[index]);
    return patch;
},
display_progress: function (_1, name, date, est, ...vals) {
    badges = vals.slice(0, 13);
    msg = "Você tem certeza que quer enviar? Resumo do envio:\n\n";
    msg += "Seções com poucos itens: " + vals.slice(13).filter((c, i) => c.length < CFG.product_rows[CFG.products[i]]).length;
    output = badges.map(v => {
        if (v === "success") {return {"color": "green"}}
        else if (v === "danger") {return {"color": "red"}}
        else {return {"color": "rgb(252, 174, 30)"}}});
    // Update save button status
    if ([name, date, est].every(v => v == "correct") && badges.every(v => v != "danger")) {
        output = output.concat(["success", ""])}
    else {output = output.concat(["danger", "unclickable"])};
    console.log("CALL progress: (",dash_clientside.callback_context.triggered_id,")",[name,date,est],badges,output);
    output.push(msg);
    output.push("");
    return output;
}
}
