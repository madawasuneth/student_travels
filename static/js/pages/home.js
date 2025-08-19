
(function(){
  const { $, $$, offerCard, renderHeaderAuth, attachListBookHandlers } = window.UI;
  document.addEventListener('DOMContentLoaded', ()=>{
    renderHeaderAuth();
    const s = window.ST.getState();
    const featured = s.offers.filter(o=>o.status==='published').sort((a,b)=>new Date(b.createdAt)-new Date(a.createdAt)).slice(0,4);
    const dests = Array.from(new Set(s.offers.filter(o=>o.status==='published').map(o=>o.destination))).sort();
    const destSel = $('#sDest'); if(destSel){ destSel.innerHTML = `<option value="">Any</option>` + dests.map(d=>`<option>${d}</option>`).join(''); }
    const featuredEl = $('#featured');
    if(featuredEl){
      // If server already rendered featured cards, do not overwrite them.
      const hasServerContent = featuredEl.children && featuredEl.children.length > 0;
      if(!hasServerContent){
        featuredEl.innerHTML = featured.map(offerCard).join('');
        attachListBookHandlers();
      }
    }

    const btnSearch = $('#btnSearch');
    if(btnSearch){
      btnSearch.onclick = ()=>{
        const type = $('#segPacks').checked ? 'pack':'flight';
        const origin = $('#sOrigin').value;
        const dest = $('#sDest').value;
        const max = Number($('#sMax').value||0);
        let list = s.offers.filter(o=>o.status==='published' && o.type===type);
        if(origin) list=list.filter(o=>o.origin===origin);
        if(dest) list=list.filter(o=>o.destination===dest);
        if(max) list=list.filter(o=>o.discountPrice<=max);
        featuredEl.innerHTML = list.map(offerCard).join('') || '<p>No matches.</p>';
        attachListBookHandlers();
      };
    }
    $('#year').textContent = new Date().getFullYear();
  });
})();
