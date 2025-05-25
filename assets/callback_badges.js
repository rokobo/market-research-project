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

function updateSizeBadge() {
    const badge = document.getElementById("size-badge");
    const size = (Object.keys(localStorage).reduce((t, k) => {
        return t + (localStorage[k].length + k.length) * 2;
    }, 0) / 1024).toFixed(2);
    badge.textContent = `${size} KB`;
}


function updateBadges(position, error) {
    updateGeoBadge(position, error);
    updateSizeBadge();
}

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
                position => updateBadges(position, null),
                error => {updateBadges(null, error)},
                GEOOPTS
            );
        }
        result.onchange = () => {
            location.reload();
        };
    });
});

function startHeartbeat(interval) {
    setInterval(async () => {
        let response;
        try {
            const url = window.location.origin;
            response = await fetch(url, { method: 'GET', cache: 'no-store' });
        } catch (error) {
            response = null;
        }
        console.log(response);
        const badge = document.getElementById("online-badge");
        if (response && response.ok) {
            badge.textContent = "ONLINE";
            badge.className = "badge bg-success";
        } else {
            badge.textContent = response.status || "OFFLINE";
            badge.className = "badge bg-danger";
        }
    }, interval);
}
startHeartbeat(5000);
window.dash_clientside.input={

}
