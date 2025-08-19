
(function(){
  const { $, renderHeaderAuth } = window.UI;
  document.addEventListener('DOMContentLoaded', ()=>{
    renderHeaderAuth();
    const err = $('#regErrors');
    $('#studentRegisterForm').onsubmit = (e)=>{
      e.preventDefault();
      const first=$('#regFirst').value.trim(), last=$('#regLast').value.trim();
      const email=$('#regEmail').value.trim().toLowerCase(), mobile=$('#regMobile').value.trim();
      const uni=$('#regUni').value, street=$('#regStreet').value.trim(), suburb=$('#regSuburb').value.trim();
      const state=$('#regState').value, post=$('#regPostcode').value.trim();
      const pass=$('#regPass').value, pass2=$('#regPass2').value;
      if(!first||!last||!email||!mobile||!uni||!street||!suburb||!state||!post||!pass||!pass2){ err.textContent='Please fill in all required fields.'; return; }
      if(!/^\d{4}$/.test(post)){ err.textContent='Postcode must be 4 digits.'; return; }
      const pwPolicy=/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;
      if(!pwPolicy.test(pass)){ err.textContent='Password must include upper, lower, number, and symbol (min 8 chars).'; return; }
      if(pass!==pass2){ err.textContent='Passwords do not match.'; return; }
      const s=window.ST.getState();
      if(s.users.some(u=>(u.email||'').toLowerCase()===email)){ err.textContent='An account with this email already exists.'; return; }
      const id='stu_'+Math.random().toString(36).slice(2,7);
      s.users.push({ id, role:'student', email, password: pass, firstName:first, lastName:last, mobile,
        university: uni, address:{street, suburb, state, postcode: post}, favourites:[], joinMonth: new Date().toISOString().slice(0,7), logins:{} });
      window.ST.saveState(s); window.ST.setAuth(id);
      window.location.href = "student_dashboard.html";
    };
    $('#year').textContent = new Date().getFullYear();
  });
})();
