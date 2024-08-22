if(!window.dash_clientside){window.dash_clientside={}}
window.dash_clientside.debug={
refresh_debugs:function(_){
    let out="",lcl=Object.keys(localStorage);
    if(lcl.length==0){return "Sem itens"};
    out += `Contagem de itens: ${lcl.length}\n`;
    for(let i=0; i<lcl.length; i++){out+=`###### ${lcl[i]}:\n ${localStorage[lcl[i]]}\n`}
    return[out,new Date().toLocaleTimeString()]
}
}
