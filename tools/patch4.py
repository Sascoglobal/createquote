import re
P='index.template.html'; h=open(P,encoding='utf-8').read()
def rep(o,n):
    global h
    assert h.count(o)==1,('count',h.count(o),o[:80]); h=h.replace(o,n)

# ===== 4) colours
rep("--navy:#1B2A4A;--navy2:#2E4D8B;--blue:#4472C4;","--navy:#018bce;--navy2:#0172a8;--blue:#018bce;--on-orange:#0b3b55;")
rep("--orange:#E8630A;--orange-lt:#FDEBD0;","--orange:#eef5f1;--orange-lt:#f6faf8;")
rep("</style>","""/* colour overrides: accent #eef5f1 is light, so text on it is dark */
.logo-sq{color:var(--on-orange);}
.nav-btn.active{color:var(--on-orange);}
.step-num{color:var(--on-orange)!important;}
.ctbl .sec-row td{color:var(--on-orange)!important;}
.sec-row a{color:var(--navy2)!important;}
.gen-bar{border-top:2px solid var(--navy);}
.gen-btn{color:var(--on-orange);border:1.5px solid var(--navy);}
.gate-box button{color:var(--on-orange)!important;border:1.5px solid var(--navy)!important;}
.tot-row.vat{background:var(--orange-lt);}
.hdr-logo{height:44px;width:auto;background:#fff;border-radius:8px;padding:3px 6px;display:block;}
.dash-err{background:#fef2f2;border:1px solid #fecaca;color:#991b1b;border-radius:8px;padding:10px 12px;font-size:13px;margin-bottom:12px;}
.fx-tbl input{border:1.5px solid var(--border);border-radius:6px;padding:5px 8px;font-size:13px;width:130px;text-align:right;}
.fx-tbl td,.fx-tbl th{padding:7px 10px;}
</style>""")
rep("const NAVY=[27,42,74], NAVY2=[46,77,139], ORANGE=[232,99,10], ALT=[235,241,248], WHITE=[255,255,255], GOLD=[245,197,24], ORA_LT=[253,235,208];",
    "const NAVY=[1,139,206], NAVY2=[1,114,168], ORANGE=[238,245,241], ALT=[235,241,248], WHITE=[255,255,255], GOLD=[230,245,255], ORA_LT=[246,250,248];")
rep("doc.setTextColor(...(g?WHITE:[40,40,40]));","doc.setTextColor(...(g?NAVY2:[40,40,40]));")

# ===== 1) Courier
rep('<button class="chip" data-val="warehouse">🏭 Warehousing</button>','<button class="chip" data-val="courier">📦 Courier</button>\n            <button class="chip" data-val="warehouse">🏭 Warehousing</button>')
rep("function modeLabel(){ return {sea:'Sea',air:'Air',land:'Land',warehouse:'Warehousing'}[S.mode]; }","function modeLabel(){ return {sea:'Sea',air:'Air',land:'Land',courier:'Courier',warehouse:'Warehousing'}[S.mode]; }")
rep("const wh = S.mode==='warehouse', air = S.mode==='air';\n  $('sec-direction')","const wh = S.mode==='warehouse', air = S.mode==='air', cou = S.mode==='courier';\n  $('sec-direction')")
rep("$('sec-container').classList.toggle('hidden', wh || air);","$('sec-container').classList.toggle('hidden', wh || air || cou);")
rep("  else if(S.mode==='land'){ polL.textContent='Loading Point / Origin';","  else if(cou){ polL.textContent='Origin (City / Address)'; podL.textContent='Destination (City / Address)'; delL.textContent='Place of Delivery'; }\n  else if(S.mode==='land'){ polL.textContent='Loading Point / Origin';")
rep("  if(S.mode==='land'){\n    h += fld('Truck Type'","""  if(S.mode==='courier'){
    h += fld('Shipment Type','f-shiptype','select',['Parcel / Package','Documents','Mixed']);
    h += fld('Actual Weight (KG)','f-weight','text','');
    h += fld('Dimensions (L×W×H cm)','f-dims','text','Per package');
    h += fld('Chargeable Weight (KG)','f-chargewt','text','Higher of actual or L×W×H ÷ 5000');
    h += fld('No. of Pieces','f-pkgs','text','');
    h += fld('Courier / Service Level','f-carrier','text','e.g., DHL Express, FedEx Priority');
  }
  if(S.mode==='land'){
    h += fld('Truck Type'""")
rep("const polL = S.mode==='air'?'Airport of Origin':S.mode==='land'?'Loading Point':","const polL = S.mode==='air'?'Airport of Origin':S.mode==='courier'?'Origin':S.mode==='land'?'Loading Point':")
rep("const podL = S.mode==='air'?'Airport of Destination':S.mode==='land'?'Delivery Point':'Port of Discharge';","const podL = S.mode==='air'?'Airport of Destination':S.mode==='courier'?'Destination':S.mode==='land'?'Delivery Point':'Port of Discharge';")

# ===== 3) names / login
rep("""function fullName(email){
  const t = (DATA.team||[]).find(x => x.email === email);
  if(t && t.name) return t.name;
  return""","""function fullName(email){
  email = (email||'').trim().toLowerCase();
  const t = (DATA.team||[]).find(x => x.email === email);
  if(t && t.name) return t.name;
  try{ const n = localStorage.getItem('sasco_name_'+email); if(n) return n; }catch(e){}
  return""")
rep('<div class="gate-err" id="gate-err"></div>','<div class="hidden" id="gate-name-wrap"><input type="text" id="gate-name" placeholder="Your full name (as it should appear on quotes)" autocomplete="name" style="margin-top:8px;"></div>\n    <div class="gate-err" id="gate-err"></div>')
rep("    $('gate-err').textContent = '';\n    enterApp(v);","""    $('gate-err').textContent = '';
    if(!teamOf(v)){
      const nm = gv('gate-name').trim();
      if(!nm){ $('gate-name-wrap').classList.remove('hidden'); $('gate-err').textContent = 'This email is not in the team list. Enter your full name to continue.'; return; }
      try{ localStorage.setItem('sasco_name_'+v.trim().toLowerCase(), nm); }catch(e){}
    }
    enterApp(v);""")
rep("  if(!gv('f-prepby')) $('f-prepby').value = fullName(S.user);\n  $('mode-banner')","  $('f-prepby').value = fullName(S.user);\n  $('mode-banner')")
rep("    created_by_name: gv('f-prepby') || fullName(S.user),","    created_by_name: fullName(S.createdBy || S.user),")
rep("  const sl = ['Name / Designation:','Signature, Date & Stamp:'];","  const sl = ['Name / Designation:','Signature, Date & Stamp:'];\n  const prepT = teamOf(S.createdBy || S.user), prepName = (gv('f-prepby') || fullName(S.createdBy || S.user)) + (prepT && prepT.role ? ' / ' + prepT.role : '');")
rep("    doc.text(sl[0], x+2, sy+4.4+3.4); doc.text(sl[1], x+2, sy+sigH-1.8);","""    if(i===0){ doc.setFont('helvetica','bold'); doc.setTextColor(40,40,40); doc.text(pdfSafe(prepName), x+2, sy+4.4+3.4, {maxWidth:sigW-6}); doc.setFont('helvetica','normal'); doc.setTextColor(120,120,120); }
    else doc.text(sl[0], x+2, sy+4.4+3.4);
    doc.text(sl[1], x+2, sy+sigH-1.8);""")

# ===== 6) save before export + dirty tracking
rep("function setSaveState(t){ $('save-state').textContent = t; }","""function setSaveState(t){ $('save-state').textContent = t; }
let SNAP = '';
function snapNow(){ try{ return JSON.stringify(serialize()); }catch(e){ return Math.random()+''; } }
function markSaved(){ SNAP = snapNow(); }
function isSaved(){ return S.persisted && SNAP === snapNow(); }
function needSave(){
  if(isSaved()) return false;
  toast('Please save the quotation first (Save button), then generate the PDF or email.', 5000);
  return true;
}
let _dirtyT = null;
function watchDirty(){
  const f = () => { clearTimeout(_dirtyT); _dirtyT = setTimeout(() => { if(S.persisted && !isSaved()) setSaveState('Unsaved changes'); else if(!S.persisted) setSaveState('Not saved yet'); }, 250); };
  ['input','change','click'].forEach(ev => $('view-quote').addEventListener(ev, f));
}""")
rep("    setSaveState('Saved '+new Date()","    markSaved();\n    setSaveState('Saved '+new Date()")
rep("  const {doc} = makePdf();\n  await saveQuote(true);\n","  const {doc} = makePdf();\n")
rep("toast('PDF generated and quotation saved');","toast('PDF generated');")
rep("  $('email-modal').classList.remove('hidden');\n  await saveQuote(true);\n}","  $('email-modal').classList.remove('hidden');\n}")
rep("async function generatePDF(){\n  if(fxBlocked()) return;","async function generatePDF(){\n  if(needSave()) return;\n  if(fxBlocked()) return;")
rep("async function openEmail(){\n  if(fxBlocked()) return;","async function openEmail(){\n  if(needSave()) return;\n  if(fxBlocked()) return;")
rep("  initGate();\n  if(!S.user)","  watchDirty();\n  initGate();\n  if(!S.user)")

# ===== 7) add charge line with section picker
rep('''        <button class="add-btn" id="btn-add-row">＋ Add Charge Line</button>
        <span class="hint">|</span>
        <input type="text" class="sec-name-inp" id="new-sec-name" placeholder="New section name…">
        <button class="add-sec-confirm" id="btn-add-sec">＋ Add Section</button>''','''        <label class="hint" for="add-sec-sel">Add to section:</label>
        <select id="add-sec-sel" class="cur-sel" style="width:auto;padding:6px 8px;">
          <option value="FREIGHT">Freight</option><option value="ORIGIN">Origin</option><option value="DESTINATION">Destination</option>
          <option value="CUSTOMS">Customs</option><option value="DELIVERY">Delivery</option><option value="INSURANCE">Insurance</option>
          <option value="WAREHOUSE">Warehouse</option><option value="OTHER">Other</option>
        </select>
        <button class="add-btn" id="btn-add-row">＋ Add Charge Line</button>''')
a=h.index("  const blank = () => ({d:''"); b=h.index("  $('disc-type').addEventListener")
h=h[:a]+"""  const blank = cat => ({d:'', u:'Per Shipment', ccy:S.currency, bill:'', pct:false, r:'', q:1, rem:'', rc:'Editable', on:true, vat:true, locked:false, cat});
  $('btn-add-row').addEventListener('click', () => {
    const cat = $('add-sec-sel').value;
    let sec = S.charges.find(s => s.cat===cat);
    if(!sec){ sec = {sec:CAT_LABEL[cat]||cat, cat, rows:[]}; S.charges.push(sec); sortSections(); }
    sec.rows.push(blank(cat));
    renderCharges();
    const tr = $('charges-body').querySelector(`tr[data-si="${S.charges.indexOf(sec)}"][data-ri="${sec.rows.length-1}"] input[data-key="d"]`);
    if(tr){ tr.scrollIntoView({block:'center'}); tr.focus(); }
  });
"""+h[b:]
rep("function calc(){","""function catRank(c){ const i = CAT_ORDER.indexOf(c); return i>=0 ? i : (c==='WAREHOUSE' ? 20 : 30); }
function sortSections(){ S.charges.sort((a,b) => catRank(a.cat) - catRank(b.cat)); }
function calc(){""")
rep("  const custom = S.charges.map(s => ({sec:s.sec, cat:'OTHER', rows:s.rows.filter(r => !r.id)})).filter(s => s.rows.length);","  const custom = []; S.charges.forEach(s => s.rows.forEach(r => { if(!r.id){ r.cat = r.cat || s.cat || 'OTHER'; custom.push(r); } }));")
rep("  S.charges = secs.concat(custom);","""  custom.forEach(r => {
    const c = r.cat || 'OTHER', key = c==='WAREHOUSE' ? 'WH:ADDED' : c;
    let g = secs.find(s => (s.cat===c) && (c!=='WAREHOUSE' || s.sec==='WAREHOUSE' || true));
    if(!g){ g = {sec: CAT_LABEL[c]||c, cat:c, rows:[]}; secs.push(g); }
    g.rows.push(r);
  });
  S.charges = secs; sortSections();""")

# ===== dashboard error display
rep('<div class="stat-row" id="dash-stats"></div>','<div class="dash-err hidden" id="dash-err"></div>\n  <div class="stat-row" id="dash-stats"></div>')
rep("  try{ QUOTES = await DB.list(); }catch(e){ toast(e.message, 5000); QUOTES = []; }\n  renderDash();","""  const box = $('dash-err'); box.classList.add('hidden');
  try{ QUOTES = await DB.list(); }
  catch(e){
    QUOTES = [];
    box.classList.remove('hidden');
    box.innerHTML = '<b>Could not load quotations from the database.</b> ' + escHtml(e.message||'') + ' The Supabase project is probably paused or offline. Open the Supabase dashboard, restore the project, then press Refresh. Nothing has been lost: saved quotations are still in the database.';
  }
  renderDash();""")
open(P,'w',encoding='utf-8').write(h); print('ok')
