
(function(){
  const { $, renderHeaderAuth } = window.UI;
  document.addEventListener('DOMContentLoaded', ()=>{
    renderHeaderAuth();
    const me = window.ST.ensureLoggedIn("ad_create.html");
    if(!me) return;
    if(me.role!=='advertiser'){ window.location.href = 'index.html'; return; }
    $('#coType').onchange = ()=>{ document.getElementById('coPackFields').style.display = $('#coType').value==='pack'?'flex':'none'; };
    $('#createOfferForm').onsubmit = (e)=>{
      e.preventDefault();
      const s=window.ST.getState();
      const o={
        id:'offer_'+(s.offers.length+1).toString().padStart(3,'0'),
        agentId:me.id,
        status:'draft',
        type:$('#coType').value,
        title:$('#coTitle').value.trim(),
        origin:$('#coOrigin').value,
        destination:$('#coDest').value.trim(),
        image:($('#coImg').value||'images/gold-coast-sunny.jpg'),
        regularPrice:Number($('#coReg').value),
        discountPct:Number($('#coDisc').value),
        discountPrice: Math.round(Number($('#coReg').value)*(1-Number($('#coDisc').value)/100)),
        description: $('#coDesc').value.trim() || 'Student-friendly offer.',
        flightDuration: $('#coDur').value.trim(),
        baggage: $('#coBag').value.trim(),
        stayDuration: $('#coStay').value.trim() || undefined,
        accommodation: $('#coAcc').value.trim() || undefined,
        expiry: $('#coExp').value,
        createdAt: new Date().toISOString(),
        views: 0, favourites: 0
      };
      s.offers.push(o); window.ST.saveState(s);
      alert('Offer created as Draft and sent to Moderator queue.');
      window.location.href = 'advertiser_dashboard.html';
    };
    $('#year').textContent = new Date().getFullYear();
  });
})();
