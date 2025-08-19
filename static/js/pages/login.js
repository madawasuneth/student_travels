
(function(){
  const { $, renderHeaderAuth } = window.UI;
  document.addEventListener('DOMContentLoaded', ()=>{
    renderHeaderAuth();
    const err = $('#loginErrors');
    $('#loginForm').onsubmit = (e)=>{
      e.preventDefault();
      const email = $('#loginEmail').value.trim().toLowerCase();
      const pass  = $('#loginPass').value;
      if(!email || !pass){ err.textContent='Please enter your email and password.'; return; }
      const s=window.ST.getState();
      const u=s.users.find(x=>(x.email||'').toLowerCase()===email && x.password===pass);
      if(!u){ err.textContent='Invalid email or password.'; return; }
      window.ST.setAuth(u.id);
      const redirect = new URL(window.location.href).searchParams.get('redirect');
      if(redirect){ window.location.href = redirect; return; }
      const dest = u.role==='student'?'student_dashboard.html': u.role==='advertiser'?'advertiser_dashboard.html': u.role==='moderator'?'moderator_dashboard.html':'admin_dashboard.html';
      window.location.href = dest;
    };
    $('#year').textContent = new Date().getFullYear();
  });
})();
