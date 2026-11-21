(()=>{const d=document,b=d.body,$=s=>d.querySelector(s),box=$("#cookie"),K="cookie-consent";
const get=()=>{try{return localStorage.getItem(K)}catch(e){return null}},set=v=>{try{localStorage.setItem(K,v)}catch(e){}};
function ga(){const id=b.dataset.ga;if(!/^G-[A-Z0-9]+$/.test(id)||window.gaLoaded)return;window.gaLoaded=1;
const s=d.createElement("script");s.async=1;s.src="https://www.googletagmanager.com/gtag/js?id="+id;d.head.appendChild(s);
window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag("js",new Date());gtag("config",id,{anonymize_ip:true})}
if(get()==="yes")ga();else if(get()===null)box.hidden=false;
$(".yes").onclick=()=>{set("yes");box.hidden=true;ga()};$(".no").onclick=()=>{set("no");box.hidden=true};
$("#cookie-settings").onclick=()=>{box.hidden=false};
const th=$("#theme");if(th)th.onclick=()=>{const m=d.documentElement.dataset.theme=="dark"?"light":"dark";
const apply=()=>{d.documentElement.dataset.theme=m;const mt=$('meta[name="theme-color"]');if(mt)mt.content=m=="dark"?"#0f2116":"#f7f3e6"};
try{localStorage.setItem("theme",m)}catch(e){}
if(d.startViewTransition&&!matchMedia("(prefers-reduced-motion: reduce)").matches)d.startViewTransition(apply);else apply()};
const hd=$("#hd");addEventListener("scroll",()=>hd.classList.toggle("sc",scrollY>20),{passive:true});
const o=$("#open");if(o){const n=new Date(),h=n.getHours()+n.getMinutes()/60,on=h>=9&&h<20;
o.textContent=on?"● Відкрито зараз · до 20:00":"● Зараз зачинено · відкриваємось о 9:00";o.classList.toggle("on",on)}
const w=$("#when");if(w)w.min=new Date(Date.now()-new Date().getTimezoneOffset()*6e4).toISOString().slice(0,16);
const lg=$(".lang");if(lg)lg.addEventListener("click",e=>{const a=e.target.closest("a");if(!a||a.hasAttribute("aria-current")||e.ctrlKey||e.metaKey)return;e.preventDefault();lg.style.setProperty("--i",a.dataset.i);setTimeout(()=>{location.href=a.href},matchMedia("(prefers-reduced-motion: reduce)").matches?0:600)});
if(matchMedia("(prefers-reduced-motion: reduce)").matches)return;
d.documentElement.classList.add("js");
const els=d.querySelectorAll("section .eyebrow,section h2,section .sub,.card,.tile,.stat,.band>*,.hero .txt>*,.hero .art");
els.forEach(e=>{e.classList.add("rv");e.style.setProperty("--d",Math.min([...e.parentElement.children].indexOf(e),6)*120+"ms")});
const io=new IntersectionObserver(es=>es.forEach(x=>{if(!x.isIntersecting)return;const t=x.target;t.classList.add("in");io.unobserve(t);
t.addEventListener("transitionend",ev=>{if(ev.target===t&&ev.propertyName==="opacity"){t.classList.remove("rv","in");t.style.removeProperty("--d")}})}),{threshold:.1,rootMargin:"0px 0px -5% 0px"});
els.forEach(e=>io.observe(e))})();
