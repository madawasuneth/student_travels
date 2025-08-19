
(function(){
  const { $, renderHeaderAuth } = window.UI;
  document.addEventListener('DOMContentLoaded', ()=>{
    renderHeaderAuth();
    const me = window.ST.ensureLoggedIn("admin_dashboard.html");
    if(!me) return;
    if(me.role!=='admin'){ window.location.href = 'index.html'; return; }
    const s=window.ST.getState();
    const totalUsers=s.users.length,totalOffers=s.offers.length,totalBookings=s.bookings.length,totalViews=s.offers.reduce((a,b)=>a+(b.views||0),0);
    $('#stats').textContent = `Users: ${totalUsers} • Adverts: ${totalOffers} • Bookings: ${totalBookings} • Views: ${totalViews}`;
    $('#year').textContent = new Date().getFullYear();
  });
})();
