import re
P = 'index.template.html'
h = open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global h
    assert h.count(old) >= 1, 'missing: ' + old[:80]
    if count == 1: assert h.count(old) == 1, 'not unique: ' + old[:80]
    h = h.replace(old, new)

# ---- DATA placeholder
rep("const DATA = /*__DATA__*/{charges:[],terms:[],matrix:{},settings:{},team:[]};",
    "const DATA = /*__DATA__*/{charges:[],terms:[],matrix:{},settings:{},team:[],fx:{rates:{AED:1},names:{},fee:0}};")

# ---- CSS
rep("</style>", """.fx-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:8px;margin:4px 0 8px;}
.fx-item{display:flex;align-items:center;gap:6px;font-size:12.5px;background:var(--alt);border-radius:8px;padding:6px 8px;}
.fx-item input{width:92px;border:1.5px solid var(--border);border-radius:6px;padding:4px 6px;font-size:13px;text-align:right;}
.fx-item input.bad{border-color:#dc2626;background:#fef2f2;}
.fx-warn{background:#fef2f2;border:1px solid #fecaca;color:#991b1b;border-radius:8px;padding:8px 10px;font-size:12.5px;margin-top:6px;}
.cur-bar input[type=number]{border:1.5px solid var(--border);border-radius:8px;padding:6px 8px;font-size:13px;width:80px;}
.allin{border:1.5px dashed var(--border);border-radius:10px;padding:10px 12px;margin-bottom:12px;background:#fafbfd;}
.allin label.top{font-size:13px;display:flex;gap:8px;align-items:center;cursor:pointer;}
.allin-cats{display:flex;flex-wrap:wrap;gap:6px 14px;margin:8px 0;font-size:12.5px;}
.allin-cats label{display:flex;gap:5px;align-items:center;cursor:pointer;}
.allin-row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:4px;}
.allin-row input[type=text]{flex:1;min-width:220px;border:1.5px solid var(--border);border-radius:8px;padding:6px 10px;font-size:13px;}
.allin-prev{margin-top:8px;font-size:12.5px;background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:8px 10px;}
.sec-row a{color:#fff;opacity:.85;font-weight:400;text-transform:none;letter-spacing:0;cursor:pointer;text-decoration:underline;margin-left:10px;font-size:10.5px;}
</style>""")

# ---- HTML: charges card
rep('''<div class="card">
    <div class="card-hdr"><div class="step-num">4</div><h2>Charges Breakdown</h2></div>''',
'''<div class="card">
    <div class="card-hdr"><div class="step-num">4</div><h2>Currency &amp; Conversion</h2></div>
    <div class="card-body">
      <div class="cur-bar">
        <label>Quote currency:</label><select id="f-currency"></select>
        <label>Transfer charge %:</label><input type="number" id="fx-fee" min="0" step="0.01" placeholder="0">
        <button class="sec-btn" id="fx-reset" type="button">Reset to defaults</button>
        <span class="hint" style="margin-left:auto;">Every rate and amount prints in the quote currency only. The transfer charge is added when a line's cost currency differs.</span>
      </div>
      <div class="fx-grid" id="fx-rates"></div>
      <div class="fx-warn hidden" id="fx-warn"></div>
    </div>
  </div>

  <div class="card">
    <div class="card-hdr"><div class="step-num">5</div><h2>Charges Breakdown</h2></div>''')
h = re.sub(r'<div class="cur-bar">\s*<label>Currency:</label>.*?<span class="hint" style="margin-left:auto;">☑ include.*?</span>\s*</div>',
'''<div class="allin">
        <label class="top"><input type="checkbox" id="allin-on"> <b>All-in quote</b> &nbsp;print one lump-sum line instead of itemised charges (nothing is deleted)</label>
        <div id="allin-opts" class="hidden">
          <div class="hint">Roll these groups into the all-in line. Other groups still print line by line:</div>
          <div class="allin-cats" id="allin-cats"></div>
          <div class="allin-row"><label class="hint">Line wording</label><input type="text" id="allin-label" placeholder="All-in Freight &amp; Charges"></div>
          <div class="allin-prev" id="allin-prev"></div>
        </div>
      </div>
      <div class="cur-bar">
        <label>VAT Rate:</label>
        <select id="f-vat">
          <option value="0.05">5% (UAE Standard)</option>
          <option value="0">0% (Exempt / Out-of-Scope)</option>
          <option value="0.10">10%</option>
        </select>
        <span class="hint" style="margin-left:auto;">☑ include a line · VAT ☑ marks it VAT-chargeable · 🔒 = fixed rate · section headings show here only, not in the print or email</span>
      </div>''', h, count=1, flags=re.S)
assert 'id="allin-on"' in h
rep('<th style="width:92px;" class="r">Rate</th>', '<th style="width:92px;" class="r" id="th-rate">Rate</th>')
rep('<th style="width:100px;" class="r">Amount</th>', '<th style="width:100px;" class="r" id="th-amt">Amount</th>')
rep('<div class="step-num">5</div><h2>Terms &amp; Conditions', '<div class="step-num">6</div><h2>Terms &amp; Conditions')
rep('<div class="step-num">6</div><h2>Notes &amp; Special Instructions', '<div class="step-num">7</div><h2>Notes &amp; Special Instructions')
rep('add client email in step 3', 'add client email in step 3')

# ---- serialize
rep("currency:S.currency,vatRate:S.vatRate,disc:S.disc},", "currency:S.currency,vatRate:S.vatRate,disc:S.disc,fx:S.fx,allin:S.allin},")

# ---- state init
rep("  disc:{type:'pct', val:''},\n  user:null,", "  disc:{type:'pct', val:''}, fx:null, allin:null,\n  user:null,")

# ---- CHARGES section replacement
a = h.index("function buildCharges(){")
b = h.index("// ═══════════════════════════════════════════════════════════════\n// TERMS & CONDITIONS (layered from DATA)")
NEW = r'''const CAT_ORDER = ['FREIGHT','ORIGIN','DESTINATION','CUSTOMS','DELIVERY','INSURANCE'];
const CAT_LABEL = {FREIGHT:'Freight',ORIGIN:'Origin',DESTINATION:'Destination',CUSTOMS:'Customs',DELIVERY:'Delivery',INSURANCE:'Insurance',WAREHOUSE:'Warehouse',OTHER:'Other'};
function listHas(v, x){
  if(v==null || v==='' || String(v).toUpperCase()==='ALL') return true;
  return String(v).split(',').map(s => s.trim().toLowerCase()).includes(String(x).toLowerCase());
}
function round2(x){ return Math.round((x + Number.EPSILON)*100)/100; }

// ---- currency
function defFx(){ const f = DATA.fx || {}; return {rates:Object.assign({AED:1}, f.rates||{}), fee:(typeof f.fee==='number'?f.fee:0)}; }
function defAllin(){ return {on:false, label:'All-in Freight & Charges', cats:{FREIGHT:true, ORIGIN:true, DESTINATION:true}}; }
function fxRate(c){ const v = S.fx.rates[c]; return (typeof v==='number' && v>0) ? v : null; }
function fxFactor(from, to){
  if(!from || from===to) return 1;
  const a = fxRate(from), b = fxRate(to);
  if(a==null || b==null) return null;
  return a/b*(1+(S.fx.fee||0));
}
function rowCalc(r){
  if(r.pct){ const rt = num(r.r); return {rate:rt, amt:round2(rt*num(r.q)), miss:false}; }
  if(r.r==='' || r.r==null) return {rate:0, amt:0, miss:false};
  const f = fxFactor(r.ccy || S.currency, S.currency);
  if(f==null) return {rate:0, amt:0, miss:true};
  const rate = round2(num(r.r)*f);
  return {rate, amt:round2(rate*num(r.q)), miss:false};
}
function missingFx(){
  const out = new Set();
  if(fxRate(S.currency)==null) out.add(S.currency);
  S.charges.forEach(s => s.rows.forEach(r => {
    if(!r.on || r.pct || r.r==='' || r.r==null) return;
    const c = r.ccy || S.currency;
    if(c!==S.currency && fxRate(c)==null) out.add(c);
  }));
  return [...out];
}

// ---- build
function buildCharges(){
  const prev = {};
  S.charges.forEach(s => s.rows.forEach(r => { if(r.id) prev[r.id] = r; }));
  const custom = S.charges.map(s => ({sec:s.sec, cat:'OTHER', rows:s.rows.filter(r => !r.id)})).filter(s => s.rows.length);
  const m = cap(S.mode), d = S.mode==='warehouse' ? 'ALL' : cap(S.dir), ld = loadLabel(), nat = cap(S.cargo);
  const groups = {}, whOrder = [];
  DATA.charges.forEach(c => {
    if(!listHas(c.mode, m)) return;
    if(!listHas(c.dir, d)) return;
    if(!listHas(c.load, ld)) return;
    if(!listHas(c.nature, nat)) return;
    if(!listHas(c.ctype, S.ctype)) return;
    const explicitInco = !(c.inco==null || c.inco==='' || c.inco==='ALL');
    if(explicitInco && !listHas(c.inco, S.inco)) return;
    if(!explicitInco && S.mode!=='warehouse'){
      const gate = (((DATA.matrix||{})[S.inco]||{})[cap(S.dir)]||{})[c.cat];
      if(gate === 'N') return;
    }
    const cost = (typeof c.cost==='number') ? c.cost : null;
    const sell = cost==null ? '' : Math.round(cost*(1+(c.margin||0))*1e6)/1e6;
    const row = {id:c.id, d:c.d, u:c.u, ccy:c.ccy, pct:!!c.pct, r:sell, q:c.q, rem:c.rem, rc:c.rc, on:!!c.on, vat:!!c.vat, cat:c.cat,
                 locked:(c.rc==='Auto' && cost>0)};
    const p = prev[c.id];
    if(p){ row.q=p.q; row.rem=p.rem; row.on=p.on; row.vat=p.vat; row.d=p.d; row.u=p.u; if(!row.locked){ row.r=p.r; row.ccy=p.ccy; } }
    const key = c.cat==='WAREHOUSE' ? 'WH:'+c.sec : c.cat;
    if(!groups[key]){ groups[key] = {sec: c.cat==='WAREHOUSE' ? c.sec : (CAT_LABEL[c.cat]||c.cat), cat:c.cat, rows:[]}; if(c.cat==='WAREHOUSE') whOrder.push(key); }
    groups[key].rows.push(row);
  });
  const order = CAT_ORDER.concat(whOrder, ['OTHER']);
  const secs = order.filter(k => groups[k]).map(k => groups[k]);
  Object.keys(groups).forEach(k => { if(!order.includes(k)) secs.push(groups[k]); });
  S.charges = secs.concat(custom);
}

function calc(){
  let sub = 0, vatBase = 0;
  S.charges.forEach(s => s.rows.forEach(r => {
    if(!r.on) return;
    const a = rowCalc(r).amt; sub += a; if(r.vat) vatBase += a;
  }));
  sub = round2(sub);
  let disc = S.disc.type==='pct' ? sub*num(S.disc.val)/100 : num(S.disc.val);
  disc = Math.min(Math.max(disc,0), sub);
  const ratio = sub ? (1 - disc/sub) : 1;
  const vb = vatBase*ratio, vat = round2(vb*S.vatRate), net = round2(sub-disc);
  return {sub, disc:round2(disc), net, vatBase:vb, vat, grand:round2(net+vat)};
}

// ---- what actually prints (PDF + email): itemised, or one all-in line
function rateStr(l){
  if(!l.rate) return '-';
  return l.pct ? (Math.round(l.rate*10000)/100)+'%' : money(l.rate);
}
function outputLines(){
  const rows = []; S.charges.forEach(s => s.rows.forEach(r => { if(r.on) rows.push(r); }));
  const A = S.allin || defAllin(), lines = []; let note = '';
  const inAll = r => A.on && !!A.cats[r.cat||'OTHER'];
  if(A.on){
    const grp = rows.filter(inAll), priced = grp.filter(r => rowCalc(r).amt > 0), un = grp.filter(r => !(rowCalc(r).amt > 0));
    if(priced.length){
      const tot = round2(priced.reduce((a,r) => a + rowCalc(r).amt, 0)), nv = priced.filter(r => r.vat).length;
      lines.push({d:A.label||'All-in Charges', u:'Lump sum', rate:0, q:0, amt:tot, vat:(nv===priced.length?'Y':nv===0?'-':'Part'), rem:'', allin:true});
    }
    if(un.length) note = 'Not included in the all-in price (charged at actuals / on request): ' + un.map(r => r.d).join('; ') + '.';
  }
  rows.filter(r => !inAll(r)).forEach(r => {
    const c = rowCalc(r);
    lines.push({d:r.d, u:r.u, rate:c.rate, q:num(r.q), amt:c.amt, vat:r.vat?'Y':'-', rem:r.rem||'', pct:r.pct, act:/actual/i.test(r.u||'') && !c.rate});
  });
  return {lines, note};
}

// ---- render
function renderFx(){
  const keys = Object.keys(S.fx.rates);
  if(!keys.includes(S.currency)) keys.push(S.currency);
  const names = (DATA.fx||{}).names || {};
  $('f-currency').innerHTML = keys.map(c => `<option value="${c}">${c}${names[c]?' – '+escHtml(names[c]):''}${fxRate(c)==null?' (rate missing)':''}</option>`).join('');
  $('f-currency').value = S.currency;
  $('fx-fee').value = S.fx.fee ? Math.round(S.fx.fee*10000)/100 : '';
  $('fx-rates').innerHTML = keys.filter(c => c!=='AED').map(c => {
    const v = S.fx.rates[c];
    return `<div class="fx-item"><b>1 ${c} =</b><input type="number" min="0" step="0.0001" data-fx="${c}" value="${v==null?'':v}" class="${fxRate(c)==null?'bad':''}" placeholder="rate"> AED</div>`;
  }).join('');
}
function renderAllinOpts(){
  const A = S.allin;
  $('allin-on').checked = !!A.on;
  $('allin-opts').classList.toggle('hidden', !A.on);
  $('allin-label').value = A.label || '';
  const cats = []; S.charges.forEach(s => s.rows.forEach(r => { const c = r.cat||'OTHER'; if(!cats.includes(c)) cats.push(c); }));
  cats.sort((a,b) => { const o = CAT_ORDER.concat(['WAREHOUSE','OTHER']); return o.indexOf(a)-o.indexOf(b); });
  $('allin-cats').innerHTML = cats.map(c => `<label><input type="checkbox" data-allincat="${c}" ${A.cats[c]?'checked':''}> ${CAT_LABEL[c]||c}</label>`).join('');
}
function renderCharges(){
  let html = '', n = 1;
  S.charges.forEach((sec, si) => {
    html += `<tr class="sec-row"><td colspan="9">▸ &nbsp;${escHtml(sec.sec)} <a data-action="sec-all" data-si="${si}">all</a><a data-action="sec-none" data-si="${si}">none</a></td><td style="text-align:right;"><button class="del-btn" data-action="del-sec" data-si="${si}" title="Remove section">✕</button></td></tr>`;
    sec.rows.forEach((row, ri) => {
      const c = rowCalc(row);
      const rv = row.r==='' ? '' : (row.pct ? Math.round(num(row.r)*10000)/100 : c.rate);
      html += `<tr class="${ri%2===0?'':'r-even'} ${row.on?'':'off'}" data-si="${si}" data-ri="${ri}">
        <td class="ctr" style="color:#6b7280;">${n++}</td>
        <td class="ctr"><input type="checkbox" data-si="${si}" data-ri="${ri}" data-key="on" ${row.on?'checked':''}></td>
        <td><input type="text" value="${escHtml(row.d)}" data-si="${si}" data-ri="${ri}" data-key="d"></td>
        <td><input type="text" value="${escHtml(row.u)}" data-si="${si}" data-ri="${ri}" data-key="u"></td>
        <td><input type="number" value="${rv}" placeholder="${row.pct?'0.00 %':'0.00'}" min="0" step="0.01" data-si="${si}" data-ri="${ri}" data-key="r" class="${row.locked?'locked':''}" ${row.locked?'readonly title="Fixed rate"':''} style="text-align:right;"></td>
        <td><input type="number" value="${row.q===''?'':row.q}" placeholder="0" min="0" step="0.01" data-si="${si}" data-ri="${ri}" data-key="q" style="text-align:right;" ${row.pct?'title="Cargo value in the quote currency"':''}></td>
        <td class="amt" id="amt-${si}-${ri}">${amtCell(row)}</td>
        <td class="ctr"><input type="checkbox" data-si="${si}" data-ri="${ri}" data-key="vat" ${row.vat?'checked':''}></td>
        <td><input type="text" value="${escHtml(row.rem||'')}" placeholder="Remarks…" data-si="${si}" data-ri="${ri}" data-key="rem"></td>
        <td><button class="del-btn" data-action="del-row" data-si="${si}" data-ri="${ri}" title="Remove row">✕</button></td>
      </tr>`;
    });
  });
  $('charges-body').innerHTML = html;
  renderAllinOpts();
  updateTotals();
}
function amtCell(row){
  const c = rowCalc(row);
  return (c.miss ? '<span style="color:#dc2626;" title="No exchange rate for '+escHtml(row.ccy||'')+'">⚠ FX</span>' : (c.amt ? money(c.amt) : '<span style="color:#aaa;">—</span>')) + (row.locked?' <span class="lock">🔒</span>':'');
}

function updateTotals(){
  const c = calc(), cur = S.currency, f = v => cur+' '+money(v);
  $('th-rate').textContent = 'Rate ('+cur+')'; $('th-amt').textContent = 'Amount ('+cur+')';
  $('tot-sub').textContent = f(c.sub);
  $('tot-disc').textContent = c.disc ? '− '+f(c.disc) : f(0);
  $('tot-net').textContent = f(c.net);
  $('vat-lbl').textContent = `VAT (${Math.round(S.vatRate*10000)/100}% on ${f(c.vatBase)})`;
  $('tot-vat').textContent = f(c.vat);
  $('tot-grand').textContent = f(c.grand);
  const mf = missingFx(), w = $('fx-warn');
  w.classList.toggle('hidden', !mf.length);
  w.textContent = mf.length ? 'No AED rate for '+mf.join(', ')+'. Fill it in above before generating the PDF or email.' : '';
  const A = S.allin;
  if(A && A.on){
    const o = outputLines(), first = o.lines.find(l => l.allin);
    $('allin-prev').innerHTML = first ? `Prints as: <b>${escHtml(first.d)}</b> — ${cur} ${money(first.amt)}` + (o.lines.length>1 ? ` &nbsp;+ ${o.lines.length-1} itemised line(s)` : '') : 'Nothing priced in the selected groups yet.';
    if(o.note) $('allin-prev').innerHTML += `<br><span class="hint">${escHtml(o.note)}</span>`;
  }
}

function initChargesEvents(){
  const body = $('charges-body');
  const apply = e => {
    const el = e.target; if(!el.dataset.key) return;
    const si = +el.dataset.si, ri = +el.dataset.ri, key = el.dataset.key, row = S.charges[si].rows[ri];
    if(el.type==='checkbox'){
      row[key] = el.checked;
      if(key==='on'){ el.closest('tr').classList.toggle('off', !el.checked); }
    } else if(key==='r'){
      if(el.value==='') row.r = '';
      else if(row.pct) row.r = parseFloat(el.value)/100;
      else { row.r = parseFloat(el.value); row.ccy = S.currency; }
    } else row[key] = el.value;
    if(key==='r' || key==='q' || key==='on' || key==='vat'){
      const cell = $(`amt-${si}-${ri}`); if(cell) cell.innerHTML = amtCell(row);
      updateTotals();
    }
  };
  body.addEventListener('input', apply);
  body.addEventListener('change', apply);
  body.addEventListener('click', e => {
    const btn = e.target.closest('[data-action]'); if(!btn) return;
    const si = +btn.dataset.si, act = btn.dataset.action;
    if(act==='del-row'){ S.charges[si].rows.splice(+btn.dataset.ri,1); if(!S.charges[si].rows.length) S.charges.splice(si,1); }
    else if(act==='sec-all' || act==='sec-none'){ S.charges[si].rows.forEach(r => r.on = (act==='sec-all')); }
    else S.charges.splice(si,1);
    renderCharges();
  });
  const blank = () => ({d:'', u:'Per Shipment', ccy:S.currency, pct:false, r:'', q:1, rem:'', rc:'Editable', on:true, vat:true, locked:false, cat:'OTHER'});
  $('btn-add-row').addEventListener('click', () => {
    if(!S.charges.length) S.charges.push({sec:'ADDITIONAL CHARGES', cat:'OTHER', rows:[]});
    S.charges[S.charges.length-1].rows.push(blank());
    renderCharges();
  });
  $('btn-add-sec').addEventListener('click', () => {
    const name = ($('new-sec-name').value || 'ADDITIONAL CHARGES').trim().toUpperCase(); $('new-sec-name').value = '';
    S.charges.push({sec:name, cat:'OTHER', rows:[blank()]});
    renderCharges();
  });
  $('disc-type').addEventListener('change', e => { S.disc.type = e.target.value; updateTotals(); });
  $('disc-val').addEventListener('input', e => { S.disc.val = e.target.value; updateTotals(); });
  $('f-vat').addEventListener('change', e => { S.vatRate = parseFloat(e.target.value); updateTotals(); });
  // currency
  $('f-currency').addEventListener('change', e => { S.currency = e.target.value; renderCharges(); });
  $('fx-fee').addEventListener('input', e => { S.fx.fee = Math.max(0, num(e.target.value))/100; renderCharges(); });
  $('fx-rates').addEventListener('input', e => {
    const c = e.target.dataset.fx; if(!c) return;
    const v = parseFloat(e.target.value); S.fx.rates[c] = (v>0 ? v : null);
    e.target.classList.toggle('bad', !(v>0)); renderCharges();
  });
  $('fx-reset').addEventListener('click', () => { S.fx = defFx(); renderFx(); renderCharges(); });
  // all-in
  $('allin-on').addEventListener('change', e => { S.allin.on = e.target.checked; renderAllinOpts(); updateTotals(); });
  $('allin-label').addEventListener('input', e => { S.allin.label = e.target.value; updateTotals(); });
  $('allin-cats').addEventListener('change', e => { const c = e.target.dataset.allincat; if(c){ S.allin.cats[c] = e.target.checked; updateTotals(); } });
}

'''
h = h[:a] + NEW + h[b:]

# ---- defaults / reset / open
rep("vatRate:(typeof ST.vat_rate==='number'?ST.vat_rate:0.05), disc:{type:'pct',val:''}, charges:[], terms:[], persisted:false, createdBy:null});",
    "vatRate:(typeof ST.vat_rate==='number'?ST.vat_rate:0.05), disc:{type:'pct',val:''}, charges:[], terms:[], persisted:false, createdBy:null, fx:defFx(), allin:defAllin()});")
rep("  $('f-currency').value = S.currency; $('f-vat').value = String(S.vatRate); $('disc-type').value='pct'; $('disc-val').value='';",
    "  renderFx(); $('f-vat').value = String(S.vatRate); $('disc-type').value='pct'; $('disc-val').value='';")
rep("  $('f-currency').value = S.currency; $('f-vat').value = String(S.vatRate);\n  $('disc-type').value = S.disc.type;",
    "  if(!S.fx) S.fx = defFx(); if(!S.allin) S.allin = defAllin();\n  renderFx(); $('f-vat').value = String(S.vatRate);\n  $('disc-type').value = S.disc.type;")
rep("  S.charges = p.charges||[]; S.terms = p.terms||[];", "  S.charges = p.charges||[]; S.terms = p.terms||[];\n  S.charges.forEach(s => { s.cat = s.cat||'OTHER'; s.rows.forEach(r => { r.cat = r.cat||s.cat||'OTHER'; r.ccy = r.ccy||S.currency; }); });")
rep("  $('f-currency').value = S.currency; $('f-vat').value = String(S.vatRate);\n  refreshTemplate();",
    "  S.fx = defFx(); S.allin = defAllin(); renderFx(); $('f-vat').value = String(S.vatRate);\n  refreshTemplate();")
# validity default
h = h.replace("const d = new Date(), v = new Date(); v.setDate(d.getDate() + (parseInt(ST.validity_days)||14));\n  $('f-date').value = todayISO(); $('f-valid').value = v.toISOString().slice(0,10);",
              "$('f-date').value = todayISO(); $('f-valid').value = defValid();")
assert "parseInt(ST.validity_days)" not in h
rep("function resetForm(confirmFirst){", "function defValid(){\n  const n = parseInt(ST.validity_days); if(!n) return '';\n  const v = new Date(); v.setDate(v.getDate()+n); return v.toISOString().slice(0,10);\n}\nfunction resetForm(confirmFirst){")

# ---- contact line + PDF header
rep("  return [ST.address, ST.phone, ST.website, ST.company_email||'sasco@sascoglobal.com'].filter(Boolean).join('   |   ');",
    "  return [ST.address, ST.phone, ST.website, ST.company_email||'sasco@sascoglobal.com', ST.trn?'TRN '+ST.trn:''].filter(Boolean).join('   |   ');")
rep("      doc.text(pdfSafe(contactLine()), 11, 16, {maxWidth:118});",
"""      const fit = (t, yy) => { let fs = 7; doc.setFontSize(fs); while(doc.getTextWidth(t) > 118 && fs > 4.6){ fs -= 0.2; doc.setFontSize(fs); } doc.text(t, 11, yy); };
      fit(pdfSafe(ST.address||''), 14.4);
      fit(pdfSafe([ST.phone, ST.website, ST.company_email||'sasco@sascoglobal.com', ST.trn?'TRN '+ST.trn:''].filter(Boolean).join('  |  ')), 18.6);""")

# ---- PDF charges body
a = h.index("  const body = [];\n  let k = 1;\n  S.charges.forEach(sec => {")
b = h.index("  const tfs = Math.max(6.1, 7.8*scale)")
h = h[:a] + """  const body = [];
  const OL = outputLines();
  OL.lines.forEach((l, i) => {
    body.push([i+1, pdfSafe(l.d), pdfSafe(l.u), l.allin ? '-' : rateStr(l), l.q ? String(l.q) : '-',
      l.amt ? money(l.amt) : (l.act ? 'At actuals' : '-'), l.vat, pdfSafe(l.rem)]);
  });
  if(OL.note) body.push([{content:pdfSafe(OL.note), colSpan:8, styles:{fontStyle:'italic', textColor:[90,90,90], fillColor:WHITE}}]);
""" + h[b:]

# ---- missingRates / generatePDF
a = h.index("function missingRates(){")
b = h.index("async function generatePDF(){")
h = h[:a] + """function missingRates(){
  let n = 0; S.charges.forEach(s => s.rows.forEach(r => { if(r.on && !rowCalc(r).rate && !/actual/i.test(r.u||'')) n++; }));
  return n;
}
function fxBlocked(){
  const mf = missingFx();
  if(mf.length){ toast('Add the AED rate for '+mf.join(', ')+' in step 4 first.', 6000); return true; }
  return false;
}
""" + h[b:]
rep("async function generatePDF(){\n  const miss", "async function generatePDF(){\n  if(fxBlocked()) return;\n  const miss")
rep("async function openEmail(){\n  const miss", "async function openEmail(){\n  if(fxBlocked()) return;\n  const miss")

# ---- email body
a = h.index("  S.charges.forEach(sec => {\n    const rows = sec.rows.filter(r => r.on); if(!rows.length) return;\n    h += `<tr><td colspan=\"5\"")
b = h.index("  const tot = [['Subtotal', C.sub, false]];")
h = h[:a] + """  const OL = outputLines();
  OL.lines.forEach(r => {
    const amt = r.amt ? money(r.amt) : (r.act ? 'At actuals' : '-');
    const rs = r.allin ? '-' : rateStr(r);
    h += `<tr><td style="${tdS}">${escHtml(r.d)}${r.rem?` <span style="color:#6b7280;font-size:11px;">(${escHtml(r.rem)})</span>`:''}</td><td style="${tdS}">${escHtml(r.u)}</td><td style="${tdS}text-align:right;">${rs}</td><td style="${tdS}text-align:right;">${r.q||'-'}</td><td style="${tdS}text-align:right;font-weight:bold;">${amt}</td></tr>`;
    text += `${r.d} | ${r.u} | ${rs} x ${r.q||'-'} = ${amt}\\n`;
  });
  if(OL.note){ h += `<tr><td colspan="5" style="${tdS}font-style:italic;color:#6b7280;font-size:12px;">${escHtml(OL.note)}</td></tr>`; text += OL.note+'\\n'; }
""" + h[b:]

# ---- gate + permissions
rep("function enterApp(email){\n  S.user = email.trim().toLowerCase();",
"""function teamOf(e){ return (DATA.team||[]).find(x => x.email === (e||'').trim().toLowerCase()); }
function canDash(e){ const t = teamOf(e); return (DATA.team||[]).length ? !!(t && t.dash) : true; }
function enterApp(email){
  const t = teamOf(email);
  if(t && t.active === false){ $('gate').classList.remove('hidden'); $('gate-err').textContent = 'Access for this email has been disabled. Contact the administrator.'; try{ localStorage.removeItem('sasco_user'); }catch(e){} return false; }
  S.user = email.trim().toLowerCase();
  $('nav-dash').classList.toggle('hidden', !canDash(S.user));
  if(!canDash(S.user)) showView('quote');""")
rep("  refreshQuoteNo();\n}\nfunction initGate(){", "  refreshQuoteNo();\n  return true;\n}\nfunction initGate(){")
rep("    $('gate-err').textContent = '';\n    enterApp(v);", "    $('gate-err').textContent = '';\n    enterApp(v);")
rep("  if(v==='dash') loadDash();", "  if(v==='dash') loadDash();")
rep("function showView(v){\n", "function showView(v){\n  if(v==='dash' && S.user && !canDash(S.user)) v = 'quote';\n")
open(P, 'w', encoding='utf-8').write(h)
print('ok', len(h))
