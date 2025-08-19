
(function(){
  const { $, $$, renderHeaderAuth } = window.UI;
  document.addEventListener('DOMContentLoaded', ()=>{
    renderHeaderAuth();
    const me = window.ST.ensureLoggedIn("moderator_dashboard.html");
    if(!me) return;
    if(me.role!=='moderator'){ window.location.href = 'index.html'; return; }
    const s=window.ST.getState();
    const queue=s.offers.filter(o=>o.status==='draft');
    $('#queueBody').innerHTML = queue.map(o=>`<tr><td>${o.title}</td><td>${o.type==='pack'?'Pack':'Flight'}</td><td>$${o.discountPrice}</td><td><button class="btn" data-approve-offer="${o.id}">Approve</button> <button class="btn" data-reject-offer="${o.id}">Reject</button></td></tr>`).join('');
    $$('[data-approve-offer]').forEach(b=>b.onclick=()=>{ const id=b.getAttribute('data-approve-offer'); const s=window.ST.getState(); const o=s.offers.find(x=>x.id===id); if(o){ o.status='published'; window.ST.saveState(s); alert('Offer approved.'); location.reload(); } });
    $$('[data-reject-offer]').forEach(b=>b.onclick=()=>{ const id=b.getAttribute('data-reject-offer'); const s=window.ST.getState(); const o=s.offers.find(x=>x.id===id); const reason=$('#modReason')?.value.trim(); if(!reason){ alert('Enter a rejection reason.'); return; } if(o){ o.status='rejected'; o.moderatorReason=reason; window.ST.saveState(s); alert('Offer rejected.'); location.reload(); } });
    $('#year').textContent = new Date().getFullYear();
  });
})();
