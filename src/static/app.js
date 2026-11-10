"use strict";
const $ = id => document.getElementById(id);
const el = (tag, value, className) => {
  const node=document.createElement(tag);
  if(value!==undefined) node.textContent=value;
  if(className) node.className=className;
  return node;
};
let benchmark=null;
function view(isBenchmark){
  $("search").hidden=isBenchmark; $("benchmark").hidden=!isBenchmark;
  $("searchTab").setAttribute("aria-pressed",String(!isBenchmark));
  $("benchTab").setAttribute("aria-pressed",String(isBenchmark));
}
$("searchTab").onclick=()=>view(false);
$("benchTab").onclick=()=>view(true);
async function request(path,body){
  const opts=body===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)};
  const r=await fetch(path,opts);
  if(!r.ok){
    const err=await r.json().catch(()=>({}));
    throw new Error(typeof err.detail==="string"?err.detail:"Request failed. Please try again.");
  }
  return r.json();
}
function highlight(text,q){
  const terms=new Set(q.toLowerCase().match(/[a-z0-9_]+/g)||[]);
  const node=el("p",undefined,"excerpt");
  for(const part of text.split(/([a-z0-9_]+)/gi)){
    node.append(terms.has(part.toLowerCase())?el("mark",part):document.createTextNode(part));
  }
  return node;
}
function showResults(id,items,q){
  const list=$(id); list.replaceChildren();
  if(!items.length)list.append(el("li","No matching results."));
  for(const [i,{chunk,score}] of items.entries()){
    const row=el("li"), meta=chunk.metadata;
    row.append(el("strong",`#${i+1} · ${score.toFixed(4)}`),
      el("p",meta.headers.join(" › ")||chunk.parent_doc),
      el("small",`${chunk.parent_doc} · lines ${meta.start_line}–${meta.end_line} · ${meta.tokens} tokens`),
      highlight(chunk.content,q));
    list.append(row);
  }
}
$("searchForm").onsubmit=async e=>{
  e.preventDefault();
  const button=e.currentTarget.querySelector("button"), query=$("query").value.trim();
  if(!query){$("searchStatus").textContent="Enter a technical query.";return;}
  button.disabled=true;$("searchStatus").textContent="Searching both indexes…";
  try{
    const d=await request("/api/search",{query,k:Number($("k").value),strategy:$("strategy").value});
    showResults("bm25",d.bm25,query);showResults("dense",d.dense,query);
    $("searchStatus").textContent=`BM25 ${d.timings.bm25.toFixed(2)} ms · dense lookup ${d.timings.dense.toFixed(2)} ms · query encoding ${d.timings.embedding.toFixed(2)} ms`;
  }catch(err){$("searchStatus").textContent=err.message;}finally{button.disabled=false;}
};
function showBenchmark(){
  if(!benchmark)return;
  const k=Number($("cutoff").value);
  $("bars").replaceChildren();$("rows").replaceChildren();$("failures").replaceChildren();
  for(const r of benchmark.rows.filter(r=>r.k===k)){
    const chart=el("div",undefined,"chartrow");chart.append(el("strong",r.name));
    for(const [label,value] of [["Hit Rate",r.hit_rate],["Recall",r.recall],["MRR",r.mrr]]){
      const row=el("div",undefined,"meter"), meter=el("meter");
      meter.max=1;meter.value=value;meter.setAttribute("aria-label",`${r.name} ${label}`);
      row.append(el("span",label),meter,el("span",value.toFixed(3)));chart.append(row);
    }
    $("bars").append(chart);
    const row=el("tr");row.append(el("td",r.name));
    for(const key of ["hit_rate","recall","mrr","avg_ms","p50_ms","p95_ms","embedding_ms"])row.append(el("td",r[key].toFixed(3)));
    $("rows").append(row);
  }
  for(const f of benchmark.failures){
    const row=el("article",undefined,"case");
    row.append(el("strong",`${f.winner} ranked evidence higher · ${f.kind}`),el("p",f.query),
      el("p",`Reciprocal rank: BM25 ${f.bm25.toFixed(2)} · dense ${f.dense.toFixed(2)}. ${f.hint}`));
    for(const e of f.evidence) row.append(el("p",`Evidence · ${e.doc}: ${e.quote}`));
    $("failures").append(row);
  }
  if(!benchmark.failures.length)$("failures").append(el("p","No differences in first relevant rank at K=5."));
  $("benchResults").hidden=false;
}
$("cutoff").onchange=showBenchmark;
$("run").onclick=async()=>{
  $("run").disabled=true;$("benchStatus").textContent="Running the evaluation…";
  try{
    benchmark=await request("/api/benchmark",{});
    $("benchStatus").textContent=`${benchmark.queries} queries completed. ${benchmark.latency_scope}`;
    showBenchmark();
  }catch(err){$("benchStatus").textContent=err.message;}finally{$("run").disabled=false;}
};
request("/api/info").then(x=>{
  $("docs").textContent=`${x.documents} source documents`;
  $("queries").textContent=`${x.queries} labeled queries`;
  for(const v of x.examples){
    const b=el("button",v.kind==="exact"?"Try exact identifier":"Try conceptual query");
    b.type="button";b.onclick=()=>{$("query").value=v.query;$("query").focus();};$("examples").append(b);
  }
}).catch(()=>{});
