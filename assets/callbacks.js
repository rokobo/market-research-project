if(!window.dash_clientside){window.dash_clientside={}}
const CFG=JSON.parse(localStorage.getItem('config'));
const COORDINATES=JSON.parse(localStorage.getItem('coordinates'));
const groupValidations2=(lists,keys)=>lists.reduce((acc,_,i)=>{if(i%4===0&&keys[i/4]){acc[keys[i/4]]=lists.slice(i,i+4).flat()}return acc},{});
function haversineDistance(a,t,h,n){var r=deg2rad(h-a),s=deg2rad(n-t),M=Math.sin(r/2)*Math.sin(r/2)+Math.cos(deg2rad(a))*Math.cos(deg2rad(h))*Math.sin(s/2)*Math.sin(s/2);return 6371*(2*Math.atan2(Math.sqrt(M),Math.sqrt(1-M)))};
function deg2rad(d){return d*(Math.PI/180)};
const GEOOPTS={enableHighAccuracy:true,timeout:5000,maximumAge:5};
let LOCATION = null;
const getPosition = (options) => {return new Promise((resolve, reject)=>{navigator.geolocation.getCurrentPosition(resolve,reject,options)})};
const ERRORS = {
    1:"Permita o uso de localização e tente novamente!",
    2:"Posição indisponível, tente novamente!",
    3:"Tempo de requisição esgotado, tente novamente!",
    4: "Localização não é suportada nesse browser!",
    default:"Erro desconhecido!"
};
const translateError=(error)=>{return ERRORS[error]||ERRORS.default};

window.dash_clientside.clientside={
clear_contents:function(clk){
    if (typeof clk !== 'number'){return dash_clientside.no_update};
    console.log("clear_contents: (",dash_clientside.callback_context.triggered_id,")");
    return [];
},
close_modal:function(clk){if(typeof clk!=='number'){return dash_clientside.no_update};return false},
update_badges:async function(_,pos){
    output=[];
    if(navigator.onLine){output=output.concat(["ONLINE","success"])}
    else {output=output.concat(["OFFLINE","danger"])};
    if(navigator.geolocation){try{LOCATION=await getPosition(GEOOPTS);output=output.concat([LOCATION.coords.latitude.toFixed(4)+", "+LOCATION.coords.longitude.toFixed(4),"secondary"])}
    catch(error){LOCATION=error.code;output=output.concat(["LOCALIZAÇÃO NEGADA","danger"])}}
    else{LOCATION=4;output=output.concat(["ERRO LOCALIZAÇÃO","danger"])}
    return output;
},
save_state:function(_,load,name,date,estab,obs,...prdc){
    if (load === null){return dash_clientside.no_update}
    let data=[];data.push({'first':[name,date,estab]});data.push({'observations':obs});
    for(let i=0;i < prdc.length;i++){
        let product_name=CFG.products[i];
        let product=prdc[i];
        for(let prod_row of product){
            let row_id=prod_row.props.id;
            let val=prod_row.props.children;
            let vals={};
            for(let idx=0;idx < val.length;idx++){
                try {vals[idx]=val[idx].props.children.props.value} catch (error){}}
            let row=[null,null,null,null];
            switch (val.length){
                case 4:
                    row=[vals[1],vals[2],vals[3],null];
                    break;
                case 3:
                    if (product_name=='banana'){row=[vals[1],vals[2],null,null]}
                    else {row=[null,vals[1],null,vals[2]]}
                    break;
                default:row=[null,null,null,null];
            }
            data.push({"container":product_name,"values":row,"row_id":row_id.split("-").slice(-1)[0]});
        }
    };
    console.log("save_state: (",dash_clientside.callback_context.triggered_id,")",data);
    return data;
},
validate_args:function(_,name,date,est,...vals){
    var firsts=vals.splice(-3);
    var seconds=vals.slice((vals.length - CFG.products.length)/2 + CFG.products.length);
    var valids=[],status1=[],status2=[];
    ctx = dash_clientside.callback_context.triggered_id;
    // Individual validations
    for(var i=0;i < seconds.length;i += 4){
        var [br,pr,qn,obs]=seconds.slice(i,i + 4);
        valids=valids.concat([
            br.map((a=>"string"==typeof a)),
            pr.map((a=>"number"==typeof a&&!isNaN(a))),
            qn.map((()=>!0)),
            obs.map((()=>!0))]);
    };
    // Section validations
    for(var i=0;i < valids.length;i += 4){
        const val=valids.slice(i,i + 4);
        if (val.every(sublist=>sublist.every(v=>v))){
            if (val[1].length >= CFG.product_rows[CFG.products[i/4]]){status1.push("Completo");status2.push("success")
            }else {status1.push("Okay");status2.push("warning");}
        }else{status1.push("Faltando");status2.push("danger")}
    };
    // Transform to appropriate classnames
    valids=valids.map(sublist=>sublist.map(v=>v?"correct":"wrong"));
    console.log("validate_args: (",ctx,")",firsts,groupValidations2(valids,CFG.products));
    valids=valids.concat(status1).concat(status2).concat(firsts.map(v=>(v!==null&&v!==""?"correct":"wrong")));
    valids.push("");valids.push(false);
    // Add scroll on focus event listeners
    document.querySelectorAll('.form-control').forEach(function(input){
        if (!input.hasEventListener){
            input.addEventListener('focus',function(){input.scrollIntoView({behavior:'smooth',block:'center'})});
            input.hasEventListener=true;
        }
    })
    return valids;
},
delete_product_row:function(...vals){
    var ctx=dash_clientside.callback_context.triggered_id;
    if (vals.slice(0,CFG.products.length).every(sublist=>sublist.every(v=>typeof v === "undefined"))){
        return dash_clientside.no_update;}
    var states=vals.slice(CFG.products.length);
    var ctxType=ctx.type.slice(7);
    var prop_id=`${ctxType}-product-row-${ctx.index}`
    var index=CFG.products.indexOf(ctxType);
    var patch=Array(CFG.products.length).fill(dash_clientside.no_update);
    var children=states[index];
    for(let i=0;i < children.length;i++){
        var child=children[i];
        // Find row by row index and context index,remove child at index i
        if (child.props.id === prop_id){children.splice(i,1);break;}}
    patch[index]=children;
    console.log("delete_product_row:",CFG.products[index]);
    return patch;
},
display_progress:function(_,name,date,est,...vals){
    badges=vals.slice(0,13);
    today=new Date().toISOString().split('T')[0];
    date_val=vals[26];
    idx=0;
    msg="Você tem certeza que quer enviar?\n\n";
    msg+=`${idx+=1}. Seções com poucos itens: `+vals.slice(13,26).filter((c,i)=>c.length<CFG.product_rows[CFG.products[i]]).length+"\n";
    if(today!=date_val){msg+=`${idx+=1}. Envio em dia diferente:\n      - Data atual: `+today+"\n      - Registrado: "+date_val}
    output=badges.map(v=>{
        if (v === "success"){return {"color":"green"}}
        else if (v === "danger"){return {"color":"red"}}
        else {return {"color":"rgb(252,174,30)"}}});
    // Update save button status
    if ([name,date,est].every(v=>v=="correct") && badges.every(v=>v!="danger")){output=output.concat(["success",""])}
    else {output=output.concat(["danger","unclickable"])};
    console.log("display_progress: (",dash_clientside.callback_context.triggered_id,")",[name,date,est],badges,output, msg);
    output.push(msg);
    output.push("");
    return output;
},
establishment_address:function(est){
    if(est in COORDINATES){loc=COORDINATES[est].Endereço}else{loc="Sem endereço"}
    console.log("establishment_address:",est,loc);return loc;
},
locate_establishment:function(_){
    output=[dash_clientside.no_update, ""];
    pos=LOCATION;
    if(typeof pos==="number"){output[1]=translateError(LOCATION);return output}
    lat=pos.coords.latitude;
    lon=pos.coords.longitude;
    smallestDist=[Infinity, ""];
    for (est in COORDINATES) {
        vals=COORDINATES[est];dist=haversineDistance(lat,lon,vals.Latitude,vals.Longitude);
        if (dist<smallestDist[0]){smallestDist=[dist,est]}}
    console.log("locate_establishment:",smallestDist,pos);
    text="Distância: "+smallestDist[0].toFixed(2)+"km ± "+pos.coords.accuracy.toFixed(0)+"m, ";
    text+=new Date(pos.timestamp).toLocaleString("en-CA",{hour12:false});
    output=[smallestDist[1],text]
    return output;
}
}
