
window.UI = (function(){
  const $ = (s, r=document)=>r.querySelector(s);
  const $$ = (s, r=document)=>Array.from(r.querySelectorAll(s));
  function money(v){ return "$"+Number(v).toFixed(0); }
  function badge(t){ return `<span class="badge ${t==='pack'?'pack':'flight'}">${t==='pack'?'Flights + Stay':'Flight'}</span>`; }
  function offerCard(o){
    return `<article class="card">
      <img src="${o.image}" alt="${o.destination}">
      <div class="card-body">
        <div class="row"><span>${badge(o.type)}</span><span class="small">Expires: ${o.expiry}</span></div>
        <h3 style="margin:.2rem 0">${o.title}</h3>
        <div class="small">${o.origin} → ${o.destination}</div>
        <div class="price-row"><div class="price-new">${money(o.discountPrice)}</div><div class="price-old">${money(o.regularPrice)}</div></div>
      </div>
      <div class="card-footer">
        <span class="small">${o.flightDuration} • ${o.baggage}</span>
        <div class="actions"><button class="btn btn-primary" data-book="${o.id}">Book</button><a class="btn" href="offer_details.html?id=${o.id}">View</a></div>
      </div>
    </article>`;
  }
  function getParam(name){
    const u = new URL(window.location.href);
    return u.searchParams.get(name);
  }
  function renderHeaderAuth(){
    const row = $('.auth-actions');
    if(!row) return;
  // If server-side rendered auth UI exists, do not overwrite it.
  if (row.dataset && row.dataset.serverAuth === 'true') return;
    const me = window.ST.getAuth();
    if(me){
  const dest = me.role==='student'?'/dashboard/student/': me.role==='advertiser'?'/dashboard/advertiser/': me.role==='moderator'?'/dashboard/moderator/':'/dashboard/admin/';
  row.innerHTML = `<a class="btn" href="${dest}">${me.role.charAt(0).toUpperCase()+me.role.slice(1)} Dashboard</a> <button id="btnLogout" class="btn btn-primary">Log out</button>`;
  const out = $('#btnLogout'); if(out){ out.onclick=()=>{ window.ST.logout(); window.location.href="/"; }; }
    } else {
      // Include IDs so modal handlers in `base.html` can find these buttons
      row.innerHTML = `<a id="btnLogin" class="btn" href="/login/">Log in</a> <a id="btnRegister" class="btn btn-primary" href="/register/">Register</a>`;
    }
    const menuBtn=$('#btnMenu'); if(menuBtn){ menuBtn.onclick=()=>{ const d=$('#menu-drawer'); const open=d.classList.toggle('open'); d.setAttribute('aria-hidden', String(!open)); }; }
  }
  function attachListBookHandlers(){
    $$('[data-book]').forEach(b=>b.onclick=()=>{
      const me = window.ST.ensureLoggedIn(window.location.pathname + window.location.search);
      if(!me || me.role!=='student') return;
      const offerId=b.getAttribute('data-book');
      const s=window.ST.getState();
      s.bookings.push({id:'book_'+Math.random().toString(36).slice(2,7), studentId:me.id, offerId:offerId, status:'pending', createdAt:new Date().toISOString()});
      window.ST.saveState(s);
      alert('Booking submitted as Pending.');
    });
  }
  return { $, $$, money, badge, offerCard, getParam, renderHeaderAuth, attachListBookHandlers };
})();
