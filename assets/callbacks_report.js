if(!window.dash_clientside){window.dash_clientside={}}
window.dash_clientside.report={
refresh_files:async function(refr,disabled,fileHash,files){
    INFO(refr,disabled,fileHash);
    if(!refr>0){return [files,fileHash,files]}
    if(disabled){alert("ERRO");return [NOUPDATE,fileHash,files]}SYNC();
    if(!Array.isArray(fileHash)||fileHash.length!=2||files.length==0){fileHash=[0,0]}
    const response=await fetch('/get-file-names',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({hash:fileHash[0]||''})});
    const data=await response.json();
    if(data.updated&&files.length==fileHash[1]){alert("Versão atual ok");INFO("File hash is the same");return [files,fileHash,files]}
    const agData=data.file_names.map(fileName=>{
        const parts=fileName.replace(".csv", "").split('|');
        let fileRow={Nome:parts[2],Data:`${parts[0]}, ${new Date(parts[1]*1000).toLocaleString("en-CA",{hour12:false})}`};
        if(!parts[4]||!parts[5]){fileRow.Loc="Sem coordenadas";fileRow.Estab=parts[3].split(" ")[0]}
        else {
            estabNear=nearest(parts[4],parts[5]);
            estabNear=`${estabNear[1].split(" ")[0]}, ${Math.round(estabNear[0]*1000)}`;
            distEstab=Math.round(1000*haversine([parts[4],parts[5]],[COORDS[parts[3]].Latitude,COORDS[parts[3]].Longitude]));
            fileRow.Loc=`${parts[4]}, ${parts[5]}, (${estabNear}m)`;
            fileRow.Estab=`${parts[3].split(" ")[0]}, ${distEstab}m`;
        }
        return fileRow
    });fileHash=[data.hash,agData.length];alert("Versão atualizada");INFO("File hash updated",agData.length,data,agData);return [agData,fileHash,agData]
}
}
