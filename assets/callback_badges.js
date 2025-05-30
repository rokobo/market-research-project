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
    if (args.length % 2 !== 0) {
        throw new Error("Expected an even number of arguments.");
    }
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
        if (raw) history = JSON.parse(raw);
    } catch {
        history = [];
    }

    // Append if moved more than 100m
    const newEntry = [latitude, longitude, position.timestamp];
    if (
        history.length === 0 ||
        haversine(history.at(-1), newEntry) > 0.1
    ) {
        history.push(newEntry);
        if (history.length > 50) history.shift(); // keep recent 50 entries
        localStorage.setItem("geo-history", JSON.stringify(history));
    }
};

function handleDeniedPermission() {
    updateBadges(null, { code: 1, message: "Permission denied" });
}

function waitForBadge(elementId, callbackFn) {
    if (document.getElementById(elementId)) {
        callbackFn();
        return;
    }

    const observer = new MutationObserver(() => {
        if (document.getElementById(elementId)) {
            observer.disconnect();
            callbackFn();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
}

waitForBadge("geolocation-badge", () => {
    navigator.permissions.query({ name: 'geolocation' }).then(result => {
        if (result.state === 'denied') {handleDeniedPermission()}
        else {
            navigator.geolocation.watchPosition(
                position => updateGeoBadge(position, null),
                error => {updateGeoBadge(null, error)},
                GEOOPTS
            );
        }
        result.onchange = () => {
            location.reload();
        };
    });
});

window.dash_clientside.functions={
refresh_local_storages: function(_){
    const history = localStorage.getItem("geo-history");
    const persistence = Object.keys(localStorage).filter(key => key.startsWith("_dash_persistence"));
    let formattedHistory = "";
    try {
        const parsed = JSON.parse(history || "[]");
        formattedHistory = parsed.map(item => JSON.stringify(item)).join('\n');
    } catch {
        formattedHistory = history || "";
    }
    let markdown = `### Geo-history\n\`\`\`json\n${formattedHistory}\n\`\`\`\n\n`;
    markdown += `### _dash_persistence values\n\`\`\`json\n${JSON.stringify(persistence, null, 2)}\n\`\`\``;
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
        rtn = ["Sem dados", "warning", `${icon}-orange.svg`]
        INFO(rtn, cls, src);
        return rtn;
    }
    const allSuccess = cls.every(cl => cl.includes("success"));
    if (allSuccess) {
        if (cls.length < CFG.product_rows[prd]) {
            rtn =  ["Faltando", "warning", `${icon}-orange.svg`];
            INFO(rtn, cls, src);
            return rtn;
        } else {
            rtn = ["Completo", "success", `${icon}-green.svg`];
            INFO(rtn, cls, src);
            return rtn;
        }
    } else {
        rtn = ["Valores", "danger", `${icon}-red.svg`];
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

}
}
