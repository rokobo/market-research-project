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

setInterval(refresh_CFG, 1000 * 60);

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
validate_row_brand: function(brd, prc, qty, className) {
    const output = [
        brd === null || brd === "" || brd === undefined,
        prc === null || prc === "" || prc === undefined || isNaN(prc) || prc <= 0,
        false]

    const allValid = output.every(val => !val);

    if (allValid) {
        const nc = "btn-outline-success";
        if (className === nc) { output.push(dash_clientside.no_update)
        } else { output.push(nc) }
    } else {
        const nc = "btn-outline-danger";
        if (className === nc) { output.push(dash_clientside.no_update)
        } else { output.push(nc) }
    }
    INFO(output, brd, prc, qty, className);
    return output;
},
validate_row_brandless: function(prc, qty, className) {
    const output = [
        prc === null || prc === "" || prc === undefined || isNaN(prc) || prc <= 0,
        false]

    const allValid = output.every(val => !val);

    if (allValid) {
        const nc = "btn-outline-success";
        if (className === nc) { output.push(dash_clientside.no_update)
        } else { output.push(nc) }
    } else {
        const nc = "btn-outline-danger";
        if (className === nc) { output.push(dash_clientside.no_update)
        } else { output.push(nc) }
    }
    INFO(output, prc, qty, className);
    return output;
},
validate_rows: function(cls, src) {
    const icon = src.split("-")[0];
    const current = src.split("-")[1];
    const prd = icon.split("/").at(-1);
    const CFG = JSON.parse(localStorage.getItem("CFG-data"));

    if (cls.length === 0) {
        rtn = ["Sem dados", "warning", "icon-orange"]
        INFO(rtn, cls, src);
        return rtn;
    }
    const allSuccess = cls.every(cl => cl.includes("success"));
    if (allSuccess) {
        if (cls.length < CFG.product_rows[prd]) {
            rtn =  ["Faltando", "warning", "icon-orange"];
            INFO(rtn, cls, src);
            return rtn;
        } else {
            rtn = ["Completo", "success", "icon-green"];
            INFO(rtn, cls, src);
            return rtn;
        }
    } else {
        rtn = ["Valores", "danger", "icon-red"];
        INFO(rtn, cls, src);
        return rtn;
    }
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
    message += `Produtos Perfeitos: ${counts["Completo"] || 0}\n`;
    message += `Produtos com Faltas: ${counts["Faltando"] || 0}\n`;
    message += `Produtos Sem dados: ${counts["Sem dados"] || 0}\n`;
    INFO(disabled, disabled ? "danger" : "success", disabled ? "unclickable" : "", "\n", message);
    return [message, disabled, disabled ? "danger" : "success", disabled ? "unclickable" : ""];
},
load_brands: function(_) {
    ctx = dash_clientside.callback_context.outputs_list.id.type.split("-")[1];
    brands = JSON.parse(localStorage.getItem(`brands-${ctx}`));
    if (brands === null || brands === undefined) {
        ERROR("No brands found for", ctx);
        return [];
    }
    INFO("load_brands", ctx);
    return brands
}
}
