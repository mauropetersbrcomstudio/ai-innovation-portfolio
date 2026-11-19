const selected = [];
const $ = (id) => document.getElementById(id);
const known = new Set(["xml","ofx","csv","pdf","txt","xlsx","xls"]);
function formatSize(n){if(n<1024)return n+" B";if(n<1048576)return (n/1024).toFixed(1)+" KB";return (n/1048576).toFixed(1)+" MB";}
function addEvent(message){const el=document.createElement("div");el.className="event";el.textContent=new Date().toLocaleTimeString("pt-BR")+" — "+message;$("events").prepend(el);}
function render(){
 $("mFiles").textContent=selected.length;
 $("mFormats").textContent=new Set(selected.map(x=>x.ext).filter(x=>known.has(x))).size;
 $("fileRows").replaceChildren();
 if(!selected.length){const tr=document.createElement("tr"),td=document.createElement("td");td.colSpan=4;td.textContent="Nenhum arquivo selecionado.";td.style.color="#82909b";tr.append(td);$("fileRows").append(tr);return;}
 for(const f of selected){const tr=document.createElement("tr");for(const value of [f.name,f.ext.toUpperCase()||"—",formatSize(f.size),"Recebido na sessão"]){const td=document.createElement("td");td.textContent=value;tr.append(td);} $("fileRows").append(tr);}
}
$("files").addEventListener("change",e=>{
 for(const f of e.target.files){const ext=(f.name.split(".").pop()||"").toLowerCase();if(selected.some(x=>x.name===f.name&&x.size===f.size))continue;selected.push({name:f.name,size:f.size,ext});addEvent("Arquivo selecionado localmente: "+f.name+" ("+(known.has(ext)?"formato reconhecido":"formato não mapeado") +"). Conteúdo não enviado.");}
 render();e.target.value="";
});
$("clear").addEventListener("click",()=>{selected.length=0;render();$("events").replaceChildren();addEvent("Sessão limpa pelo operador.");});
render();
