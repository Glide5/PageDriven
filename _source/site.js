/* PageDriven shared site script: every block checks that its elements exist, so one file serves every page. */
(function(){
"use strict";
var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
var hasG = typeof window.gsap !== "undefined" && typeof window.ScrollTrigger !== "undefined";
var hasT = typeof window.THREE !== "undefined";
function $(id){ return document.getElementById(id); }
function each(sel,fn,root){ Array.prototype.forEach.call((root||document).querySelectorAll(sel),fn); }

var PROCESS = [
  ["Diagnose","We review your offer, audience, traffic source, current page, competitors, and conversion goal."],
  ["Structure","We map the page flow and define the right sections to guide visitors toward action."],
  ["Write & design","We write conversion-focused copy and design a clean layout around one clear action."],
  ["Build","We build on your chosen platform with responsive, accessible implementation."],
  ["Improve","For ongoing engagements we watch performance signals and keep improving the page."]
];

/* ---------- Smooth scroll ---------- */
var lenis=null;
function scrollToY(y){ if(lenis) lenis.scrollTo(y,{duration:1.2}); else window.scrollTo({top:y,behavior:reduce?"auto":"smooth"}); }
function scrollToEl(t,off){ scrollToY(t.getBoundingClientRect().top+(window.scrollY||0)-(off||80)); }

/* ---------- Nav: scrolled state, services menu, mobile menu ---------- */
var nav=$("nav");
var menuBtn=$("svcBtn"), menu=$("svcMenu"), menuWrap=menuBtn?menuBtn.parentNode:null, closeT;
function setMenu(open){
  if(!menu) return;
  menu.classList.toggle("open",open); menuBtn.setAttribute("aria-expanded",String(open));
}
if(menu){
  menuWrap.addEventListener("mouseenter",function(){ clearTimeout(closeT); setMenu(true); });
  menuWrap.addEventListener("mouseleave",function(){ closeT=setTimeout(function(){ setMenu(false); },140); });
  menuBtn.addEventListener("click",function(){ setMenu(!menu.classList.contains("open")); });
  menuWrap.addEventListener("focusout",function(e){ if(!menuWrap.contains(e.relatedTarget)) setMenu(false); });
  document.addEventListener("keydown",function(e){ if(e.key==="Escape" && menu.classList.contains("open")){ setMenu(false); menuBtn.focus(); } });
}
var mBtn=$("mnavBtn"), mNav=$("mnav");
if(mBtn && mNav){
  mBtn.addEventListener("click",function(){
    var open=mNav.hidden; mNav.hidden=!open; mBtn.setAttribute("aria-expanded",String(open));
    mBtn.setAttribute("aria-label",open?"Close menu":"Open menu"); document.documentElement.classList.toggle("mnav-open",open);
    if(open && hasG && !reduce) gsap.from("#mnav .mnav-in > *",{y:12,opacity:0,duration:.35,stagger:.03,ease:"power2.out"});
  });
  each("#mnav a",function(a){ a.addEventListener("click",function(){ mNav.hidden=true; mBtn.setAttribute("aria-expanded","false"); document.documentElement.classList.remove("mnav-open"); }); });
}
var mbar=$("mbar"), ctaEl=document.querySelector(".cta");
function onScrollUI(){
  var y=window.scrollY||document.documentElement.scrollTop;
  if(nav) nav.classList.toggle("scrolled",y>20);
  if(mbar) mbar.classList.toggle("show", y>window.innerHeight*0.8 && (!ctaEl || ctaEl.getBoundingClientRect().top>window.innerHeight));
}
window.addEventListener("scroll",onScrollUI,{passive:true}); onScrollUI();

/* ---------- Static ribbon art ---------- */
function hexRgb(h){ h=h.replace("#",""); return [parseInt(h.substr(0,2),16),parseInt(h.substr(2,2),16),parseInt(h.substr(4,2),16)]; }
/* ---------- Project thumbnails: the ribbon wave, each project at its own angle and zoom, drifting slowly ---------- */
var arts=[];
function sizeArt(st){
  var dpr=Math.min(1.5,window.devicePixelRatio||1); st.w=st.cv.clientWidth||392; st.h=st.cv.clientHeight||368;
  st.cv.width=Math.round(st.w*dpr); st.cv.height=Math.round(st.h*dpr); st.dpr=dpr; st.c=st.cv.getContext("2d");
}
function drawRibbon(st,time){
  var c=st.c,w=st.w,h=st.h,o=st.o,z=o.zoom||1; c.setTransform(st.dpr,0,0,st.dpr,0,0);
  c.fillStyle=o.bg; c.fillRect(0,0,w,h);
  var g=c.createRadialGradient(w*.7,h*.25,0,w*.5,h*.5,Math.max(w,h)*.9); g.addColorStop(0,"rgba(255,255,255,.10)"); g.addColorStop(1,"rgba(0,0,0,.16)"); c.fillStyle=g; c.fillRect(0,0,w,h);
  c.save(); c.translate(w/2,h/2); c.rotate((o.angle||0)*Math.PI/180); c.scale(z,z); c.translate(-w/2,-h/2);
  /* control points drift a little so the ribbon breathes */
  var P=o.pts.map(function(p,k){ return [p[0]*w+Math.sin(time*.23+k*1.7)*w*.025, p[1]*h+Math.cos(time*.29+k*2.1)*h*.04]; });
  function bz(t,i){var u=1-t;return u*u*u*P[0][i]+3*u*u*t*P[1][i]+3*u*t*t*P[2][i]+t*t*t*P[3][i];}
  function db(t,i){var u=1-t;return 3*u*u*(P[1][i]-P[0][i])+6*u*t*(P[2][i]-P[1][i])+3*t*t*(P[3][i]-P[2][i]);}
  var N=84, S=90, B=16, buckets=[], k; for(k=0;k<B;k++) buckets.push([]);
  var W=o.width*Math.min(w,h);
  for(var i=0;i<N;i++){
    var v=i/(N-1)*2-1, prev=null, stripe=(i%4===0)?-0.16:(i%2?0.04:0);
    for(var j=0;j<=S;j++){
      var t=j/S, x=bz(t,0), y=bz(t,1), dx=db(t,0), dy=db(t,1), L=Math.hypot(dx,dy)||1, nx=-dy/L, ny=dx/L;
      var th=o.phase+o.twist*Math.PI*t+time*.22, wt=W*(0.55+0.6*Math.sin(Math.PI*t)), cs=Math.cos(th), sn=Math.sin(th);
      var px=x+nx*wt*v*cs+dx/L*wt*v*sn*.22, py=y+ny*wt*v*cs+dy/L*wt*v*sn*.22;
      var lit=0.22+0.78*Math.pow(Math.abs(Math.sin(th+0.9)),1.4);
      lit*= cs>=0 ? (0.78+0.22*(v*.5+.5)) : (0.62+0.18*(1-(v*.5+.5)));
      lit=Math.max(0,Math.min(.999,lit+stripe));
      if(prev) buckets[(lit*B)|0].push(prev[0],prev[1],px,py);
      prev=[px,py];
    }
  }
  var dk=st.dk, lt=st.lt; c.lineCap="round"; c.lineWidth=0.85/z;
  for(var b=0;b<B;b++){ var a=buckets[b]; if(!a.length) continue; var l=(b+.5)/B;
    c.strokeStyle="rgba("+Math.round(dk[0]+(lt[0]-dk[0])*l)+","+Math.round(dk[1]+(lt[1]-dk[1])*l)+","+Math.round(dk[2]+(lt[2]-dk[2])*l)+","+(0.55+0.4*l).toFixed(2)+")";
    c.beginPath(); for(var q=0;q<a.length;q+=4){ c.moveTo(a[q],a[q+1]); c.lineTo(a[q+2],a[q+3]); } c.stroke(); }
  c.restore();
}
each("canvas[data-art]",function(cv){
  try{ var st={cv:cv,o:JSON.parse(cv.getAttribute("data-art")),vis:true}; st.dk=hexRgb(st.o.dark); st.lt=hexRgb(st.o.light);
    sizeArt(st); drawRibbon(st,0); arts.push(st);
    if("IntersectionObserver" in window) new IntersectionObserver(function(es){ st.vis=es[0].isIntersecting; }).observe(cv); }catch(e){}
});
/* one shared loop, ~24fps, only for thumbnails on screen */
if(arts.length && !reduce){ var artLast=0; (function artLoop(now){ if(now-artLast>41){ artLast=now; var s=now/1000; arts.forEach(function(st){ if(st.vis) drawRibbon(st,s); }); } requestAnimationFrame(artLoop); })(0); }
var artT; window.addEventListener("resize",function(){ clearTimeout(artT); artT=setTimeout(function(){ arts.forEach(function(st){ sizeArt(st); drawRibbon(st,reduce?0:performance.now()/1000); }); },250); });

/* ---------- Carousels ---------- */
each(".hs",function(sec){
  var outer=sec.querySelector(".hs-outer"), track=sec.querySelector(".hs-track"), bar=sec.querySelector(".hs-progress i"),
      cnt=sec.querySelector(".hs-count"), prevB=sec.querySelector(".hs-prev"), nextB=sec.querySelector(".hs-next");
  if(!outer||!track) return;
  var n=track.children.length;
  function stepW(){ var cd=track.firstElementChild; return cd ? cd.getBoundingClientRect().width+24 : 400; }
  function upd(){
    var max=outer.scrollWidth-outer.clientWidth, p=max>0?outer.scrollLeft/max:0;
    if(bar) bar.style.transform="scaleX("+(0.14+p*0.86)+")";
    var idx=Math.min(n,Math.round(outer.scrollLeft/stepW())+1);
    if(cnt) cnt.textContent=("0"+idx).slice(-2)+" / "+("0"+n).slice(-2);
    if(prevB) prevB.disabled=outer.scrollLeft<4; if(nextB) nextB.disabled=outer.scrollLeft>max-4;
  }
  if(prevB) prevB.addEventListener("click",function(){ outer.scrollBy({left:-stepW(),behavior:reduce?"auto":"smooth"}); });
  if(nextB) nextB.addEventListener("click",function(){ outer.scrollBy({left:stepW(),behavior:reduce?"auto":"smooth"}); });
  outer.addEventListener("scroll",upd,{passive:true}); window.addEventListener("resize",upd); upd();
  var down=false, sx=0, sl=0, moved=false;
  outer.addEventListener("pointerdown",function(e){ if(e.pointerType!=="mouse") return; down=true; moved=false; sx=e.clientX; sl=outer.scrollLeft; });
  window.addEventListener("pointermove",function(e){ if(!down) return; var d=e.clientX-sx; if(Math.abs(d)>4){ moved=true; outer.classList.add("drag"); } if(moved) outer.scrollLeft=sl-d; });
  window.addEventListener("pointerup",function(){ if(!down) return; down=false; outer.classList.remove("drag"); });
  outer.addEventListener("click",function(e){ if(moved){ e.preventDefault(); e.stopPropagation(); moved=false; } },true);
});

/* ---------- Work index filters ---------- */
each(".filters",function(f){
  var list=$(f.getAttribute("data-for")); if(!list) return;
  each("button",function(b){
    b.addEventListener("click",function(){
      var k=b.getAttribute("data-filter");
      each("button",function(o){ o.setAttribute("aria-pressed",String(o===b)); },f);
      var n=0; each("[data-service]",function(it){ it.hidden = !(k==="all" || it.getAttribute("data-service")===k); if(!it.hidden) n++; },list);
      var em=list.parentNode.querySelector(".wempty"); if(em) em.hidden = n>0;
      if(hasG) ScrollTrigger.refresh();
    });
  },f);
  each("[data-filter-reset]",function(r){ r.addEventListener("click",function(){ var all=f.querySelector('[data-filter="all"]'); if(all) all.click(); }); },list.parentNode);
});

/* ---------- Compare sliders ---------- */
each(".compare",function(cmp){
  var rng=cmp.querySelector(".cmp-range"); if(!rng) return;
  rng.addEventListener("input",function(){ cmp.style.setProperty("--split",rng.value+"%"); });
});

/* ---------- Copy buttons ---------- */
each("[data-copy]",function(b){
  b.addEventListener("click",function(){
    var txt=b.getAttribute("data-copy"), done=function(){ b.textContent="Copied"; setTimeout(function(){ b.textContent="Copy"; },1600); };
    function sel(){ var el=$(b.getAttribute("data-copy-el")); if(!el) return; var r=document.createRange(); r.selectNodeContents(el); var s=getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent="Press ⌘C"; }
    try{ navigator.clipboard.writeText(txt).then(done,sel); }catch(e){ sel(); }
  });
});

/* ---------- Form delivery: POST to Formspree, which emails every submission to riz@gopagedriven.com ---------- */
var FORM_ENDPOINT="https://formspree.io/f/xwlllyvv", FORM_INBOX="riz@gopagedriven.com";
/* no backend behind the claude.ai preview or a local file, so submissions there are only simulated */
var FORM_PREVIEW=location.protocol==="file:" || /(^|\.)(claude\.ai|claudeusercontent\.com|anthropic\.com)$/.test(location.hostname);
var FORM_FAIL='Couldn\u2019t send right now. Please email <a href="mailto:'+FORM_INBOX+'">'+FORM_INBOX+'</a> instead.';
var FORM_NAME={review:["Free page review","Page review request from "],contact:["Contact","New message from "],chat:["Chat widget","Chat question from "]};
/* resolves only once Formspree answers {ok:true}; anything else rejects, with .field set when Formspree flags a field */
function sendForm(kind,data,form){
  var hp=form && form.querySelector('[name="website"]');
  if(hp && hp.value) return Promise.resolve({}); /* spam trap: real visitors never fill the hidden "website" field */
  data.form=FORM_NAME[kind][0]; data.page=location.pathname; data._subject=FORM_NAME[kind][1]+(data.name||data.email);
  if(FORM_PREVIEW) return Promise.resolve({preview:true});
  var body=new FormData(); Object.keys(data).forEach(function(k){ body.append(k,data[k]); });
  var ctl=("AbortController" in window) ? new AbortController() : null, timer=setTimeout(function(){ if(ctl) ctl.abort(); },15000);
  return fetch(FORM_ENDPOINT,{method:"POST",headers:{"Accept":"application/json"},body:body,signal:ctl?ctl.signal:undefined})
    .then(function(r){ return r.json().catch(function(){ return {}; }).then(function(j){
      clearTimeout(timer);
      if(r.ok && j.ok) return {};
      var errs=j.errors||[], e=new Error(errs.map(function(x){ return x.message; }).join("; ")||j.error||"HTTP "+r.status);
      e.field=errs[0] && errs[0].field; throw e;
    }); })
    .catch(function(e){ clearTimeout(timer); if(window.console) console.warn("Form not sent:",e.message); throw e; });
}
function formError(e){ return e && e.field==="email" ? "Enter a valid email address, for example you@company.com." : FORM_FAIL; }
function formBusy(btn,on){
  if(!btn) return;
  if(on){ btn.setAttribute("data-label",btn.innerHTML); btn.disabled=true; btn.textContent="Sending\u2026"; }
  else { btn.disabled=false; if(btn.hasAttribute("data-label")) btn.innerHTML=btn.getAttribute("data-label"); }
}
function previewNote(box,res){
  var old=box.querySelector(".pv-note"); if(old) old.remove();
  if(!res || !res.preview) return;
  var p=document.createElement("p"); p.className="pv-note"; p.textContent="Preview only: this wasn\u2019t sent. On the live Vercel site it\u2019s emailed to "+FORM_INBOX+".";
  box.appendChild(p);
}

/* ---------- Review modal (two-step) ---------- */
var dlg=$("review");
var openReview=function(){};
if(dlg){
  var form=$("reviewForm"), step=1, s1=$("s1"), s2=$("s2"), s3=$("s3"), err=$("mErr");
  var mNext=$("mNext"), mBack=$("mBack"), mProg=$("mProg"), mStep=$("m-step"), mTitle=$("m-title"), mActs=$("mActs");
  var renderStep=function(){
    s1.hidden=step!==1; s2.hidden=step!==2; s3.hidden=step!==3; mActs.hidden=step===3; mBack.hidden=step!==2; err.textContent="";
    mProg.style.width=(step===1?50:100)+"%";
    mStep.textContent= step===3 ? "Done" : "Step "+step+" of 2";
    mTitle.textContent= step===1 ? "Which page should Riz review?" : step===2 ? "Where should the review go?" : "You're on the list";
    mNext.innerHTML = step===1 ? 'Continue <span class="arr">→</span>' : 'Send my review request <span class="arr">→</span>';
  };
  openReview=function(svc){
    if(svc) $("f-svc").value=svc;
    if(step===3){ form.reset(); step=1; }
    renderStep();
    if(dlg.showModal){ if(!dlg.open) dlg.showModal(); } else dlg.setAttribute("open","");
    setTimeout(function(){ var f=$(step===1?"f-url":"f-name"); if(f) f.focus(); },50);
  };
  $("mClose").addEventListener("click",function(){ dlg.close ? dlg.close() : dlg.removeAttribute("open"); });
  dlg.addEventListener("click",function(e){ if(e.target===dlg && dlg.close) dlg.close(); });
  mBack.addEventListener("click",function(){ step=1; renderStep(); });
  form.addEventListener("submit",function(e){
    e.preventDefault();
    if(step===1){
      var u=$("f-url").value.trim();
      if(!/^(https?:\/\/)?[\w-]+(\.[\w-]+)+/.test(u)){ err.textContent="Enter the page address, for example yourbusiness.com/landing-page."; return; }
      step=2; renderStep(); $("f-name").focus(); return;
    }
    if(step===2){
      var n=$("f-name").value.trim(), em=$("f-email").value.trim();
      if(!n){ err.textContent="Add your name so Riz knows who to address."; return; }
      if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)){ err.textContent="Enter a valid email address, for example you@company.com."; return; }
      var goal=form.querySelector('[name="goal"]:checked');
      formBusy(mNext,true);
      sendForm("review",{url:$("f-url").value.trim(),goal:goal?goal.value:"",service:$("f-svc").value,name:n,email:em},form).then(function(res){
        formBusy(mNext,false);
        $("okTitle").textContent="Thanks, "+n.split(" ")[0]+". Request received.";
        step=3; renderStep(); previewNote(s3,res);
      },function(e){ formBusy(mNext,false); err.innerHTML=formError(e); });
    }
  });
  each("[data-open-review]",function(b){ b.addEventListener("click",function(e){ e.preventDefault(); openReview(b.getAttribute("data-service")); }); });
}

/* ---------- Contact modal ---------- */
var cdlg=$("contact");
function openContact(){ if(!cdlg) return; $("cForm").hidden=false; $("cOk").hidden=true; $("cErr").textContent=""; if(cdlg.showModal){ if(!cdlg.open) cdlg.showModal(); } else cdlg.setAttribute("open",""); setTimeout(function(){ $("c-name").focus(); },50); }
if(cdlg){
  each("[data-open-contact]",function(b){ b.addEventListener("click",function(e){ e.preventDefault(); openContact(); }); });
  $("cClose").addEventListener("click",function(){ cdlg.close ? cdlg.close() : cdlg.removeAttribute("open"); });
  cdlg.addEventListener("click",function(e){ if(e.target===cdlg && cdlg.close) cdlg.close(); });
  $("cForm").addEventListener("submit",function(e){
    e.preventDefault();
    var n=$("c-name").value.trim(), em=$("c-email").value.trim(), m=$("c-msg").value.trim(), er=$("cErr");
    if(!n){ er.textContent="Add your name."; return; }
    if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)){ er.textContent="Enter a valid email address, for example you@company.com."; return; }
    if(m.length<5){ er.textContent="Add a short message so Riz knows what you need."; return; }
    var cbtn=$("cForm").querySelector('[type="submit"]'); er.textContent=""; formBusy(cbtn,true);
    sendForm("contact",{name:n,email:em,message:m},$("cForm")).then(function(res){
      formBusy(cbtn,false); $("cForm").hidden=true; $("cOk").hidden=false; $("cOkT").textContent="Thanks, "+n.split(" ")[0]+". Message received.";
      previewNote($("cOk"),res); $("cForm").reset();
    },function(e){ formBusy(cbtn,false); er.innerHTML=formError(e); });
  });
}

/* ---------- Inline review form (Book, Work) ---------- */
each(".inline-review",function(f){
  f.addEventListener("submit",function(e){
    e.preventDefault();
    var g=function(n){ return f.querySelector('[name="'+n+'"]'); }, er=f.querySelector(".err");
    if(!/^(https?:\/\/)?[\w-]+(\.[\w-]+)+/.test(g("url").value.trim())){ er.textContent="Enter the page address, for example yourbusiness.com/landing-page."; return; }
    if(!g("name").value.trim()){ er.textContent="Add your name so Riz knows who to address."; return; }
    if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(g("email").value.trim())){ er.textContent="Enter a valid email address, for example you@company.com."; return; }
    var ibtn=f.querySelector('[type="submit"]'), nm=g("name").value.trim(); er.textContent=""; formBusy(ibtn,true);
    sendForm("review",{url:g("url").value.trim(),goal:g("goal")?g("goal").value:"",service:"Free Page Review",name:nm,email:g("email").value.trim()},f).then(function(res){
      formBusy(ibtn,false); f.querySelector(".ir-fields").hidden=true; var ok=f.querySelector(".ir-ok"); ok.hidden=false;
      ok.querySelector("h3").textContent="Thanks, "+nm.split(" ")[0]+". Request received."; previewNote(ok,res);
    },function(e){ formBusy(ibtn,false); er.innerHTML=formError(e); });
  });
});

/* ---------- Video testimonial ---------- */
each(".vposter",function(btn){
  btn.addEventListener("click",function(){
    var f=document.createElement("iframe");
    f.src="https://www.youtube-nocookie.com/embed/"+btn.getAttribute("data-yt")+"?autoplay=1&rel=0&modestbranding=1";
    f.title=btn.getAttribute("aria-label")||"Video"; f.allow="autoplay; encrypted-media; picture-in-picture; fullscreen"; f.allowFullscreen=true;
    var p=btn.parentNode; p.innerHTML=""; p.appendChild(f);
  });
});

/* ---------- Scroll-lit statement: wrap words ---------- */
var litEls=[];
each("[data-words]",function(el){
  (function wrap(node){ Array.prototype.slice.call(node.childNodes).forEach(function(n){
    if(n.nodeType===3){ var frag=document.createDocumentFragment();
      n.textContent.split(/(\s+)/).forEach(function(part){ if(!part) return;
        if(/^\s+$/.test(part)) frag.appendChild(document.createTextNode(part));
        else { var sp=document.createElement("span"); sp.className="w"; sp.textContent=part; frag.appendChild(sp); } });
      n.parentNode.replaceChild(frag,n); }
    else if(n.nodeType===1) wrap(n);
  }); })(el);
  litEls.push(el);
});

/* ---------- Solution rows: active row follows scroll and hover ---------- */
each(".sol-rows",function(box){
  var rows=box.querySelectorAll(".sol-row");
  function set(r){ Array.prototype.forEach.call(rows,function(x){ x.classList.toggle("on",x===r); }); }
  Array.prototype.forEach.call(rows,function(r){ r.addEventListener("mouseenter",function(){ set(r); }); r.addEventListener("focus",function(){ set(r); }); });
  if("IntersectionObserver" in window){
    var io=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting && !box.matches(":hover")) set(e.target); }); },{rootMargin:"-45% 0px -45% 0px"});
    Array.prototype.forEach.call(rows,function(r){ io.observe(r); });
  }
});

/* ---------- Engagement cards: hovered or focused card expands ---------- */
each(".ecards",function(box){
  var cards=box.querySelectorAll(".ecard");
  function set(c){ Array.prototype.forEach.call(cards,function(x){ x.classList.toggle("on",x===c); }); }
  Array.prototype.forEach.call(cards,function(c){ ["mouseenter","focus","click"].forEach(function(ev){ c.addEventListener(ev,function(){ set(c); }); }); });
});

/* ---------- Platforms: three cursor chips at a time, random spots ---------- */
each(".plat-stage",function(stage){
  var chips=Array.prototype.slice.call(stage.querySelectorAll(".pchip")); if(chips.length<2) return;
  var sec=stage.parentNode, visible=true, order=[], oi=0;
  /* zones as [xmin,xmax,ymin,ymax,side] in % of the stage, kept clear of the centered heading; three of four are used per cycle */
  var ZD=[[1,12,5,18,"L"],[2,15,72,85,"L"],[66,76,5,18,"R"],[62,74,72,85,"R"]];
  var ZM=[[0,6,2,8,"L"],[48,54,2,8,"R"],[0,8,88,93,"L"],[46,52,88,93,"R"]];
  function rnd(a,b){ return a+Math.random()*(b-a); }
  function shuffle(a){ for(var i=a.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1)), t=a[i]; a[i]=a[j]; a[j]=t; } return a; }
  function nextChip(){ if(oi>=order.length){ order=shuffle(chips.slice()); oi=0; } return order[oi++]; }
  function place(ch,side,z){
    ch.classList.toggle("r",side==="R");
    var w=stage.clientWidth, h=stage.clientHeight, cw=ch.offsetWidth||220, chh=ch.offsetHeight||66;
    var x=rnd(z[0],z[1])/100*w, y=rnd(z[2],z[3])/100*h;
    x=side==="R" ? Math.max(70,Math.min(w-cw-16,x)) : Math.max(16,Math.min(w-cw-70,x));
    y=Math.max(12,Math.min(h-chh-50,y));
    ch.style.left=x+"px"; ch.style.top=y+"px";
    aim(ch,x,y,cw,chh);
  }
  /* point the cursor from the chip's edge toward the centre of the heading */
  function aim(ch,x,y,cw,chh){
    var cur=ch.querySelector(".pc-cur"), hd=sec.querySelector(".plat-h"); if(!cur||!hd) return;
    var sr=stage.getBoundingClientRect(), hr=hd.getBoundingClientRect();
    var tx=hr.left-sr.left+hr.width/2, ty=hr.top-sr.top+hr.height/2;
    var cx=x+cw/2, cy=y+chh/2, dx=tx-cx, dy=ty-cy, L=Math.hypot(dx,dy)||1, nx=dx/L, ny=dy/L;
    var t=Math.min((cw/2)/Math.max(Math.abs(nx),1e-3),(chh/2)/Math.max(Math.abs(ny),1e-3));
    var cs=cur.offsetWidth||28, px=cw/2+nx*(t+cs*0.62), py=chh/2+ny*(t+cs*0.62);
    var rot=Math.atan2(ny,nx)*180/Math.PI+135; /* the arrow's tip points up-left (-135deg) by default */
    cur.style.left=(px-cs*5/32)+"px"; cur.style.top=(py-cs*3.5/32)+"px";
    cur.style.setProperty("--rot",rot.toFixed(1)+"deg"); cur.style.setProperty("--nx",nx.toFixed(3)); cur.style.setProperty("--ny",ny.toFixed(3));
  }
  function zonesFor(){ return window.innerWidth<760?ZM:ZD; }
  if(reduce){ var z0=zonesFor(); for(var k=0;k<Math.min(3,chips.length);k++){ place(chips[k],z0[k][4],z0[k]); chips[k].classList.add("show"); } return; }
  if("IntersectionObserver" in window) new IntersectionObserver(function(es){ visible=es[0].isIntersecting; }).observe(sec);
  (function cycle(){
    if(!visible || document.hidden){ setTimeout(cycle,700); return; }
    var zs=shuffle(zonesFor().slice()).slice(0,Math.min(3,chips.length)), picked=[];
    while(picked.length<zs.length){ var c=nextChip(); if(picked.indexOf(c)<0) picked.push(c); }
    picked.forEach(function(ch,k){ place(ch,zs[k][4],zs[k]); });
    picked.forEach(function(ch,k){ setTimeout(function(){ ch.classList.add("show"); },40+k*380); });
    setTimeout(function(){
      picked.forEach(function(ch,k){ setTimeout(function(){ ch.classList.remove("show"); },k*200); });
      setTimeout(cycle,1100);
    },4200);
  })();
});

/* ---------- Process arc ---------- */
var arcPinned=false, procST=null, setArc=null;
if($("arcWrap")){
  var CX=500, CY=500, R=440, nodesG=$("arcNodes"), labels=$("arcLabels"), nodeHTML="", labHTML="";
  PROCESS.forEach(function(p,i){
    var a=Math.PI*(1-i/4), x=CX+R*Math.cos(a), y=CY-R*Math.sin(a);
    nodeHTML+='<circle class="anode" cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="6" fill="#0B2545" stroke="rgba(255,255,255,.45)" stroke-width="1.5"/>';
    var dx=Math.cos(a)*86, dy=-Math.sin(a)*34;
    labHTML+='<button type="button" class="node-lbl" data-step="'+i+'" style="left:'+(x/10)+'%;top:'+(y/5.4)+'%;margin-left:'+dx.toFixed(0)+'px;margin-top:'+dy.toFixed(0)+'px"><span>0'+(i+1)+'</span>'+p[0].replace("&","&amp;")+'</button>';
  });
  nodesG.innerHTML=nodeHTML; labels.innerHTML=labHTML;
  $("stepsList").innerHTML = PROCESS.map(function(p,i){return '<li><span>STEP 0'+(i+1)+'</span><h3>'+p[0].replace("&","&amp;")+'</h3><p>'+p[1]+'</p></li>'}).join("");
  var curStep=-1, comet=$("comet"), cometGlow=$("cometGlow"), arcProg=$("arcProg"), stepN=$("stepN"), stepT=$("stepT"), stepB=$("stepB");
  var lblEls=labels.querySelectorAll(".node-lbl"), nodeEls=nodesG.querySelectorAll(".anode");
  setArc=function(p){
    p=Math.max(0,Math.min(1,p));
    var a=Math.PI*(1-p), x=CX+R*Math.cos(a), y=CY-R*Math.sin(a);
    comet.setAttribute("cx",x); comet.setAttribute("cy",y); cometGlow.setAttribute("cx",x); cometGlow.setAttribute("cy",y);
    arcProg.setAttribute("stroke-dashoffset",(1382.3*(1-p)).toFixed(1));
    var s=Math.min(4,Math.round(p*4));
    Array.prototype.forEach.call(nodeEls,function(n,i){ n.setAttribute("fill", i<=s?"#A79CFF":"#0B2545"); });
    if(s!==curStep){
      curStep=s;
      Array.prototype.forEach.call(lblEls,function(l,i){ l.classList.toggle("on",i===s); });
      var apply=function(){ stepN.textContent="STEP 0"+(s+1)+" / 05"; stepT.textContent=PROCESS[s][0]; stepB.textContent=PROCESS[s][1]; };
      if(hasG && !reduce){ gsap.to([stepT,stepB,stepN],{opacity:0,y:8,duration:.18,onComplete:function(){apply();gsap.to([stepN,stepT,stepB],{opacity:1,y:0,duration:.35,stagger:.04,ease:"power2.out"});}}); }
      else apply();
    }
  };
  setArc(0);
  Array.prototype.forEach.call(lblEls,function(l){
    l.addEventListener("click",function(){
      var i=+l.getAttribute("data-step");
      if(arcPinned && procST) scrollToY(procST.start+(procST.end-procST.start)*(i/4)+2); else setArc(i/4);
    });
  });
}

/* ---------- Chat widget (scripted answers from site content) ---------- */
var chat=$("chat");
if(chat){
  var panel=$("chatPanel"), fab=$("chatFab"), log=$("chatLog"), quick=$("chatQuick"), cin=$("chatIn"), teaser=$("chatTeaser");
  var chatStarted=false, awaitingEmail=false, chatQ="";
  var FAQ = {
    time:"Most landing pages are completed in 5–7 business days, depending on scope and feedback rounds. Rush timelines are available.",
    platform:"Webflow, WordPress, Shopify, Unbounce, ClickFunnels, HighLevel, HubSpot, Wix, and more. We build where your page already lives, so you do not need to migrate.",
    agency:"Yes. We provide white-label landing pages, location pages, website production, UX improvements, and technical support for SEO, PPC, and digital agencies.",
    ab:"Where it makes sense. Reliable experiments need sufficient traffic and trustworthy tracking. We'll tell you honestly whether your traffic supports testing, and prioritize direct, evidence-based improvements when it doesn't.",
    who:"Riz leads discovery, conversion strategy, and final quality review on every engagement, supported by a specialist copy, design, and development team.",
    where:"Working with businesses and agencies across the US and Canada. Remote collaboration with daily availability for meetings during US business hours."
  };
  var ANS = {
    review:{t:"The free page review is a short, personal look at one page: where it's most likely losing momentum and the three highest-impact fixes. It takes a page URL and an email to start.",act:["Start my free review","review"]},
    price:{t:"Pricing is scoped to the page, the platform and how much copy is involved. Send the page through the free review and Riz will include a quote with the fixes.",act:["Start my free review","review"]},
    time:{t:FAQ.time}, platform:{t:FAQ.platform}, agency:{t:FAQ.agency,act:["See agency partnerships","agency"]},
    ab:{t:FAQ.ab}, who:{t:FAQ.who}, where:{t:FAQ.where},
    results:{t:"CaseLeap is a good example. After the first iteration, average homepage time went from 3 to 18 seconds and quick backs fell from 21.4% to 11.8%.",act:["Read the CaseLeap story","case"]}
  };
  var INTENTS=[[/review|free|audit|look at|check my|feedback/i,"review"],[/price|pricing|cost|budget|quote|how much|\$/i,"price"],[/how long|time ?line|turnaround|fast|days|weeks?/i,"time"],[/platform|webflow|wordpress|shopify|unbounce|highlevel|hubspot|clickfunnels|wix|elementor/i,"platform"],[/agenc|white.?label|partner|resell/i,"agency"],[/a\/b|split|test|experiment/i,"ab"],[/time ?zone|based|location|where are/i,"where"],[/who|team|riz|founder/i,"who"],[/result|case|example|proof|work/i,"results"]];
  var QUICK=[["Get a free page review","review"],["How long does a page take?","time"],["Do you work with agencies?","agency"],["Which platforms?","platform"],["Show me results","results"]];
  var scrollLog=function(){ log.scrollTop=log.scrollHeight; };
  var runAct=function(a){
    if(a==="review"){ toggleChat(false); openReview(); }
    else if(a==="case"){ window.location.href="work-caseleap.html"; }
    else if(a==="agency"){ window.location.href="agency-partners.html"; }
  };
  var addMsg=function(who,text,act){
    var m=document.createElement("div"); m.className="msg "+who; m.textContent=text;
    if(act){ var b=document.createElement("button"); b.type="button"; b.className="act"; b.textContent=act[0]; b.addEventListener("click",function(){ runAct(act[1]); }); m.appendChild(document.createElement("br")); m.appendChild(b); }
    log.appendChild(m); scrollLog(); return m;
  };
  var typing=function(){ var ty=document.createElement("div"); ty.className="msg bot typing"; ty.innerHTML="<i></i><i></i><i></i>"; log.appendChild(ty); scrollLog(); return ty; };
  var botSay=function(text,act,delay){
    var ty=typing();
    setTimeout(function(){ ty.remove(); addMsg("bot",text,act); }, reduce?0:(delay||650));
  };
  var answer=function(key){ var a=ANS[key]; botSay(a.t,a.act); };
  var handle=function(text){
    text=text.trim(); if(!text) return;
    addMsg("me",text);
    if(awaitingEmail){
      if(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(text)){
        awaitingEmail=false; var ty=typing();
        sendForm("chat",{email:text,message:chatQ},null).then(function(res){
          ty.remove(); addMsg("bot","Thanks. Riz will reply to "+text+" personally."+(res.preview?" (Preview only: this wasn\u2019t sent.)":""));
        },function(e){
          ty.remove(); awaitingEmail=true;
          addMsg("bot",e.field==="email" ? "That doesn't look like an email address. Try something like you@company.com." : "Couldn\u2019t send that right now. Try again, or email "+FORM_INBOX+".");
        });
      }
      else botSay("That doesn't look like an email address. Try something like you@company.com.");
      return;
    }
    for(var i=0;i<INTENTS.length;i++){ if(INTENTS[i][0].test(text)){ answer(INTENTS[i][1]); return; } }
    awaitingEmail=true; chatQ=text;
    botSay("Good question for Riz directly. Leave your email and he'll get back to you during US business hours.");
  };
  QUICK.forEach(function(q){ var b=document.createElement("button"); b.type="button"; b.textContent=q[0]; b.addEventListener("click",function(){ addMsg("me",q[0]); answer(q[1]); }); quick.appendChild(b); });
  $("chatForm").addEventListener("submit",function(e){ e.preventDefault(); handle(cin.value); cin.value=""; });
  var toggleChat=function(open){
    if(open===undefined) open=panel.hidden;
    panel.hidden=!open; chat.classList.toggle("open",open); fab.setAttribute("aria-expanded",String(open)); teaser.hidden=true;
    if(open){
      if(!chatStarted){ chatStarted=true; botSay("Hi, I'm Riz, founder of PageDriven. Ask me anything about your landing page or website, or pick a question below.",null,400); }
      if(hasG && !reduce) gsap.fromTo(panel,{opacity:0,y:16,scale:.97},{opacity:1,y:0,scale:1,duration:.35,ease:"power3.out"});
      setTimeout(function(){ cin.focus(); },60);
    }
  };
  fab.addEventListener("click",function(){ toggleChat(); });
  $("chatClose").addEventListener("click",function(){ toggleChat(false); fab.focus(); });
  document.addEventListener("keydown",function(e){ if(e.key==="Escape" && !panel.hidden) toggleChat(false); });
  $("ctX").addEventListener("click",function(){ teaser.hidden=true; try{ sessionStorage.setItem("pd-teaser","1"); }catch(e){} });
  $("ctGo").addEventListener("click",function(){ toggleChat(true); });
  setTimeout(function(){ var seen=false; try{ seen=!!sessionStorage.getItem("pd-teaser"); }catch(e){} if(!seen && panel.hidden && !chatStarted){ teaser.hidden=false; try{ sessionStorage.setItem("pd-teaser","1"); }catch(e){} setTimeout(function(){ teaser.hidden=true; },12000); } },9000);
}

/* ---------- Sticky side-nav scrollspy (home services, about principles) ---------- */
each(".svc-nav",function(nav){
  var links=nav.querySelectorAll("a"); if(!links.length || !("IntersectionObserver" in window)) return;
  var ids=Array.prototype.map.call(links,function(a){ return a.getAttribute("href").slice(1); });
  var spy=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ var i=ids.indexOf(e.target.id); Array.prototype.forEach.call(links,function(a,k){ a.classList.toggle("on",k===i); }); } }); },{rootMargin:"-45% 0px -50% 0px"});
  ids.forEach(function(id){ var t=document.getElementById(id); if(t) spy.observe(t); });
});
/* Doc/case table of contents scrollspy */
var tocLinks=document.querySelectorAll(".toc a");
if(tocLinks.length && "IntersectionObserver" in window){
  var tids=Array.prototype.map.call(tocLinks,function(a){ return a.getAttribute("href").slice(1); });
  var tspy=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ var i=tids.indexOf(e.target.id); Array.prototype.forEach.call(tocLinks,function(a,k){ a.classList.toggle("on",k===i); }); } }); },{rootMargin:"-30% 0px -60% 0px"});
  tids.forEach(function(id){ var el=$(id); if(el) tspy.observe(el); });
}

/* ---------- In-page anchors ---------- */
each('a[href^="#"]',function(a){
  a.addEventListener("click",function(e){
    var id=a.getAttribute("href"); if(id.length<2){ e.preventDefault(); scrollToY(0); return; }
    var t=document.querySelector(id); if(!t) return;
    e.preventDefault(); scrollToEl(t,96);
  });
});

/* ---------- About work rows: focused row lights up, sticky centre image cross-fades ---------- */
each(".wgd-body",function(body){
  var rows=body.querySelectorAll(".wgd-row"), pics=body.querySelectorAll(".wgd-stick .wgd-pic");
  if(!rows.length || !("IntersectionObserver" in window)) return;
  function set(i){ Array.prototype.forEach.call(rows,function(r,k){ r.classList.toggle("on",k===i); }); Array.prototype.forEach.call(pics,function(p,k){ p.classList.toggle("on",k===i); }); }
  var io=new IntersectionObserver(function(es){ es.forEach(function(en){ if(en.isIntersecting) set(Array.prototype.indexOf.call(rows,en.target)); }); },{rootMargin:"-48% 0px -48% 0px"});
  Array.prototype.forEach.call(rows,function(r){ io.observe(r); });
});

/* ---------- THREE: line-wave (home hero full, inner heroes soft) ---------- */
function lineWave(canvas){
  var mode=canvas.getAttribute("data-wave"), soft=mode!=="full";
  var renderer=new THREE.WebGLRenderer({canvas:canvas,antialias:true,alpha:true});
  renderer.setPixelRatio(Math.min(2,window.devicePixelRatio||1));
  var scene=new THREE.Scene(), cam=new THREE.PerspectiveCamera(36,1,0.1,100);
  cam.position.set(0,0,12);
  /* one ribbon: widest through the centre, twisting down to thin ends at both edges */
  var LINES=soft?96:130, SEG=soft?160:220, d=[];
  for(var i=0;i<LINES;i++){ var v=i/(LINES-1)*2-1;
    for(var j=0;j<SEG;j++){ d.push(j/SEG,v,0,(j+1)/SEG,v,0); } }
  var g=new THREE.BufferGeometry();
  g.setAttribute("aD",new THREE.Float32BufferAttribute(d,3));
  g.setAttribute("position",new THREE.Float32BufferAttribute(new Float32Array(d.length),3));
  var uni={uTime:{value:0},uMouse:{value:new THREE.Vector2()},uScroll:{value:0},uW:{value:20},uY:{value:-1.6},uA:{value:soft?0.46:0.6}};
  var mat=new THREE.ShaderMaterial({uniforms:uni,transparent:true,depthWrite:false,
    vertexShader:[
      "attribute vec3 aD;uniform float uTime;uniform vec2 uMouse;uniform float uScroll;uniform float uW;uniform float uY;",
      "varying float vX;varying float vV;",
      "void main(){float u=aD.x;float v=aD.y;float t=uTime*0.22;",
      "float x=(u-0.5)*uW;float xn=u*2.0-1.0;",
      "float yc=0.2+0.28*xn+0.24*sin(xn*2.3+t*1.2);",
      "float w=0.1+0.82*exp(-pow(xn*1.4,2.0));",
      "float tw=xn*1.7+sin(t*0.6)*0.3;",
      "vec3 p=vec3(x,yc+v*w*cos(tw),v*w*sin(tw)*0.9);",
      "p.y+=uY+uScroll*1.4;float c=1.0-abs(xn);p.x+=uMouse.x*0.45*c;p.y+=uMouse.y*0.3*c;",
      "vX=xn;vV=v;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);}"
    ].join("\n"),
    fragmentShader:[
      "precision mediump float;uniform float uA;varying float vX;varying float vV;",
      "void main(){vec3 violet=vec3(0.33,0.32,0.96);vec3 orchid=vec3(0.58,0.42,0.93);vec3 pink=vec3(0.88,0.48,0.68);vec3 peach=vec3(0.95,0.6,0.5);",
      "vec3 col=mix(peach,pink,smoothstep(-1.0,-0.55,vX));col=mix(col,orchid,smoothstep(-0.35,0.2,vX));col=mix(col,violet,smoothstep(0.2,0.9,vX));",
      "float a=smoothstep(-1.0,-0.72,vX)*(1.0-smoothstep(0.8,1.0,vX));",
      "float band=0.45+0.55*(1.0-abs(vV));",
      "gl_FragColor=vec4(col,clamp(uA*a*band,0.0,0.95));}"
    ].join("\n")});
  var mesh=new THREE.LineSegments(g,mat); mesh.frustumCulled=false; scene.add(mesh);
  function size(){ var w=canvas.clientWidth,h=canvas.clientHeight; if(!w||!h) return; renderer.setSize(w,h,false); cam.aspect=w/h; cam.updateProjectionMatrix();
    var vh=2*12*Math.tan(18*Math.PI/180), vw=vh*cam.aspect; uni.uW.value=vw*1.12; uni.uY.value=-vh*0.17; }
  size(); window.addEventListener("resize",size);
  var target=new THREE.Vector2(), visible=true;
  window.addEventListener("pointermove",function(e){ if(e.pointerType==="mouse") target.set(e.clientX/window.innerWidth*2-1, -(e.clientY/window.innerHeight*2-1)); },{passive:true});
  if("IntersectionObserver" in window){ new IntersectionObserver(function(es){ visible=es[0].isIntersecting; }).observe(canvas); }
  var t0=performance.now(), hero=canvas.parentNode;
  function frame(now){
    if(visible){
      uni.uTime.value=(now-t0)/1000; uni.uMouse.value.lerp(target,0.04);
      var r=hero.getBoundingClientRect(); uni.uScroll.value=Math.max(0,Math.min(1,-r.top/Math.max(1,r.height)));
      renderer.render(scene,cam);
    }
    if(!reduce) requestAnimationFrame(frame);
  }
  if(reduce){ uni.uTime.value=6; renderer.render(scene,cam); } else requestAnimationFrame(frame);
}
if(hasT){ each("canvas[data-wave]",function(c){ try{ lineWave(c); }catch(e){} }); }

/* ---------- 2D canvas backdrops (dark sections) ---------- */
var FX=["58,159,214","224,122,174","226,160,69","167,156,255","15,159,132"];
function runWhenVisible(cv,draw){
  var vis=false; if("IntersectionObserver" in window) new IntersectionObserver(function(es){vis=es[0].isIntersecting;}).observe(cv); else vis=true;
  function loop(t){ if(vis) draw(t); requestAnimationFrame(loop); }
  if(reduce) draw(4000); else requestAnimationFrame(loop);
}
function sizeCanvas(cv){ var pr=Math.min(2,window.devicePixelRatio||1), w=cv.clientWidth, h=cv.clientHeight; cv.width=w*pr; cv.height=h*pr; var x=cv.getContext("2d"); x.setTransform(pr,0,0,pr,0,0); return {w:w,h:h,ctx:x}; }
function dotField(cv){
  var S, dots=[], gap=30, mouse={x:-999,y:-999};
  function build(){ S=sizeCanvas(cv); dots=[]; for(var y=gap/2;y<S.h;y+=gap) for(var x=gap/2;x<S.w;x+=gap) dots.push({x:x,y:y,a:0}); }
  build(); window.addEventListener("resize",build);
  cv.parentNode.addEventListener("pointermove",function(e){ var r=cv.getBoundingClientRect(); mouse.x=e.clientX-r.left; mouse.y=e.clientY-r.top; });
  cv.parentNode.addEventListener("pointerleave",function(){ mouse.x=mouse.y=-999; });
  runWhenVisible(cv,function(){
    var c=S.ctx; c.clearRect(0,0,S.w,S.h);
    for(var i=0;i<dots.length;i++){ var d=dots[i];
      if(Math.random()<0.0012) d.a=1;
      d.a*=0.982;
      var m=Math.hypot(d.x-mouse.x,d.y-mouse.y), boost=m<140?(1-m/140)*0.8:0, lit=Math.max(d.a,boost);
      /* ambient blink peaks at 10% opacity; the pointer glow keeps its full strength */
      c.fillStyle="rgba(255,255,255,"+Math.max(0.08+d.a*0.02,0.08+boost*0.72).toFixed(3)+")";
      c.beginPath(); c.arc(d.x,d.y,1.1+lit*1.1,0,6.283); c.fill();
    }
  });
}
function orbits(cv){
  var S; function build(){ S=sizeCanvas(cv); } build(); window.addEventListener("resize",build);
  var rings=[0.22,0.32,0.43,0.55,0.68].map(function(r,i){ return {r:r,tilt:0.34+i*0.015,sp:(0.00006+i*0.00002)*(i%2?-1:1),ph:Math.random()*6.28,c:FX[i%FX.length]}; });
  runWhenVisible(cv,function(t){
    var c=S.ctx, cx=S.w/2, cy=S.h*0.72, base=Math.min(S.w,S.h*1.8); c.clearRect(0,0,S.w,S.h);
    rings.forEach(function(g){
      var rx=base*g.r, ry=rx*g.tilt;
      c.strokeStyle="rgba(255,255,255,.045)"; c.lineWidth=1; c.beginPath(); c.ellipse(cx,cy,rx,ry,0,0,6.283); c.stroke();
      for(var k=0;k<2;k++){
        var a=g.ph+k*3.14+t*g.sp, x=cx+Math.cos(a)*rx, y=cy+Math.sin(a)*ry;
        for(var tr=0;tr<14;tr++){ var aa=a-tr*0.012*Math.sign(g.sp); c.fillStyle="rgba("+g.c+","+(0.45*(1-tr/14)).toFixed(3)+")"; c.beginPath(); c.arc(cx+Math.cos(aa)*rx,cy+Math.sin(aa)*ry,1.8*(1-tr/18),0,6.283); c.fill(); }
        var gr=c.createRadialGradient(x,y,0,x,y,14); gr.addColorStop(0,"rgba("+g.c+",.5)"); gr.addColorStop(1,"rgba("+g.c+",0)"); c.fillStyle=gr; c.beginPath(); c.arc(x,y,14,0,6.283); c.fill();
      }
    });
  });
}
each('canvas[data-fx="dots"]',function(c){ try{ dotField(c); }catch(e){} });
each('canvas[data-fx="orbit"]',function(c){ try{ orbits(c); }catch(e){} });

/* ---------- GSAP motion ---------- */
if(hasG && !reduce){
  gsap.registerPlugin(ScrollTrigger);
  if(typeof window.Lenis!=="undefined"){
    try{
      lenis=new Lenis({lerp:0.1,smoothWheel:true});
      lenis.on("scroll",ScrollTrigger.update);
      gsap.ticker.add(function(t){ lenis.raf(t*1000); });
      gsap.ticker.lagSmoothing(0);
    }catch(e){ lenis=null; }
  }
  if(document.querySelector(".g-in")) gsap.from(".g-in",{y:28,opacity:0,duration:1,ease:"power3.out",stagger:.08,delay:.1});
  each("canvas[data-wave]",function(c){ gsap.from(c,{opacity:0,duration:2,ease:"power2.out",delay:.3}); });

  gsap.utils.toArray(".reveal").forEach(function(el){
    gsap.from(el,{y:36,opacity:.25,duration:1,ease:"power3.out",scrollTrigger:{trigger:el,start:"top 90%",once:true}});
  });
  gsap.utils.toArray(".sec-head").forEach(function(el){
    if(el.closest(".phero")) return;
    gsap.from(el.children,{y:22,opacity:.2,duration:.9,stagger:.07,ease:"power3.out",scrollTrigger:{trigger:el,start:"top 86%",once:true}});
  });
  gsap.utils.toArray(".stagger").forEach(function(el){
    gsap.from(el.children,{y:24,opacity:.2,duration:.8,stagger:.07,ease:"power3.out",scrollTrigger:{trigger:el,start:"top 88%",once:true}});
  });
  gsap.utils.toArray("[data-count]").forEach(function(el){
    var to=+el.getAttribute("data-count"), pre=el.getAttribute("data-prefix")||"", suf=el.getAttribute("data-suffix")||"", o={v:0};
    ScrollTrigger.create({trigger:el,start:"top 90%",once:true,onEnter:function(){ gsap.to(o,{v:to,duration:1.6,ease:"power2.out",onUpdate:function(){ el.textContent=pre+Math.round(o.v)+suf; }}); }});
  });
  gsap.utils.toArray(".bar .fl").forEach(function(el){ gsap.from(el,{scaleX:0,duration:1.4,ease:"power3.out",scrollTrigger:{trigger:el,start:"top 92%",once:true}}); });
  each(".spark .draw",function(dp){ if(!dp.getTotalLength) return; var L=dp.getTotalLength(); dp.style.strokeDasharray=L; gsap.fromTo(dp,{strokeDashoffset:L},{strokeDashoffset:0,duration:1.6,ease:"power2.out",scrollTrigger:{trigger:dp,start:"top 92%",once:true}}); });
  each(".compare[data-sweep]",function(cmp){
    var rng=cmp.querySelector(".cmp-range");
    ScrollTrigger.create({trigger:cmp,start:"top 70%",once:true,onEnter:function(){
      var o={v:50}; gsap.timeline({onUpdate:function(){ cmp.style.setProperty("--split",o.v+"%"); rng.value=o.v; }}).to(o,{v:22,duration:.9,ease:"power2.inOut"}).to(o,{v:72,duration:1.1,ease:"power2.inOut"}).to(o,{v:50,duration:.8,ease:"power2.inOut"});
    }});
  });
  gsap.utils.toArray(".viz [data-speed], .pvis [data-speed]").forEach(function(el){
    var sp=+el.getAttribute("data-speed"), box=el.closest(".viz,.pvis");
    gsap.fromTo(el,{yPercent:sp*2.2},{yPercent:-sp*2.2,ease:"none",scrollTrigger:{trigger:box,start:"top bottom",end:"bottom top",scrub:true}});
  });
  gsap.utils.toArray(".svc-title img, .icon-item img, .tilt3d").forEach(function(el){
    gsap.fromTo(el,{y:8,rotate:-4},{y:-8,rotate:4,ease:"none",scrollTrigger:{trigger:el,start:"top bottom",end:"bottom top",scrub:true}});
  });
  /* "Choose your path" icons float without rocking so they stay upright */
  gsap.utils.toArray(".path img").forEach(function(el){
    gsap.fromTo(el,{y:8},{y:-8,ease:"none",scrollTrigger:{trigger:el,start:"top bottom",end:"bottom top",scrub:true}});
  });
  gsap.utils.toArray(".steps-v").forEach(function(el){
    var line=el.querySelector(".steps-line i"); if(line) gsap.fromTo(line,{scaleY:0},{scaleY:1,ease:"none",scrollTrigger:{trigger:el,start:"top 75%",end:"bottom 60%",scrub:true}});
  });
  gsap.utils.toArray(".flow").forEach(function(el){
    gsap.from(el.querySelectorAll("li"),{x:-16,opacity:.15,duration:.6,stagger:.12,ease:"power2.out",scrollTrigger:{trigger:el,start:"top 85%",once:true}});
  });
  gsap.utils.toArray(".story-portrait img").forEach(function(el){
    gsap.fromTo(el,{y:22},{y:-22,ease:"none",scrollTrigger:{trigger:el.parentNode,start:"top bottom",end:"bottom top",scrub:true}});
  });
  if($("riz")) gsap.from("#riz",{y:50,ease:"none",scrollTrigger:{trigger:".cta",start:"top bottom",end:"bottom 85%",scrub:true}});
  /* founder story: the arrow from Riz's shoulder to his name draws in once */
  gsap.utils.toArray(".sf-arrow").forEach(function(svg){
    var ps=svg.querySelectorAll("path"); if(ps.length<2) return;
    Array.prototype.forEach.call(ps,function(p){ var l=p.getTotalLength(); p.style.strokeDasharray=l; p.style.strokeDashoffset=l; });
    gsap.timeline({scrollTrigger:{trigger:svg,start:"top 80%",once:true}}).to(ps[0],{strokeDashoffset:0,duration:.9,ease:"power2.inOut"}).to(ps[1],{strokeDashoffset:0,duration:.3,ease:"power2.out"});
  });
  var ap=$("arrowPath"), ah=$("arrowHead");
  if(ap && ah){
    [ap,ah].forEach(function(p){ var l=p.getTotalLength(); p.style.strokeDasharray=l; p.style.strokeDashoffset=l; });
    gsap.timeline({scrollTrigger:{trigger:".cta",start:"top 75%",once:true}}).to(ap,{strokeDashoffset:0,duration:.9,ease:"power2.inOut"}).to(ah,{strokeDashoffset:0,duration:.3,ease:"power2.out"});
  }
  litEls.forEach(function(el){
    var words=el.querySelectorAll(".w"), N=words.length, sec=el.closest("section"), SOFT=8, wl=Array.prototype.slice.call(words);
    /* highlighted phrases sweep in once their last word is lit */
    var marks=Array.prototype.map.call(el.querySelectorAll("mark"),function(mk){ var ws=mk.querySelectorAll(".w"); return [mk, wl.indexOf(ws[ws.length-1])]; });
    var paint=function(p){ var head=p*(N+SOFT); for(var i=0;i<N;i++){ var o=Math.max(0,Math.min(1,(head-i)/SOFT)); words[i].style.opacity=(0.17+0.83*o).toFixed(3); }
      marks.forEach(function(mk){ mk[0].classList.toggle("on", head-mk[1] >= SOFT*.9); });
      if(sec) sec.classList.toggle("lit-done", p>0.8); };
    if(sec) sec.classList.add("lit-arm");
    paint(0);
    if(el.getAttribute("data-words")==="flow"){ ScrollTrigger.create({trigger:el,start:"top 82%",end:"bottom 68%",scrub:true,onUpdate:function(st){ paint(st.progress); }}); return; }
    var lm=gsap.matchMedia();
    lm.add("(min-width: 900px)",function(){ ScrollTrigger.create({trigger:sec,start:"top top",end:"+=130%",pin:true,scrub:true,onUpdate:function(st){ paint(st.progress); }}); });
    lm.add("(max-width: 899px)",function(){ ScrollTrigger.create({trigger:el,start:"top 80%",end:"bottom 40%",scrub:true,onUpdate:function(st){ paint(st.progress); }}); });
  });
  if($("arcWrap")){
    var mm=gsap.matchMedia();
    mm.add("(min-width: 900px)",function(){
      arcPinned=true;
      procST=ScrollTrigger.create({trigger:"#process",start:"top top",end:"+=1800",pin:true,scrub:.5,onUpdate:function(self){ setArc(self.progress); }});
      return function(){ arcPinned=false; procST=null; };
    });
  }
  window.addEventListener("load",function(){ ScrollTrigger.refresh(); });
}
})();
