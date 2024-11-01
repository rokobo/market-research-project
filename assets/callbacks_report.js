if(!window.dash_clientside){window.dash_clientside={}}
function AgData(arq){
    // If the array is empty or the objects have less than 5 keys, return an empty array
    if(arq.length===0||Object.keys(arq[0]).length<5){return[]}

    // Extract and format the Data and Estab fields from each file
    const Data=arq.map(({Data,Estab,...e})=>{return{Data:Data.split(",")[0],Estab:Estab.split(",")[0]}});
    const Datas=[...new Set(Data.map(JSON.stringify))].map(JSON.parse);

    const Obs_Data=arq.map(({Data,obs,...e})=>{return{Data:Data.split(",")[0],obs:obs}});
    const Obs=[...new Set(Obs_Data.map(JSON.stringify))].map(JSON.parse);

    // Aggregate the remaining fields by date and product
    const Marcas=arq.map(({Estab,Loc,Nome,obs,...rest})=>{return rest}).reduce((acc,curr)=>{
        const date=curr.Data.split(",")[0].split("-").slice(0,2).join("-");
        Object.keys(curr).forEach(field=>{if(field!=='Data'){
            let dateEntry=acc.find(entry=>entry.Data===date&&entry.Produto===field);
            if(!dateEntry){dateEntry={Data:date,Produto:field,Quant:0,Marcas:[]};acc.push(dateEntry)}
            dateEntry.Quant+=curr[field]["Quant"];
            dateEntry.Marcas=[
                dateEntry.Marcas,curr[field]["Marca"]
            ].reduce((acc,d)=>{
                Object.entries(d).forEach(([p,q])=>{acc[p]=(acc[p]||0)+q});return acc
            },{});
        }});return acc;},[]);

    // Format the aggregated data for output
    const aggregatedData=Marcas.map(entry=>{
        entry.Marcas=Object.entries(entry.Marcas).map(([key,value])=>`${key}: ${value}`).join(", ");
        entry["Data-Produto"]=`[${entry.Data}] ${entry.Produto} (${entry.Quant})`;
        delete entry.Quant;return entry});
    return [Datas,aggregatedData,Obs]};
window.dash_clientside.report={
refresh_files:async function(refr,disabled,files){
    INFO("Args:",refr,disabled);

    // Generate date options for the last five months
    const cDate=new Date();
    const dates=[{label:'Todos',value:'Todos'}];
    for(let i=0;i<5;i++){
        const fDate=`${cDate.getFullYear()}-${(cDate.getMonth()-i+1).toString().padStart(2,'0')}`;
        dates.push({label:fDate,value:fDate})
    }

    // Prepare the return value with initial data
    const retrn=[dates,files,files].concat(AgData(files));

    // If no refresh is needed, return existing data
    if(!refr>0){INFO("No update");return retrn}
    // If disabled, show an error and return existing data
    if(disabled){alert("ERRO");return retrn};
    SYNC();

    // Fetch new data from the server
    const response=await fetch('/get-file-info',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({})
    });

    // Parse the response data
    const data=await response.json();INFO("Data:",data);

    // Process the new data
    const Arquivos=Object.entries(data.info).map(([fileName,fileInfo])=>{
        const parts=fileName.replace(".csv","").split('|');
        let fileRow={
            Nome:parts[2],
            Data:`${parts[0]}, ${new Date(parts[1]*1000).toLocaleString("en-CA",{hour12:false})}`
        };
        // If the file has no location or establishment, set the values accordingly
        if (!parts[3]){fileRow.Estab="Sem estabelecimento";fileRow.Loc="Sem coordenadas"}
        else if(!parts[4]||!parts[5]){fileRow.Loc="Sem coordenadas";fileRow.Estab=parts[3].split(" ")[0]}
        else {
            let estabNear=nearest(parts[4],parts[5]);
            estabNear=`${estabNear[1].split(" ")[0]}, ${Math.round(estabNear[0]*1000)}`;
            let distEstab=Math.round(1000*haversine([parts[4],parts[5]],[COORDS[parts[3]].Latitude,COORDS[parts[3]].Longitude]));
            fileRow.Loc=`${parts[4]}, ${parts[5]}, (${estabNear}m)`;
            fileRow.Estab=`${parts[3].split(" ")[0]}, ${distEstab}m`}
        fileRow=Object.assign({},fileRow,fileInfo);
        return fileRow});

    alert("Versão atualizada");
    INFO("File data updated",data,Arquivos);
    return[dates,Arquivos,Arquivos].concat(AgData(Arquivos))
},
filter_grid:function(date_f,prd_f,est_f){
    function on(){return date_f!=='Todos'||prd_f!=='Todos'||est_f!=='Todos'}
    function pass(node){
        const data=node.data;if(date_f==='Todos'&&prd_f==='Todos'&&est_f==='Todos'){return true}
        let date=data.Data?data.Data:data["Data-Produto"],prd=data["Data-Produto"]?data["Data-Produto"]:'',estab=data.Estab?data.Estab:'';
        return(date.includes(date_f)||"Todos"===date_f)&&(prd.includes(prd_f)||"Todos"===prd_f)&&(estab.includes(est_f)||"Todos"===est_f)}
    let out={isExternalFilterPresent:on,doesExternalFilterPass:pass};
    INFO(date_f,prd_f,est_f);return[out,out,out]
}
}
