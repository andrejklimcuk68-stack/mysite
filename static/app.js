(()=>{const b=document.body,box=document.getElementById("cookie"),K="cookie-consent";
const get=()=>{try{return localStorage.getItem(K)}catch(e){return null}};
const set=v=>{try{localStorage.setItem(K,v)}catch(e){}};
function ga(){const id=b.dataset.ga;if(!/^G-[A-Z0-9]+$/.test(id)||window.gaLoaded)return;window.gaLoaded=1;
const s=document.createElement("script");s.async=1;s.src="https://www.googletagmanager.com/gtag/js?id="+id;document.head.appendChild(s);
window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag("js",new Date());gtag("config",id,{anonymize_ip:true})}
if(get()==="yes")ga();else if(get()===null)box.hidden=false;
box.querySelector(".yes").onclick=()=>{set("yes");box.hidden=true;ga()};
box.querySelector(".no").onclick=()=>{set("no");box.hidden=true};
document.getElementById("cookie-settings").onclick=()=>{box.hidden=false};
const a=document.querySelector("nav a.active");if(a)a.scrollIntoView({inline:"center",block:"nearest"});
const m=document.querySelector("main[data-prev]");
if(m)addEventListener("keydown",e=>{if(e.target.matches("input,textarea"))return;
if(e.key==="ArrowRight")location.href=m.dataset.next;if(e.key==="ArrowLeft")location.href=m.dataset.prev})})();
