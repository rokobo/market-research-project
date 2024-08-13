if(!window.dash_clientside){window.dash_clientside={}}
const CFG=JSON.parse(localStorage.getItem('config'));
const COORDS=JSON.parse(localStorage.getItem('coordinates'));
const logValids=(lists,keys)=>lists.reduce((acc,_,i)=>{if(i%4===0&&keys[i/4]){acc[keys[i/4]]=lists.slice(i,i+4).flat()}return acc},{});
function haversine(a,t){var[h,n]=a,[r,s]=t,M=deg2rad(r-h),d=deg2rad(s-n),e=Math.sin(M/2)*Math.sin(M/2)+Math.cos(deg2rad(h))*Math.cos(deg2rad(r))*Math.sin(d/2)*Math.sin(d/2);return 2*Math.atan2(Math.sqrt(e),Math.sqrt(1-e))*6371}
function deg2rad(d){return d*(Math.PI/180)};
const GEOOPTS={enableHighAccuracy:true,timeout:5000,maximumAge:10000};
let LOC=null;
const getPos=(options)=>{return new Promise((resolve,reject)=>{navigator.geolocation.getCurrentPosition(resolve,reject,options)})};
const ERRS={
1:"Permita o uso de localização e tente novamente!",2:"Posição indisponível, tente novamente!",
3:"Tempo de requisição esgotado, espere ou tente novamente!",4:"Localização não é suportada nesse browser!",
default:"Erro desconhecido!"};
const errTxt=(e)=>{return ERRS[e]||ERRS.default};
const BR={type:"Br",namespace:"dash_html_components",props:{}};
const STRONG=(str)=>{return{type:"Strong",namespace:"dash_html_components",props:{children:str}}};
const K=CFG.fields.length;
const NOUPDATE=dash_clientside.no_update;
const PRDOUT=new Array(13).fill(NOUPDATE);

window.dash_clientside.input={
add_row:function(...clk){out=[...PRDOUT];prd=dash_clientside.callback_context.triggered_id.slice(4);out[CFG.product_index[prd]]={"add":[{}]};console.log("add_row",prd);return out},
clear_contents:function(...clk){
    console.log("clear_contents: (",dash_clientside.callback_context.triggered_id,"): ",clk[0]);
    if(clk[0].some(v=>typeof v==='number')){console.log("clear_contents: Memory deleted");return[]}
    return NOUPDATE;
},
close_modal:function(clk){if(typeof clk!=='number'){return NOUPDATE};return false},
theme_switcher:function(s){console.log("theme_switch",s);document.documentElement.setAttribute('data-bs-theme',s);return s},
fill_date:function(_){return new Date().toLocaleDateString('en-CA')},
update_badges:async function(_,pos,geo){
    bdgOut=[];geoNow=null;
    if(navigator.onLine){bdgOut=bdgOut.concat(["ONLINE","success"])}
    else {bdgOut=bdgOut.concat(["OFFLINE","danger"])};
    if(navigator.geolocation){try{LOC=await getPos(GEOOPTS);geoNow=[LOC.coords.latitude,LOC.coords.longitude,LOC.timestamp];bdgOut=bdgOut.concat([geoNow[0].toFixed(4)+", "+geoNow[1].toFixed(4),"secondary"])}
        catch(e){LOC=e.code;bdgOut=bdgOut.concat(["LOCALIZAÇÃO NEGADA","danger"])}}
    else{LOC=4;bdgOut=bdgOut.concat(["ERRO LOCALIZAÇÃO","danger"])}
    if(bdgOut[3]=="secondary"){bdgOut=bdgOut.concat([false,NOUPDATE])}
    else {bdgOut=bdgOut.concat([true,[BR,BR,STRONG("REQUISITO PENDENTE:"),errTxt(LOC),BR,BR,BR]])}
    if(geoNow==null){bdgOut.push(NOUPDATE)}
    else if(geo.length==0||haversine(geo.at(-1),geoNow)>0.1){bdgOut.push(geo.concat([geoNow]))}
    else{{bdgOut.push(NOUPDATE)}}
    if(geo.length>CFG.geo_length){geo.shift()}
    size = (Object.keys(localStorage).reduce((t,k)=>{return t+(localStorage[k].length+k.length)*2},0)/1024).toFixed(2);
    bdgOut.push(size + " KB");
    return bdgOut;
},
load_state:function(_, _,local){console.log("load_state");local.push("");return local},
test:function(...args){
    console.log("TESTE", dash_clientside.callback_context.triggered_id, args);
},
validate_args:function(_,n,d,e, ...vals){
    vals=vals.splice(CFG.products.length);
    firsts=vals.splice(CFG.products.length);
    if(vals[0]===undefined){return NOUPDATE}
    vals=vals.map((v,i)=>v===''?Array(CFG.product_rows[CFG.products[i]]).fill({}):v);
    var badgeText=[],badgeColor=[], icons=[],ctx=dash_clientside.callback_context.triggered_id;
    for(var i=0;i<vals.length;i++){
        if (vals[i].every(d=>d["Marca"] != null && d["Preço"] != null)) {
            if (vals[i].length >= CFG.product_rows[CFG.products[i]])
                {badgeText.push("Completo");badgeColor.push("success");icons.push({"color":"green"})}
            else{badgeText.push("Okay");badgeColor.push("warning");icons.push({"color":"rgb(252,174,30)"})}
        }
        else {badgeText.push("Faltando");badgeColor.push("danger");icons.push({"color":"red"})}
    };
    firstClass = firsts.map(v=>(v!=null&&v!==""?"correct":"wrong"));
    out=badgeText.concat(badgeColor).concat(icons).concat(firstClass);
    out.push("");out.push(false);out.push(vals);

    var idx=0, today=new Date().toLocaleDateString('en-CA'), msg="Você tem certeza que quer enviar?\n\n";
    msg+=`${idx+=1}. Seções com poucos itens: `+vals.filter((c,i)=>c.length<CFG.product_rows[CFG.products[i]]).length+"\n";
    if(today!=firsts[1]){msg+=`${idx+=1}. Envio em dia diferente:\n      - Data atual: `+today+"\n      - Registrado: "+firsts[1]}
    if(firstClass.every(v=>v=="correct") && badgeColor.every(v=>v!="danger")){out=out.concat(["success",""])}
    else {out=out.concat(["danger","unclickable"])};
    console.log("validate_args: (",ctx,")",firsts,badgeText,badgeColor,icons,out.slice(-9, -6),out.slice(-2), msg);
    out.push(msg);
    // Add scroll on focus event listeners
    // document.querySelectorAll('.form-control').forEach(function(input){
    //     if(!input.hasEventListener){
    //         input.addEventListener('focus',function(){input.scrollIntoView({behavior:'instant',block:'center'})});
    //         input.hasEventListener=true;
    //     }
    // })
    return out;
},
establishment_address:function(est){
    if(est in COORDS){loc=COORDS[est].Endereço}else{loc="Sem endereço"}
    console.log("establishment_address:",est,loc);return loc;
},
locate_establishment:function(_){
    output=[NOUPDATE, ""];pos=LOC;
    if(typeof pos==="number"){output[1]=errTxt(LOC);return output}
    lat=pos.coords.latitude;lon=pos.coords.longitude;smallestDist=[Infinity, ""];
    for(est in COORDS) {
        vals=COORDS[est];dist=haversine([lat,lon],[vals.Latitude,vals.Longitude]);
        if(dist<smallestDist[0]){smallestDist=[dist,est]}}
    console.log("locate_establishment:",smallestDist,pos);
    text="Distância: "+smallestDist[0].toFixed(2)+"km ± "+pos.coords.accuracy.toFixed(0)+"m, ";
    text+=new Date(pos.timestamp).toLocaleString("en-CA",{hour12:false});
    output=[smallestDist[1],text];return output
}
}
