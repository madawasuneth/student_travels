
(function(){
  const { $, $$, money, badge, getParam, renderHeaderAuth } = window.UI;
  document.addEventListener('DOMContentLoaded', ()=>{
    renderHeaderAuth();
    const id = getParam('id');
    const s = window.ST.getState();
    const o = s.offers.find(x=>x.id===id);
    const root = $('#offerRoot');
    if(!o){ root.innerHTML = `<section class="section container"><p>Offer not found.</p></section>`; return; }
    const me = window.ST.getAuth();
    const canFav = me && me.role==='student';
    const faved = canFav && (me.favourites||[]).includes(id);
    root.innerHTML = `<section class="section container">
      <div class="card" style="overflow:hidden">
        <img src="${o.image}" alt="${o.destination}" style="height:260px;object-fit:cover">
        <div class="card-body">
          <div class="row"><span>${badge(o.type)}</span><span class="status ${o.status}">${o.status}</span></div>
          <h2>${o.title}</h2><p class="small">${o.origin} → ${o.destination}</p>
          <div class="price-row"><div class="price-new">${money(o.discountPrice)}</div><div class="price-old">${money(o.regularPrice)}</div><span class="small">Save ${o.discountPct}%</span></div>
          <p class="mt-1">${o.description}</p>
          <div class="row mt-2">
            ${canFav?`<button id="btnFav" class="btn">${faved?'★ In favourites':'☆ Save to favourites'}</button>`:''}
            <button id="btnBookSingle" class="btn btn-primary">Book</button>
            <button id="btnDM" class="btn">Message advertiser</button>
          </div>
        </div>
      </div>
      <div class="panel mt-2"><h3>Public comments</h3>
        <div id="comments">${s.comments.filter(c=>c.offerId===id).map(c=>`<p><b>${(s.users.find(u=>u.id===c.authorId)?.firstName)||(s.users.find(u=>u.id===c.authorId)?.displayName)||'User'}</b>: ${c.text}</p>`).join('')||'<p class="small">No comments yet.</p>'}</div>
        <div class="form-control mt-1"><label for="cText">Add a comment</label><textarea id="cText"></textarea></div>
        <button id="btnAddComment" class="btn mt-1">Post comment</button>
      </div>
    </section>`;

    const fav=$('#btnFav'); if(fav){ fav.onclick=()=>{ const me=window.ST.ensureLoggedIn(window.location.href); if(!me) return; const s=window.ST.getState(); const u=s.users.find(x=>x.id===me.id); u.favourites=u.favourites||[]; if(u.favourites.includes(id)) u.favourites=u.favourites.filter(x=>x!==id); else u.favourites.push(id); window.ST.saveState(s); location.reload(); }; }
    const book=$('#btnBookSingle'); if(book){ book.onclick=()=>{ const me=window.ST.ensureLoggedIn(window.location.href); if(!me || me.role!=='student') return; const s=window.ST.getState(); s.bookings.push({id:'book_'+Math.random().toString(36).slice(2,7), studentId:me.id, offerId:id, status:'pending', createdAt:new Date().toISOString()}); window.ST.saveState(s); alert('Booking submitted as Pending.'); }; }
    const dm=$('#btnDM'); if(dm){ dm.onclick=()=>{ const me=window.ST.ensureLoggedIn(window.location.href); if(!me) return; let thread=s.messages.find(t=>t.participants.includes(me.id)&&t.participants.includes(o.agentId)); if(!thread){ thread={threadId:'t'+Math.random().toString(36).slice(2,7),participants:[me.id,o.agentId],messages:[]}; s.messages.push(thread); } const m=prompt('Write your message:'); if(m){ thread.messages.push({from:me.id,text:m,ts:new Date().toISOString()}); window.ST.saveState(s); alert('Message sent.'); } }; }
    $('#year').textContent = new Date().getFullYear();
  });
})();
