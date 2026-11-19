"use strict";
const selected=[];
const records=[];
const $=id=>document.getElementById(id);
const supported=new Set(["xml","ofx","csv"]);
const MAX_FILE_BYTES=10*1024*1024;
function formatSize(n){if(n<1024)return n+" B";if(n<1048576)return(n/1024).toFixed(1)+" KB";return(n/1048576).toFixed(1)+" MB";}
function addEvent(message){const el=document.createElement("div");el.className="event";el.textContent=new Date().toLocaleTimeString("pt-BR")+" — "+message;$("events").prepend(el);}
function cell(row,value){const td=document.createElement("td");td.textContent=value==null?"":String(value);row.append(td);}
function render(){
 $("mFiles").textContent=String(selected.length);
 $("mFormats").textContent=String(new Set(selected.filter(x=>x.status!=="REJEITADO").map(x=>x.ext)).size);
 $("mRecords").textContent=String(records.length);
 const body=$("fileRows");body.replaceChildren();
 if(!selected.length){const tr=document.createElement("tr"),td=document.createElement("td");td.colSpan=4;td.className="empty";td.textContent="Nenhum arquivo selecionado.";tr.append(td);body.append(tr);}
 for(const f of selected){const tr=document.createElement("tr");[f.name,f.ext.toUpperCase()||"—",formatSize(f.size),f.status].forEach(v=>cell(tr,v));body.append(tr);}
 const rb=$("recordRows");rb.replaceChildren();
 if(!records.length){const tr=document.createElement("tr"),td=document.createElement("td");td.colSpan=4;td.className="empty";td.textContent="Nenhum registro processado.";tr.append(td);rb.append(tr);}
 for(const r of records.slice(0,100)){const tr=document.createElement("tr");[r.source,r.date,r.amount,r.description].forEach(v=>cell(tr,v));rb.append(tr);}
}
function parseDelimited(text){
 const first=(text.split(/\r?\n/,1)[0]||"");
 const candidates=[",",";","\t"];
 const delimiter=candidates.sort((a,b)=>first.split(b).length-first.split(a).length)[0];
 const rows=[];let row=[],field="",quoted=false;
 for(let i=0;i<text.length;i++){
  const ch=text[i];
  if(ch==='"'&&quoted&&text[i+1]==='"'){field+='"';i++;}
  else if(ch==='"'){quoted=!quoted;}
  else if(ch===delimiter&&!quoted){row.push(field);field="";}
  else if((ch==="\n"||ch==="\r")&&!quoted){if(ch==="\r"&&text[i+1]==="\n")i++;row.push(field);if(row.some(v=>v.trim()!==""))rows.push(row);row=[];field="";}
  else field+=ch;
 }
 if(quoted)throw new Error("CSV contém aspas não fechadas.");
 row.push(field);if(row.some(v=>v.trim()!==""))rows.push(row);
 if(rows.length<2)throw new Error("CSV sem cabeçalho e linhas de dados.");
 const norm=s=>s.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9]/g,"");
 const headers=rows[0].map(norm);
 const find=aliases=>headers.findIndex(h=>aliases.includes(h));
 const dateI=find(["data","date","dtposted","datamovimento","datatransacao"]);
 const amountI=find(["valor","amount","trnamt","valorbruto","montante"]);
 const descI=find(["descricao","description","memo","historico","nome","name"]);
 if(dateI<0||amountI<0||descI<0)throw new Error("Cabeçalho não reconhecido: são necessários campos identificáveis de data, valor e descrição.");
 return rows.slice(1).map((r,i)=>({source:"CSV · linha "+(i+2),date:(r[dateI]||"").trim(),amount:(r[amountI]||"").trim(),description:(r[descI]||"").trim()})).filter(r=>r.date||r.amount||r.description);
}
function parseOfx(text){
 if(!/<OFX[\s>]/i.test(text))throw new Error("Estrutura OFX não identificada.");
 const matches=[...text.matchAll(/<STMTTRN>([\s\S]*?)<\/STMTTRN>/gi)];
 if(!matches.length)throw new Error("Nenhuma transação STMTTRN encontrada no OFX.");
 const tag=(block,name)=>{const m=block.match(new RegExp("<"+name+">([^<\\r\\n]*)","i"));return m?m[1].trim():"";};
 return matches.map((m,i)=>({source:"OFX · transação "+(i+1),date:tag(m[1],"DTPOSTED"),amount:tag(m[1],"TRNAMT"),description:tag(m[1],"NAME")||tag(m[1],"MEMO")}));
}
function validateXml(text){
 if(/<!DOCTYPE|<!ENTITY/i.test(text))throw new Error("XML com declaração DTD/ENTITY não aceito neste protótipo.");
 const doc=new DOMParser().parseFromString(text,"application/xml");
 if(doc.querySelector("parsererror"))throw new Error("XML malformado.");
 return doc.documentElement?doc.documentElement.nodeName:"raiz não identificada";
}
async function processFile(file){
 const ext=(file.name.split(".").pop()||"").toLowerCase();
 const item={name:file.name,size:file.size,ext,status:"RECEBIDO · NÃO PROCESSADO"};
 if(file.size>MAX_FILE_BYTES){item.status="REJEITADO · LIMITE 10 MB";selected.push(item);addEvent(file.name+" excede o limite local de 10 MB.");return;}
 if(!supported.has(ext)){item.status="NÃO SUPORTADO · SEM LEITURA";selected.push(item);addEvent(file.name+" não foi processado; formato fora do escopo atual.");return;}
 try{
  const content=await file.text();
  if(ext==="csv"){const parsed=parseDelimited(content);parsed.forEach(r=>records.push({...r,source:file.name+" · "+r.source}));item.status="CSV LIDO · "+parsed.length+" REGISTROS";addEvent(file.name+": "+parsed.length+" registros CSV normalizados, sem cálculos.");}
  else if(ext==="ofx"){const parsed=parseOfx(content);parsed.forEach(r=>records.push({...r,source:file.name+" · "+r.source}));item.status="OFX LIDO · "+parsed.length+" TRANSAÇÕES";addEvent(file.name+": "+parsed.length+" transações OFX normalizadas, sem classificação.");}
  else{const root=validateXml(content);item.status="XML BEM FORMADO · "+root;addEvent(file.name+": XML bem formado; conteúdo fiscal não extraído nem interpretado.");}
 }catch(error){item.status="ERRO DE LEITURA";addEvent(file.name+": "+error.message);}
 selected.push(item);
}
$("files").addEventListener("change",async event=>{
 const files=[...event.target.files];event.target.value="";
 for(const file of files){
  if(selected.some(x=>x.name===file.name&&x.size===file.size)){addEvent("Arquivo duplicado na sessão ignorado: "+file.name);continue;}
  await processFile(file);render();
 }
});
$("clear").addEventListener("click",()=>{selected.length=0;records.length=0;render();$("events").replaceChildren();addEvent("Sessão limpa pelo operador.");});
render();