
(function(){
  const { $, $$, renderHeaderAuth } = window.UI;
  document.addEventListener('DOMContentLoaded', ()=>{
    renderHeaderAuth();
    const me = window.ST.ensureLoggedIn("advertiser_dashboard.html");
    if(!me) return;
    if(me.role!=='advertiser'){ window.location.href = 'index.html'; return; }
    const s = window.ST.getState();
    const mine=s.offers.filter(o=>o.agentId===me.id);
    const published=mine.filter(o=>o.status==='published'), drafts=mine.filter(o=>o.status==='draft'), rejected=mine.filter(o=>o.status==='rejected');
    $('#publishedBody').innerHTML = published.map(o=>`<tr><td>${o.title}</td><td>${o.type==='pack'?'Pack':'Flight'}</td><td>$${o.discountPrice}</td><td>${o.views}</td></tr>`).join('');
    $('#draftsBody').innerHTML = drafts.map(o=>`<tr><td>${o.title}</td><td>${o.type==='pack'?'Pack':'Flight'}</td><td>$${o.discountPrice}</td></tr>`).join('');
    $('#rejectedBody').innerHTML = rejected.map(o=>`<tr><td>${o.title}</td><td>${o.moderatorReason||'-'}</td></tr>`).join('');
    const myBooks=s.bookings.filter(b=>mine.some(o=>o.id===b.offerId));
    $('#bookingsBody').innerHTML = myBooks.map(b=>{const o=s.offers.find(x=>x.id===b.offerId);const st=s.users.find(u=>u.id===b.studentId);return `<tr><td>${st.firstName} ${st.lastName}</td><td>${o.title}</td><td>${new Date(b.createdAt).toLocaleString()}</td><td><span class="status ${b.status}">${b.status}</span></td><td>${b.status==='pending'?`<button class="btn" data-approve="${b.id}">Approve</button>`:''}</td></tr>`}).join('');
    $$('[data-approve]').forEach(b=>b.onclick=()=>{ const id=b.getAttribute('data-approve'); const s=window.ST.getState(); const bk=s.bookings.find(x=>x.id===id); if(bk){ bk.status='booked'; window.ST.saveState(s); location.reload(); } });
    $('#year').textContent = new Date().getFullYear();
  });
})();
