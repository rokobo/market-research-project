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

let ws;
let pingStart;
let interval;
function updateBadge(status, latency = null) {
    const badge = document.getElementById("online2-badge");
    if (status === "connected") {
        badge.textContent = `✅ Connected (${latency} ms)`;
        badge.style.color = "green";
    } else if (status === "disconnected") {
        badge.textContent = `❌ Disconnected`;
        badge.style.color = "red";
    } else {
        badge.textContent = `🔄 Connecting...`;
        badge.style.color = "gray";
    }
}
function connectWS() {
    const protocol = location.protocol === "https:" ? "wss://" : "ws://";
    const host = location.host; // includes hostname and port
    const wsUrl = protocol + host + "/ws"; // adjust path if needed

    ws = new WebSocket(wsUrl); // Change this to your server

    ws.onopen = () => {
        updateBadge("connected", "--");
        interval = setInterval(() => {
            pingStart = Date.now();
            ws.send("ping");
        }, 5000); // every 5 seconds
    };

    ws.onmessage = (event) => {
        if (event.data === "pong") {
            const latency = Date.now() - pingStart;
            updateBadge("connected", latency);
        }
    };

    ws.onclose = () => {
        updateBadge("disconnected");
        clearInterval(interval);
        setTimeout(connectWS, 3000); // retry
    };

    ws.onerror = () => {
        updateBadge("disconnected");
        ws.close();
    };
}
connectWS();
window.dash_clientside.input={
update_badges:async function(_,geo){
    let bdgOut=[],geoNow=null;
    if(navigator.onLine){bdgOut=bdgOut.concat(["ONLINE","success"])}
    else {bdgOut=bdgOut.concat(["OFFLINE","danger"])};
    if(navigator.geolocation){try{LOC=await getPos(GEOOPTS);geoNow=[LOC.coords.latitude,LOC.coords.longitude,LOC.timestamp];bdgOut=bdgOut.concat([geoNow[0].toFixed(4)+", "+geoNow[1].toFixed(4),"secondary"])}
        catch(e){LOC=e.code;bdgOut=bdgOut.concat([errTxt2(LOC),"danger"])}}
    else{LOC=4;bdgOut=bdgOut.concat([errTxt2(LOC),"danger"])}
    if(bdgOut[3]=="secondary"){bdgOut=bdgOut.concat([false,NOUPDATE])}
    else {bdgOut=bdgOut.concat([true,[STRONG("REQUISITO PENDENTE: "),errTxt(LOC)]])}
    if(geoNow==null){bdgOut.push(NOUPDATE)}
    else if(geo.length==0||haversine(geo.at(-1),geoNow)>0.1){bdgOut.push(geo.concat([geoNow]))}
    else{{bdgOut.push(NOUPDATE)}}
    if(geo.length>50){geo.shift()}
    let size=(Object.keys(localStorage).reduce((t,k)=>{return t+(localStorage[k].length+k.length)*2},0)/1024).toFixed(2);
    bdgOut.push(size+" KB");
    return bdgOut;
}
}
