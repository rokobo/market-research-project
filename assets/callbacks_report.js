if(!window.dash_clientside){window.dash_clientside={}}
function AgData(arq){
    if(arq.length===0||Object.keys(arq[0]).length===0){return[]}
    const Data=arq.map(({Data,Estab,...e})=>{return{Data:Data.split(",")[0],Estab:Estab.split(",")[0]}});
    const Datas=[...new Set(Data.map(JSON.stringify))].map(JSON.parse);
    const Marcas=arq.map(({Estab,Loc,Nome,...rest})=>{return rest}).reduce((acc,curr)=>{
        const date=curr.Data.split(",")[0].split("-").slice(0,2).join("-");
        Object.keys(curr).forEach(field=>{if(field!=='Data'){
            let dateEntry=acc.find(entry=>entry.Data===date&&entry.Produto===field);
            if(!dateEntry){dateEntry={Data:date,Produto:field,Quant:0,Marcas:[]};acc.push(dateEntry)}
            dateEntry.Quant+=curr[field]["Quant"];
            dateEntry.Marcas=[dateEntry.Marcas,curr[field]["Marca"]].reduce((acc,d)=>{Object.entries(d).forEach(([p,q])=>{acc[p]=(acc[p]||0)+q});return acc},{});
    }});return acc;},[]);
    const aggregatedData=Marcas.map(entry=>{
        entry.Marcas=Object.entries(entry.Marcas).map(([key,value])=>`${key}: ${value}`).join(", ");
        entry["Data-Produto"]=`[${entry.Data}] ${entry.Produto} (${entry.Quant})`;
        delete entry.Quant;return entry});
    return [Datas,aggregatedData]};
window.dash_clientside.report={
refresh_files:async function(refr,disabled,fileHash,files){
    INFO(refr,disabled,fileHash);
    const retrn=[files,fileHash,files].concat(AgData(files));
    if(!refr>0){return retrn}
    if(disabled){alert("ERRO");return retrn}SYNC()
    if(!Array.isArray(fileHash)||fileHash.length!=2||files.length===0||Object.keys(files[0]).length===0){fileHash=[0,0]}INFO("Fetching new data...");
    const response=await fetch('/get-file-info',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({hash:fileHash[0]||''})});
    const data=await response.json();INFO(data);
    if(data.updated&&files.length==fileHash[1]){alert("Versão atual ok");INFO("File hash is the same");return retrn}
    const Arquivos=Object.entries(data.info).map(([fileName,fileInfo])=>{
        const parts=fileName.replace(".csv","").split('|');
        let fileRow={Nome:parts[2],Data:`${parts[0]}, ${new Date(parts[1]*1000).toLocaleString("en-CA",{hour12:false})}`};
        if (!parts[3]){}
        else if(!parts[4]||!parts[5]){fileRow.Loc="Sem coordenadas";fileRow.Estab=parts[3].split(" ")[0]}
        else {
            let estabNear=nearest(parts[4],parts[5]);
            estabNear=`${estabNear[1].split(" ")[0]}, ${Math.round(estabNear[0]*1000)}`;
            let distEstab=Math.round(1000*haversine([parts[4],parts[5]],[COORDS[parts[3]].Latitude,COORDS[parts[3]].Longitude]));
            fileRow.Loc=`${parts[4]}, ${parts[5]}, (${estabNear}m)`;
            fileRow.Estab=`${parts[3].split(" ")[0]}, ${distEstab}m`}
        fileRow=Object.assign({},fileRow,fileInfo);
        return fileRow});
    fileHash=[data.hash,Arquivos.length];alert("Versão atualizada");INFO("File hash updated",Arquivos.length,data,Arquivos);return[Arquivos,fileHash,Arquivos].concat(AgData(Arquivos))
}
}
