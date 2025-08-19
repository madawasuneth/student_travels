
(function(){
  const { $, $$, offerCard, renderHeaderAuth, attachListBookHandlers } = window.UI;
  document.addEventListener('DOMContentLoaded', ()=>{
    renderHeaderAuth();
    const s = window.ST.getState();
    const list = s.offers.filter(o=>o.status==='published');
    $('#offersGrid').innerHTML = list.map(offerCard).join('') || '<p class="small">No published offers yet.</p>';
    attachListBookHandlers();
    $('#year').textContent = new Date().getFullYear();
  });
})();
