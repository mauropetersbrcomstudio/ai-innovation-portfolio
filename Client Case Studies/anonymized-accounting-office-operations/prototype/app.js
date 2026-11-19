"use strict";
const selected=[];
const $=id=>document.getElementById(id);
const known=new Set(["xml","ofx","csv","pdf","txt","xlsx","xls"]);
function formatSize(n){if(n<1024)return n+" B";if(n<1048576)return(n/1024).toFixed(1)+" KB";return(n/1048576).toFixed(1)+" MB";}
function addEvent(message){const el=document.createElement("div");el.className="event";el.textContent=new Date().toLocaleTimeString("pt-BR")+" — "+message;$("events").prepend(el);}
function render(){
 $("mFiles").textContent=String(selected.length);
 $("mFormats").textContent=String(new Set(selected.map(x=>x.ext).filter(x=>known.has(x))).size);
 const body=$("fileRows");body.replaceChildren();
 if(!selected.length){const tr=document.createElement("tr"),td=document.createElement("td");td.colSpan=4;td.className="empty";td.textContent="Nenhum arquivo selecionado.";tr.append(td);body.append(tr);return;}
 for(const f of selected){const tr=document.createElement("tr");for(const value of [f.name,f.ext.toUpperCase()||"—",formatSize(f.size),known.has(f.ext)?"Recebido na sessão":"Formato não mapeado"]){const td=document.createElement("td");td.textContent=value;tr.append(td);}body.append(tr);}
}
$("files").addEventListener("change",event=>{
 for(const file of event.target.files){
  const ext=(file.name.split(".").pop()||"").toLowerCase();
  if(selected.some(item=>item.name===file.name&&item.size===file.size))continue;
  selected.push({name:file.name,size:file.size,ext});
  addEvent("Arquivo selecionado localmente: "+file.name+". Conteúdo não lido nem enviado.");
 }
 render();event.target.value="";
});
$("clear").addEventListener("click",()=>{selected.length=0;render();$("events").replaceChildren();addEvent("Sessão limpa pelo operador.");});
render();