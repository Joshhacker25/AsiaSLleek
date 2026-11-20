const API = (window.location.port === '8000' ? '' : 'http://localhost:8000');
const token = () => localStorage.getItem('asiaslleek_token');
async function api(path, opts = {}) {
  const headers = {'Content-Type': 'application/json'};
  if (token()) headers.Authorization = 'Bearer ' + token();
  const res = await fetch(API + path, {...opts, headers});
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function fmtDur(s){s=+s||0;return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')}
function thumb(v){return '<div class="thumb" role="img" aria-label="Neutral placeholder artwork">'+esc(v.title)+'</div>'}
function videoCard(v){return '<article class="card">'+thumb(v)+'<div class="body"><h3><a href="video.html?id='+v.id+'">'+esc(v.title)+'</a></h3><p class="small muted">'+esc(v.creator_name||'')+' &middot; '+fmtDur(v.duration_seconds)+' &middot; '+(v.views||0).toLocaleString()+' views</p><p class="small">'+esc((v.description||'').slice(0,90))+'</p></div></article>'}
function renderHeader(){
  const h=document.querySelector('header.site');
  if(!h) return;
  h.innerHTML='<div class="nav"><a class="logo" href="index.html">Asia<span>S</span>Lleek</a><nav aria-label="Main"><a href="index.html">Home</a><a href="search.html">Search</a><a href="library.html">Library</a><a href="creator-dashboard.html">Creator</a><a href="help.html">Help</a><a href="admin/index.html">Admin</a></nav><form class="searchbox" action="search.html" role="search"><label class="small" for="q" style="position:absolute;left:-9999px">Search</label><input id="q" name="q" type="search" placeholder="Search fictional videos…"><button type="submit">Search</button></form><span id="authlinks"><a href="login.html">Sign in</a> | <a href="register.html">Register</a></span></div>';
  const me=token(); if(me){const a=document.getElementById('authlinks'); if(a) a.innerHTML='<a href="account.html">Account</a> | <a href="#" id="logout">Sign out</a>'; const l=document.getElementById('logout'); if(l) l.onclick=e=>{e.preventDefault();localStorage.removeItem('asiaslleek_token');location.href='index.html'};}
}
function renderFooter(){
  const f=document.querySelector('footer.site');
  if(!f) return;
  f.innerHTML='<p>AsiaSLleek — fictional catalogue. All videos are fictional placeholders; no real or explicit media.</p><p><a href="help.html">Help &amp; content rules</a> &middot; <a href="help.html#report">Report content</a> &middot; <a href="help.html#removal">Request removal</a> &middot; <a href="account.html">Privacy &amp; preferences</a></p><p class="small">Adults only. Age assurance is NOT CONFIGURED — see README. An \'I am over 18\' click is not legal age verification.</p>';
}
function ageGate(){
  if(sessionStorage.getItem('asiaslleek_age_ok')) return;
  const d=document.createElement('div'); d.className='agegate'; d.setAttribute('role','dialog'); d.setAttribute('aria-label','Adults only notice');
  d.innerHTML='<div class="box"><h1>Adults only — 18+</h1><p>AsiaSLleek is an adults-only catalogue. Age assurance is <strong>not configured</strong> in this local build; a real deployment must connect an age-assurance provider before any real use. Clicking below does <strong>not</strong> verify your age.</p><p><button id="ageok" class="btn">I understand — continue to the demo</button></p><p class="small muted"><a href="help.html">Content rules &amp; help</a></p></div>';
  document.body.appendChild(d);
  document.getElementById('ageok').onclick=()=>{sessionStorage.setItem('asiaslleek_age_ok','1'); d.remove();};
}
const FIXTURES=[{id:1,title:'Sunrise Over the Harbour',description:'A fictional sunrise timelapse story.',creator_name:'Mira Chen',duration_seconds:742,views:12840,category_slug:'documentary',tags:'fictional, sample'},{id:2,title:'Neon Streets After Rain',description:'A fictional city-night photo essay.',creator_name:'Mira Chen',duration_seconds:615,views:9320,category_slug:'documentary',tags:'fictional, sample'},{id:3,title:'Acoustic Sessions: Room 12',description:'A fictional acoustic performance.',creator_name:'Theo Alvarez',duration_seconds:428,views:15410,category_slug:'music',tags:'fictional, sample'},{id:4,title:'The Market at Dawn',description:'A fictional market-day story.',creator_name:'Priya Nair',duration_seconds:503,views:6210,category_slug:'lifestyle',tags:'fictional, sample'},{id:5,title:'How Tides Work',description:'A fictional explainer about tides.',creator_name:'Theo Alvarez',duration_seconds:689,views:11020,category_slug:'education',tags:'fictional, sample'},{id:6,title:'Late Night Sketch Show',description:'A fictional comedy sketch.',creator_name:'Priya Nair',duration_seconds:372,views:8740,category_slug:'comedy',tags:'fictional, sample'}];
async function loadVideos(params={}){
  try{const q=new URLSearchParams(params); const r=await api('/api/videos?'+q); return r.items||r;}
  catch(e){return FIXTURES.filter(v=>!params.category||v.category_slug===params.category);}
}
document.addEventListener('DOMContentLoaded',()=>{renderHeader();renderFooter();ageGate();});
