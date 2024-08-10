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

window.dash_clientside.input={
clear_contents:function(...clk){
    console.log("clear_contents: (",dash_clientside.callback_context.triggered_id,"): ",clk[0]);
    if(clk[0].some(v=>typeof v==='number')){console.log("clear_contents: Memory deleted");return []}
    return dash_clientside.no_update;
},
close_modal:function(clk){if(typeof clk!=='number'){return dash_clientside.no_update};return false},
theme_switcher:function(s){console.log("theme_switch",s);document.documentElement.setAttribute('data-bs-theme',s);return s},
fill_date:function(_){return new Date().toLocaleDateString('en-CA')},
update_badges:async function(_,pos,geo){
    bdgOut=[];geoNow=null;
    if(navigator.onLine){bdgOut=bdgOut.concat(["ONLINE","success"])}
    else {bdgOut=bdgOut.concat(["OFFLINE","danger"])};
    if(navigator.geolocation){try{LOC=await getPos(GEOOPTS);geoNow=[LOC.coords.latitude,LOC.coords.longitude,LOC.timestamp];bdgOut=bdgOut.concat([geoNow[0].toFixed(4)+", "+geoNow[1].toFixed(4),"secondary"])}
        catch(e){LOC=e.code;bdgOut=bdgOut.concat(["LOCALIZAÇÃO NEGADA","danger"])}}
    else{LOC=4;bdgOut=bdgOut.concat(["ERRO LOCALIZAÇÃO","danger"])}
    if(bdgOut[3]=="secondary"){bdgOut=bdgOut.concat([false,dash_clientside.no_update])}
    else {bdgOut=bdgOut.concat([true,[BR,BR,STRONG("REQUISITO PENDENTE:"),errTxt(LOC),BR,BR,BR]])}
    if(geoNow==null){bdgOut.push(dash_clientside.no_update)}
    else if(geo.length==0){bdgOut.push(geo.concat([geoNow]))}
    else if(haversine(geo.at(-1),geoNow)>0.1){bdgOut.push(geo.concat([geoNow]))}
    else{{bdgOut.push(dash_clientside.no_update)}}
    if(geo.length>CFG.geo_length){geo.shift()}
    return bdgOut;
},
save_state:function(_,name,date,estab,obs,...prds){
    let data=[];data.push({'first':[name,date,estab]});data.push({'observations':obs});
    for(let i=0;i<prds.length;i++){
        let prd_name=CFG.products[i];
        let prd=prds[i];
        for(let prod_row of prd){
            let row_id=prod_row.props.id;
            let val=prod_row.props.children;
            let vals={};
            for(let idx=0;idx<val.length;idx++){
                try{vals[idx]=val[idx].props.children.props.value}catch(e){}}
            let row=[null,null,null,null];
            switch(val.length){
                case 4:row=[vals[1],vals[2],vals[3]];break;
                case 3:row=[null,vals[1],vals[2]];break;
                default:row=[null,null,null]}
            data.push({"container":prd_name,"values":row,"row_id":row_id.split("-").slice(-1)[0]});
        }
    };
    console.log("save_state: (",dash_clientside.callback_context.triggered_id,")",data);
    return data;
},
validate_args:function(_,name,date,est,...vals){
    var firsts=vals.splice(-3);
    var seconds=vals.slice((vals.length-CFG.products.length)/2+CFG.products.length);
    var valids=[],status1=[],status2=[];
    ctx=dash_clientside.callback_context.triggered_id;
    // Individual validations
    for(var i=0;i<seconds.length;i+=K){
        var [br,pr,qn]=seconds.slice(i,i+K);
        valids=valids.concat([
            br.map((a=>"string"==typeof a)),
            pr.map((a=>"number"==typeof a&&!isNaN(a)&&a>0)),
            qn.map((a=>a==null|a>0))]);
    };
    // Section validations
    for(var i=0;i<valids.length;i+=K){
        const val=valids.slice(i,i+K);
        if(val.every(sublist=>sublist.every(v=>v))){
            if(val[1].length >=CFG.product_rows[CFG.products[i/K]]){status1.push("Completo");status2.push("success")
            }else {status1.push("Okay");status2.push("warning");}
        }else{status1.push("Faltando");status2.push("danger")}
    };
    // Transform to appropriate classnames
    valids=valids.map(sublist=>sublist.map(v=>v?"correct":"wrong"));
    console.log("validate_args: (",ctx,")",firsts,logValids(valids,CFG.products));
    valids=valids.concat(status1).concat(status2).concat(firsts.map(v=>(v!==null&&v!==""?"correct":"wrong")));
    valids.push("");valids.push(false);
    // Add scroll on focus event listeners
    document.querySelectorAll('.form-control').forEach(function(input){
        if(!input.hasEventListener){
            input.addEventListener('focus',function(){input.scrollIntoView({behavior:'instant',block:'center'})});
            input.hasEventListener=true;
        }
    })
    return valids;
},
delete_product_row:function(...vals){
    var ctx=dash_clientside.callback_context.triggered_id;
    if(vals.slice(0,CFG.products.length).every(sublist=>sublist.every(v=>typeof v==="undefined"))){
        return dash_clientside.no_update;}
    var states=vals.slice(CFG.products.length);
    var ctxType=ctx.type.slice(7);
    var prop_id=`${ctxType}-product-row-${ctx.index}`
    var index=CFG.products.indexOf(ctxType);
    var patch=Array(CFG.products.length).fill(dash_clientside.no_update);
    var children=states[index];
    for(let i=0;i<children.length;i++){
        var child=children[i];
        // Find row by row index and context index,remove child at index i
        if(child.props.id===prop_id){children.splice(i,1);break;}}
    patch[index]=children;
    console.log("delete_product_row:",CFG.products[index]);
    return patch;
},
display_progress:function(_,name,date,est,...vals){
    badges=vals.slice(0,13);
    today=new Date().toLocaleDateString('en-CA');
    date_val=vals[26];
    idx=0;
    msg="Você tem certeza que quer enviar?\n\n";
    msg+=`${idx+=1}. Seções com poucos itens: `+vals.slice(13,26).filter((c,i)=>c.length<CFG.product_rows[CFG.products[i]]).length+"\n";
    if(today!=date_val){msg+=`${idx+=1}. Envio em dia diferente:\n      - Data atual: `+today+"\n      - Registrado: "+date_val}
    output=badges.map(v=>{
        if(v==="success"){return {"color":"green"}}
        else if(v==="danger"){return {"color":"red"}}
        else {return {"color":"rgb(252,174,30)"}}});
    // Update save button status
    if([name,date,est].every(v=>v=="correct") && badges.every(v=>v!="danger")){output=output.concat(["success",""])}
    else {output=output.concat(["danger","unclickable"])};
    console.log("display_progress: (",dash_clientside.callback_context.triggered_id,")",[name,date,est],badges,output, msg);
    output.push(msg);
    output.push("");
    return output;
},
establishment_address:function(est){
    if(est in COORDS){loc=COORDS[est].Endereço}else{loc="Sem endereço"}
    console.log("establishment_address:",est,loc);return loc;
},
locate_establishment:function(_){
    output=[dash_clientside.no_update, ""];pos=LOC;
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
