if(!window.dash_clientside){window.dash_clientside={}}
const logValids=(lists,keys)=>lists.reduce((acc,_,i)=>{if(i%4===0&&keys[i/4]){acc[keys[i/4]]=lists.slice(i,i+4).flat()}return acc},{});
function haversine(a,t){var[h,n]=a,[r,s]=t,M=deg2rad(r-h),d=deg2rad(s-n),e=Math.sin(M/2)*Math.sin(M/2)+Math.cos(deg2rad(h))*Math.cos(deg2rad(r))*Math.sin(d/2)*Math.sin(d/2);return 2*Math.atan2(Math.sqrt(e),Math.sqrt(1-e))*6371}
function deg2rad(d){return d*(Math.PI/180)};
const GEOOPTS={enableHighAccuracy:true,timeout:5000,maximumAge:10000};
let LOC=null;
const getPos=(options)=>{return new Promise((resolve,reject)=>{navigator.geolocation.getCurrentPosition(resolve,reject,options)})};
const ERRS={
1:"Permita o uso de localização! Ação manual necessária!",
2:"Posição indisponível, dispositivo não conseguir determinar posição!",
3:"Dispositivo não respondeu com a localização a tempo!",
4:"Localização não é suportada nesse browser!",
default:"Erro desconhecido!"};
const ERRS2={
1: "LOCALIZAÇÃO NEGADA",
2: "POSIÇÃO INDISPONÍVEL",
3: "DISPOSITIVO LENTO",
4: "NAVEGADOR INCOMPATÍVEL",
default:"ERRO DESCONHECIDO"};
const errTxt=(e)=>{return ERRS[e]||ERRS.default};
const errTxt2=(e)=>{return ERRS2[e]||ERRS2.default};
const BR={type:"Br",namespace:"dash_html_components",props:{}};
const STRONG=(str)=>{return{type:"Strong",namespace:"dash_html_components",props:{children:str}}};
const NOUPDATE=dash_clientside.no_update;
const PRDOUT=new Array(13).fill(NOUPDATE);
function INFO(...m){ctx=dash_clientside.callback_context&&dash_clientside.callback_context.triggered_id?dash_clientside.callback_context.triggered_id:"?";console.log(`%c${INFO.caller.name.toUpperCase()} %c(${ctx}):`,"background:#00252E;color:#25F5FC","background:#382C00;color:#FFC800",...m)}
function ERROR(...m){console.log(`%cERROR ${ERROR.caller.name.toUpperCase()} %c(${dash_clientside.callback_context.triggered_id}):`,"background:#700000;color:#FFADAD","background:#382C00;color:#FFC800",...m)}
function nearest(lat,lon){smallestDist=[Infinity,""];for(est in COORDS){vals=COORDS[est];dist=haversine([lat,lon],[vals.Latitude,vals.Longitude]);if(dist<smallestDist[0]){smallestDist=[dist,est]}}return smallestDist}
function splitArgs(...args) {
    if (args.length % 2 !== 0) {throw new Error("Expected an even number of arguments.")}
    const half = args.length / 2;
    const firstHalf = args.slice(0, half);
    const secondHalf = args.slice(half);
    return [firstHalf, secondHalf];
}
function updateGeoBadge(position, error) {
    const badge = document.getElementById("geolocation-badge");
    if (!position) {
        badge.textContent = error ? errTxt2(error.code) : "Unknown error";
        badge.className = "badge bg-danger";
        return;
    }
    const { latitude, longitude } = position.coords;
    const date = new Date(position.timestamp);
    const hh = String(date.getHours()).padStart(2, '0');
    const mm = String(date.getMinutes()).padStart(2, '0');
    const ss = String(date.getSeconds()).padStart(2, '0');
    badge.textContent = `${latitude.toFixed(4)}, ${longitude.toFixed(4)} - ${hh}:${mm}:${ss}`;
    badge.className = "badge bg-secondary";

    // Load current history
    let history = [];
    try {
        const raw = localStorage.getItem("geo-history");
        if (raw) {history = JSON.parse(raw)}
    } catch { history = [] }

    // Append if moved more than 100m
    const newEntry = [latitude, longitude, position.timestamp];
    if (history.length === 0 || haversine(history.at(-1), newEntry) > 0.1) {
        history.push(newEntry);
        if (history.length > 50) history.shift(); // keep recent 50 entries
        localStorage.setItem("geo-history", JSON.stringify(history));
    }
};

function waitForBadge(elementId, callbackFn) {
    if (document.getElementById(elementId)) {callbackFn();return}
    const observer = new MutationObserver(() => { if (document.getElementById(elementId)) {observer.disconnect();callbackFn()}});
    observer.observe(document.body, { childList: true, subtree: true });
}

waitForBadge("geolocation-badge", () => {
    navigator.permissions.query({ name: 'geolocation' }).then(result => {
        if (result.state === 'denied') {updateGeoBadge(null, { code: 1, message: "Permission denied" })}
        else {navigator.geolocation.watchPosition(p => updateGeoBadge(p, null), e => {updateGeoBadge(null, e)}, GEOOPTS)}
        result.onchange = () => {location.reload()};
    });
});


function refresh_CFG() {
    console.time("refresh_CFG");
    fetch('/get-cfg')
        .then(response => {
            if (!response.ok) {throw new Error('Network response was not ok /refresh_CFG')}
            return response.json();
        })
        .then(data => { localStorage.setItem("CFG-data", JSON.stringify(data));console.timeEnd("refresh_CFG");refresh_brands() })
        .catch(error => { console.error('Error fetching /get-cfg:', error);console.timeEnd("refresh_CFG") });
}


function refresh_brands() {
    console.time("refresh_brands");
    products = JSON.parse(localStorage.getItem("CFG-data")).products;

    // Remove brands from localStorage that are not in the current products list
    const productKeys = products.map(p => `brands-${p}`);
    Object.keys(localStorage)
        .filter(key => key.startsWith("brands-") && !productKeys.includes(key))
        .forEach(key => localStorage.removeItem(key));

    if (!products) return;
    for (const product of products) {
        fetch(`/get-brands/${product}`)
            .then(response => {
                if (!response.ok) {throw new Error(`Network response was not ok for ${product}`)}
                return response.json();
            })
            .then(data => { localStorage.setItem(`brands-${product}`, JSON.stringify(data)) })
            .catch(error => { console.error(`Error fetching /get-brand/${product}:`, error) });
    }
    console.timeEnd("refresh_brands");
}

setInterval(refresh_CFG, 1000 * 60 * 5);

refresh_CFG();

window.dash_clientside.functions={
refresh_local_storages: function(_){
    let markdown = "";
    const keys = Object.keys(localStorage).sort();
    for (const key of keys) {
        const value = localStorage.getItem(key);
        let displayValue = "";
        try {
            // Try to pretty-print JSON values
            const parsed = JSON.parse(value);
            displayValue = JSON.stringify(parsed, null, 2);
        } catch {
            // Fallback to raw value (truncate if very long)
            displayValue = value && value.length > 500 ? value.slice(0, 500) + "..." : value;
            displayValue = "``` " + displayValue + " ```";
        }
        markdown += `###### ${key}:\n\n${displayValue}\n`;
    }
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    const ss = String(now.getSeconds()).padStart(2, '0');
    return [markdown, `${hh}:${mm}:${ss}`];
},
validate_sections: function(name, date, estab, ...args) {
    const [color, children] = splitArgs(...args);
    let disabled = color.includes("danger")
    disabled = disabled || name === "" || date === "" || estab === "";
    disabled = disabled || name === null || date === null || estab === null;
    disabled = disabled || name === undefined || date === undefined || estab === undefined;

    counts = {};

    children.forEach(item => {
        counts[item] = (counts[item] || 0) + 1;
    });

    message = "";
    message += `✅ Produtos Perfeitos: ${counts["Completo"] || 0}\n\n`;
    message += `⚠️ Produtos com Faltas: ${counts["Faltando"] || 0}\n\n`;
    message += `❌ Produtos Sem dados: ${counts["Sem dados"] || 0}\n\n`;
    INFO(disabled, disabled ? "danger" : "success", disabled ? "unclickable" : "", "\n", message);
    return [message, disabled, disabled ? "danger" : "success", disabled ? "unclickable" : ""];
},
load_brands: function(_, id, opts) {
    return new Promise((resolve) => {
        const prd = id.type.split("-")[1];
        const brands = JSON.parse(localStorage.getItem(`brands-${prd}`));
        if (brands === null || brands === undefined) {
            ERROR("No brands found for", prd);
            resolve([]);
        } else {
            INFO("load_brands", prd);
            resolve(brands);
        }
    });
},
delete_row_data_branded: function(_) {
    return new Promise((resolve) => { resolve([null, null, null]) })
},
delete_row_data_brandless: function(_) {
    return new Promise((resolve) => { resolve([null, null]) })
},
process_product_branded: function(...args) {
    return new Promise((resolve) => {resolve(process_product(...args))})
},
process_product_brandless: function(...args) {
    return new Promise((resolve) => {resolve(process_product(...args))})
}
}
function process_product(add, del, ...data) {
    const id = data.pop();
    const collap = data.pop();
    const qtys = data.pop();
    const prcs = data.pop();
    brds = null;
    if (data.length !== 0) { brds = data.pop() }

    CFG = JSON.parse(localStorage.getItem("CFG-data"));
    const prd = id.split("add-")[1];
    const ctx = dash_clientside.callback_context.triggered_id;

    // Determine collapse is_open state
    ideal_length = CFG["product_rows"][prd];
    expected_length = CFG["max_rows"];
    initial_array = new Array(expected_length).fill(false);
    for (let i = 0; i < ideal_length; i++) { initial_array[i] = true }

    let collapsed = localStorage.getItem(`collapse-${prd}`);
    let is_open = null;

    if (collapsed !== null) {
        try {
            is_open = JSON.parse(collapsed);
        } catch (e) {
            is_open = null;
        }
    }

    if ( collapsed === null || !Array.isArray(is_open) || is_open.length !== expected_length ) { is_open = initial_array }

    if (ctx === `add-${prd}`) {
        for (let i = 0; i < is_open.length; i++) {
            if (!is_open[i]) { is_open[i] = true; break }
        }
    }
    else if (typeof ctx === "object" && ctx.type === `delete-${prd}`) {
        if (typeof ctx.index === "number") { is_open[ctx.index] = false }
    }

    localStorage.setItem(`collapse-${prd}`, JSON.stringify(is_open));
    const status = `${is_open.filter(x => x).length}/${expected_length}`;

    // Validate inputs
    prcInvalid = prcs.map(p => p == null || p === "" || isNaN(p) || p <= 0);
    qtyInvalid = qtys.map(q => false);
    brdInvalid = null;

    if (brds === null) {
        buttonClass = prcInvalid.map((p, i) => {
            if (!p) { return "btn-outline-success" }
            else { return "btn-outline-danger" }
        });
    } else {
        brdInvalid = brds.map(b => !b);
        buttonClass = brdInvalid.map((b, i) => {
            if (!b && !prcInvalid[i]) { return "btn-outline-success" }
            else { return "btn-outline-danger" }
        });
    }

    // Validate section, set badge and icons
    const openValidations = buttonClass.filter((_, i) => is_open[i]);
    const validCount = openValidations.filter(cl => cl.includes("success")).length;

    if (is_open.filter(x => x).length === 0) {
        sectionValidations = ["Sem dados", "warning", "icon-orange"]
    } else if (openValidations.every(cl => cl.includes("success"))) {
        if (validCount < CFG["product_rows"][prd]) { sectionValidations =  ["Faltando", "warning", "icon-orange"] }
        else { sectionValidations = ["Completo", "success", "icon-green"] }
    } else { sectionValidations = ["Valores", "danger", "icon-red"] }


    if (brds === null) {rtn = [is_open, status, prcInvalid, qtyInvalid, buttonClass];}
    else {rtn = [is_open, status, brdInvalid, prcInvalid, qtyInvalid, buttonClass];}
    rtn = rtn.concat(sectionValidations);
    INFO(rtn)
    return rtn;
}
