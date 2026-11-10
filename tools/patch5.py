import re
P='index.template.html'; h=open(P,encoding='utf-8').read()
def rep(o,n):
    global h
    assert h.count(o)==1,('count',h.count(o),o[:80]); h=h.replace(o,n)

# --- step 4 card body
h,nn=re.subn(r'(<div class="step-num">4</div><h2>Currency &amp; Conversion</h2></div>\s*<div class="card-body">).*?(<div class="fx-warn hidden" id="fx-warn"></div>)',
r'''\1
      <div class="cur-bar">
        <label>Quote currency:</label><select id="f-currency"></select>
        <button class="sec-btn" id="fx-reset" type="button">Use latest company rates</button>
        <span class="hint" style="margin-left:auto;">Totals are in the quote currency. Any line can be billed in another currency ("Bill in"). Rates are set company-wide in the Currency tab.</span>
      </div>
      <div class="hint" id="fx-summary" style="margin:4px 0;"></div>
      \2''',h,count=1,flags=re.S)
assert nn==1

# --- nav + view
rep('<button class="nav-btn" id="nav-dash">📊 Dashboard</button>','<button class="nav-btn" id="nav-dash">📊 Dashboard</button>\n      <button class="nav-btn" id="nav-fx">💱 Currency</button>')
rep('<div class="main hidden" id="view-dash">','''<div class="main hidden" id="view-fx">
  <div class="card">
    <div class="card-hdr"><h2>Currency &amp; Conversion (company-wide)</h2></div>
    <div class="card-body">
      <p class="hint" id="fx-meta" style="margin-bottom:10px;"></p>
      <div class="tbl-wrap"><table class="dtbl fx-tbl" id="fx-table"></table></div>
      <div class="allin-row" style="margin-top:12px;"><b>Transfer charge (%)</b>
        <span id="fx-fee-box"></span>
        <span class="hint">Added when a line's cost currency differs from the currency it is billed in.</span></div>
      <div id="fx-admin" class="hidden" style="margin-top:14px;border-top:1px solid var(--border);padding-top:12px;">
        <div class="allin-row">
          <input type="text" id="fx-new-code" placeholder="New currency code, e.g. SAR" maxlength="4" style="max-width:200px;flex:none;text-transform:uppercase;">
          <input type="number" id="fx-new-rate" placeholder="AED per 1 unit" step="0.0001" min="0" style="max-width:160px;flex:none;border:1.5px solid var(--border);border-radius:8px;padding:6px 10px;font-size:13px;">
          <button class="sec-btn" id="fx-add" type="button">Add currency</button>
        </div>
        <div class="allin-row" style="margin-top:10px;">
          <input type="password" id="fx-pin" placeholder="Admin PIN" autocomplete="off" style="max-width:220px;flex:none;">
          <button class="gen-btn" id="fx-save" type="button" style="padding:9px 22px;font-size:13px;">Save rates for everyone</button>
          <span class="hint" id="fx-save-msg"></span>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="main hidden" id="view-dash">''')

# --- state helpers
rep("function defFx(){ const f = DATA.fx || {}; return {rates:Object.assign({AED:1}, f.rates||{}), fee:(typeof f.fee==='number'?f.fee:0)}; }",
"""// company-wide rates: loaded from the database (fx_settings); falls back to the workbook defaults
let GFX = null, GFX_ERR = '';
function globalFx(){
  const d = DATA.fx || {}, g = GFX || {};
  const rates = Object.assign({AED:1}, d.rates||{}, g.rates||{}); rates.AED = 1;
  const fee = (typeof g.fee==='number') ? g.fee : (typeof d.fee==='number' ? d.fee : 0);
  return {rates, fee, asOf:g.updated_at||'', by:g.updated_by||''};
}
function defFx(){ return JSON.parse(JSON.stringify(globalFx())); }""")

a=h.index("function renderFx(){"); b=h.index("function renderAllinOpts(){")
h=h[:a]+"""function renderFx(){
  const keys = Object.keys(S.fx.rates);
  if(!keys.includes(S.currency)) keys.push(S.currency);
  const names = (DATA.fx||{}).names || {};
  $('f-currency').innerHTML = keys.map(c => `<option value="${c}">${c}${names[c]?' – '+escHtml(names[c]):''}${fxRate(c)==null?' (rate missing)':''}</option>`).join('');
  $('f-currency').value = S.currency;
  const used = keys.filter(c => c!=='AED' && fxRate(c)!=null).map(c => '1 '+c+' = '+S.fx.rates[c]+' AED').join(' · ');
  $('fx-summary').textContent = 'Rates in this quote: ' + (used || 'none set') + (S.fx.fee ? ' · transfer charge ' + Math.round(S.fx.fee*10000)/100 + '%' : '') + (GFX_ERR ? ' · (database not reachable, using default rates)' : '');
}
"""+h[b:]
rep("  $('fx-fee').addEventListener('input', e => { S.fx.fee = Math.max(0, num(e.target.value))/100; renderCharges(); });\n","")
a=h.index("  $('fx-rates').addEventListener('input'"); b=h.index("  $('fx-reset').addEventListener")
h=h[:a]+h[b:]
rep("$('fx-reset').addEventListener('click', () => { S.fx = defFx(); renderFx(); renderCharges(); });",
    "$('fx-reset').addEventListener('click', async () => { await loadGlobalFx(); S.fx = defFx(); renderFx(); renderCharges(); toast('Latest company rates applied'); });")

# --- DB methods
rep("  async count(){","""  async fxGet(){
    const r = await fetch(CONFIG.SUPABASE_URL+'/rest/v1/fx_settings?id=eq.1&select=*', {headers:this.hdr()});
    if(!r.ok) throw new Error('read failed ('+r.status+')');
    return (await r.json())[0] || null;
  },
  async fxSave(pin, rates, fee, by){
    const r = await fetch(CONFIG.SUPABASE_URL+'/rest/v1/rpc/save_fx', {method:'POST', headers:this.hdr(), body:JSON.stringify({p_pin:pin, p_rates:rates, p_fee:fee, p_by:by})});
    if(!r.ok){ let m = ''; try{ m = (await r.json()).message; }catch(e){} throw new Error(m || ('save failed ('+r.status+')')); }
  },
  async count(){""")
rep("  ALLOWED_DOMAIN: 'sascoglobal.com',","  ALLOWED_DOMAIN: 'sascoglobal.com',\n  FX_ADMIN: 'nikhil@sascoglobal.com',   // only this person sees the edit controls in the Currency tab")

# --- JS for currency view
rep("function showView(v){","""async function loadGlobalFx(){
  if(!DB.cloud()){ renderFxView(); return; }
  try{
    const row = await DB.fxGet();
    if(row){ GFX = {rates:row.rates||{}, fee:+row.fee||0, updated_at:row.updated_at, updated_by:row.updated_by}; }
    GFX_ERR = '';
  }catch(e){ GFX_ERR = e.message||'error'; }
  renderFxView();
}
let FXD = null;
function renderFxView(){
  const g = globalFx(), admin = (S.user === CONFIG.FX_ADMIN);
  if(!FXD || !admin) FXD = JSON.parse(JSON.stringify(g));
  const names = (DATA.fx||{}).names || {};
  $('fx-meta').textContent = GFX_ERR ? ('Database not reachable ('+GFX_ERR+'). Showing the default rates from the workbook.')
    : (g.asOf ? 'Last updated '+String(g.asOf).slice(0,16).replace('T',' ')+' by '+(g.by||'?') : 'No company rates saved yet. Showing the workbook defaults.');
  $('fx-table').innerHTML = '<tr><th>Currency</th><th>Name</th><th style="text-align:right;">AED per 1 unit</th></tr>' +
    Object.keys(FXD.rates).map(c => {
      const v = FXD.rates[c];
      const cell = c==='AED' ? '1' : (admin ? `<input type="number" min="0" step="0.0001" data-fxc="${c}" value="${v==null?'':v}" placeholder="not set">` : (v==null?'<span style="color:#dc2626;">not set</span>':v));
      return `<tr><td><b>${c}</b></td><td>${escHtml(names[c]||'')}</td><td style="text-align:right;">${cell}</td></tr>`;
    }).join('');
  $('fx-fee-box').innerHTML = admin ? `<input type="number" id="fx-fee-in" min="0" step="0.01" value="${FXD.fee?Math.round(FXD.fee*10000)/100:''}" placeholder="0" style="width:90px;border:1.5px solid var(--border);border-radius:8px;padding:6px 8px;">` : `<b>${Math.round(g.fee*10000)/100}%</b>`;
  $('fx-admin').classList.toggle('hidden', !admin);
  if(!admin) $('fx-meta').textContent += '. Only ' + CONFIG.FX_ADMIN + ' can change these rates.';
}
function initFxView(){
  $('fx-table').addEventListener('input', e => { const c = e.target.dataset.fxc; if(!c) return; const v = parseFloat(e.target.value); FXD.rates[c] = v>0 ? v : null; });
  $('fx-fee-box').addEventListener('input', e => { if(e.target.id==='fx-fee-in') FXD.fee = Math.max(0, num(e.target.value))/100; });
  $('fx-add').addEventListener('click', () => {
    const c = gv('fx-new-code').trim().toUpperCase().replace(/[^A-Z]/g,''), v = parseFloat($('fx-new-rate').value);
    if(c.length<3){ toast('Enter a 3-letter currency code'); return; }
    FXD.rates[c] = v>0 ? v : null; $('fx-new-code').value = ''; $('fx-new-rate').value = ''; renderFxView();
  });
  $('fx-save').addEventListener('click', async () => {
    if(S.user !== CONFIG.FX_ADMIN) return;
    const pin = gv('fx-pin'), msg = $('fx-save-msg');
    if(!pin){ msg.textContent = 'Enter the admin PIN.'; return; }
    if(!DB.cloud()){ msg.textContent = 'Connect the database first.'; return; }
    msg.textContent = 'Saving…';
    try{
      await DB.fxSave(pin, FXD.rates, FXD.fee, S.user);
      $('fx-pin').value = ''; msg.textContent = 'Saved. All users now get these rates.';
      await loadGlobalFx(); if(!S.persisted){ S.fx = defFx(); renderFx(); renderCharges(); }
    }catch(e){ msg.textContent = 'Not saved: '+e.message; }
  });
  $('nav-fx').addEventListener('click', () => showView('fx'));
}
function showView(v){""")
rep("  $('view-dash').classList.toggle('hidden', v!=='dash');\n  $('nav-quote').classList.toggle('active', v==='quote'); $('nav-dash').classList.toggle('active', v==='dash');",
    "  $('view-dash').classList.toggle('hidden', v!=='dash'); $('view-fx').classList.toggle('hidden', v!=='fx');\n  $('nav-quote').classList.toggle('active', v==='quote'); $('nav-dash').classList.toggle('active', v==='dash'); $('nav-fx').classList.toggle('active', v==='fx');\n  if(v==='fx'){ FXD = null; loadGlobalFx(); }")
rep("  watchDirty();\n  initGate();","  watchDirty(); initFxView();\n  initGate();\n  loadGlobalFx().then(() => { if(!S.persisted){ S.fx = defFx(); renderFx(); renderCharges(); } });")
open(P,'w',encoding='utf-8').write(h); print('ok')
