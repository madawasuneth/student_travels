
(function(){
  const { $, $$, offerCard, renderHeaderAuth } = window.UI;
  document.addEventListener('DOMContentLoaded', ()=>{
    renderHeaderAuth();
    const me = window.ST.ensureLoggedIn("student_dashboard.html");
    if(!me) return;
    if(me.role!=='student'){ window.location.href = 'index.html'; return; }
    const s = window.ST.getState();
    const favs = s.offers.filter(o=>(me.favourites||[]).includes(o.id));
    const books = s.bookings.filter(b=>b.studentId===me.id);
    $('#stats').textContent = `Saved: ${favs.length} • Bookings: ${books.length} • Approved: ${books.filter(b=>b.status==='booked').length} • Pending: ${books.filter(b=>b.status==='pending').length}`;
    $('#favourites').innerHTML = favs.map(offerCard).join('') || '<p class="small">No favourites yet.</p>';
    $('#bookings').innerHTML = books.map(b=>{const o=s.offers.find(x=>x.id===b.offerId);return `<tr><td><a href="offer_details.html?id=${o.id}">${o.title}</a></td><td>${new Date(b.createdAt).toLocaleString()}</td><td><span class="status ${b.status}">${b.status}</span></td></tr>`}).join('');
    $('#messages').innerHTML = renderThreads(me.id);
    window.UI.attachListBookHandlers();
    $('#year').textContent = new Date().getFullYear();
  });
  function renderThreads(uid){
    const s = window.ST.getState(); const ts = s.messages.filter(t=>t.participants.includes(uid));
    if(!ts.length) return `<p class="small">No messages.</p>`;
    return ts.map(t=>`<div class="panel" style="margin:.5rem 0"><div class="small">Thread ${t.threadId}</div>${t.messages.map(m=>`<p><b>${(s.users.find(u=>u.id===m.from)?.displayName)||(s.users.find(u=>u.id===m.from)?.firstName)||'User'}</b>: ${m.text}</p>`).join('')}</div>`).join('');
  }
})();
