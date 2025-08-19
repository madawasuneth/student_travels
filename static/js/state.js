
window.ST = (function(){
  const STATE_KEY = "st_data_mpa_v3_5_1";
  const AUTH_KEY  = "st_auth_mpa_v3_5_1";
  const SEED = window.EMBED_SEED || {};

  function getState(){
    const raw = localStorage.getItem(STATE_KEY);
    if (raw) { try { return JSON.parse(raw); } catch(e){} }
    localStorage.setItem(STATE_KEY, JSON.stringify(SEED));
    return JSON.parse(localStorage.getItem(STATE_KEY));
  }
  function saveState(s){ localStorage.setItem(STATE_KEY, JSON.stringify(s)); }
  function setAuth(id){ id ? localStorage.setItem(AUTH_KEY, id) : localStorage.removeItem(AUTH_KEY); }
  function getAuth(){
    const id = localStorage.getItem(AUTH_KEY);
    if(!id) return null;
    return getState().users.find(u=>u.id===id) || null;
  }
  function logout(){ setAuth(null); }

  function ensureLoggedIn(redirectUrl){
    const me = getAuth();
    if (!me) {
  const url = redirectUrl || window.location.pathname + window.location.search;
  window.location.href = "/login/?redirect=" + encodeURIComponent(url);
      return null;
    }
    return me;
  }
  return { getState, saveState, setAuth, getAuth, logout, ensureLoggedIn };
})();
