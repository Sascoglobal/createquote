import re
P='index.template.html'; h=open(P,encoding='utf-8').read()
def rep(o,n):
    global h
    assert h.count(o)==1,('count',h.count(o),o[:70]); h=h.replace(o,n)

# ---- per-row billing currency
rep("""function rowCalc(r){
  if(r.pct){ const rt = num(r.r); return {rate:rt, amt:round2(rt*num(r.q)), miss:false}; }
  if(r.r==='' || r.r==null) return {rate:0, amt:0, miss:false};
  const f = fxFactor(r.ccy || S.currency, S.currency);
  if(f==null) return {rate:0, amt:0, miss:true};
  const rate = round2(num(r.r)*f);
  return {rate, amt:round2(rate*num(r.q)), miss:false};
}""","""// Each row is billed in its own currency (r.bill, default = quote currency). Totals are converted internally to the quote currency.
function billCcy(r){ return r.pct ? S.currency : (r.bill || S.currency); }
function rowCalc(r){
  const bc = billCcy(r);
  if(r.pct){ const rt = num(r.r); const a = round2(rt*num(r.q)); return {rate:rt, amt:a, amtQ:a, ccy:bc, miss:false}; }
  if(r.r==='' || r.r==null) return {rate:0, amt:0, amtQ:0, ccy:bc, miss:false};
  const f = fxFactor(r.ccy || bc, bc);          // cost currency -> billing currency (transfer charge applies here)
  const g = fxFactor(bc, S.currency, true);     // billing currency -> quote currency, for totals only
  if(f==null || g==null) return {rate:0, amt:0, amtQ:0, ccy:bc, miss:true};
  const rate = round2(num(r.r)*f), amt = round2(rate*num(r.q));
  return {rate, amt, amtQ:round2(amt*g), ccy:bc, miss:false};
}""")
rep("""function fxFactor(from, to){
  if(!from || from===to) return 1;
  const a = fxRate(from), b = fxRate(to);
  if(a==null || b==null) return null;
  return a/b*(1+(S.fx.fee||0));
}""","""function fxFactor(from, to, noFee){
  if(!from || from===to) return 1;
  const a = fxRate(from), b = fxRate(to);
  if(a==null || b==null) return null;
  return a/b*(noFee ? 1 : (1+(S.fx.fee||0)));
}""")
rep("""    const c = r.ccy || S.currency;
    if(c!==S.currency && fxRate(c)==null) out.add(c);""","""    const c = r.ccy || billCcy(r), bc = billCcy(r);
    if(c!==bc && fxRate(c)==null) out.add(c);
    if(bc!==S.currency && fxRate(bc)==null) out.add(bc);""")
rep("    const a = rowCalc(r).amt; sub += a; if(r.vat) vatBase += a;","    const a = rowCalc(r).amtQ; sub += a; if(r.vat) vatBase += a;")
# all-in uses quote-currency amounts
rep("const grp = rows.filter(inAll), priced = grp.filter(r => rowCalc(r).amt > 0), un = grp.filter(r => !(rowCalc(r).amt > 0));",
    "const grp = rows.filter(inAll), priced = grp.filter(r => rowCalc(r).amtQ > 0), un = grp.filter(r => !(rowCalc(r).amtQ > 0));")
rep("const tot = round2(priced.reduce((a,r) => a + rowCalc(r).amt, 0)), nv = priced.filter(r => r.vat).length;",
    "const tot = round2(priced.reduce((a,r) => a + rowCalc(r).amtQ, 0)), nv = priced.filter(r => r.vat).length;")
rep("lines.push({d:A.label||'All-in Charges', u:'Lump sum', rate:0, q:0, amt:tot, vat:(nv===priced.length?'Y':nv===0?'-':'Part'), rem:'', allin:true});",
    "lines.push({d:A.label||'All-in Charges', u:'Lump sum', rate:0, q:0, amt:tot, ccy:S.currency, rem:'', allin:true});")
rep("lines.push({d:r.d, u:r.u, rate:c.rate, q:num(r.q), amt:c.amt, vat:r.vat?'Y':'-', rem:r.rem||'', pct:r.pct, act:/actual/i.test(r.u||'') && !c.rate});",
    "lines.push({d:r.d, u:r.u, rate:c.rate, q:num(r.q), amt:c.amt, ccy:c.ccy, rem:r.rem||'', pct:r.pct, act:/actual/i.test(r.u||'') && !c.rate});")
# manual rate typed in billing currency
rep("else { row.r = parseFloat(el.value); row.ccy = S.currency; }","else { row.r = parseFloat(el.value); row.ccy = billCcy(row); }")
rep("""    } else row[key] = el.value;
    if(key==='r' || key==='q' || key==='on' || key==='vat'){""","""    } else if(key==='bill'){
      // switching a row's billing currency keeps the same price, converted
      const before = rowCalc(row); row.bill = (el.value===S.currency ? '' : el.value);
      if(!row.pct && row.r!=='' && !row.locked){ row.r = before.rate ? round2(before.rate*(fxFactor(before.ccy, billCcy(row), true)||1)) : row.r; row.ccy = billCcy(row); }
      renderCharges(); return;
    } else row[key] = el.value;
    if(key==='r' || key==='q' || key==='on' || key==='vat'){""")
# row HTML: currency select
rep("""        <td><input type="number" value="${rv}" placeholder""","""        <td>${row.pct ? '<span style="color:#6b7280;font-size:11px;">'+S.currency+'</span>' : curSel(row, si, ri)}</td>
        <td><input type="number" value="${rv}" placeholder""")
rep("function amtCell(row){","""function curSel(row, si, ri){
  const keys = Object.keys(S.fx.rates); if(!keys.includes(S.currency)) keys.push(S.currency);
  const cur = billCcy(row);
  return `<select data-si="${si}" data-ri="${ri}" data-key="bill" class="cur-sel">${keys.map(c => `<option value="${c}" ${c===cur?'selected':''}>${c}</option>`).join('')}</select>`;
}
function amtCell(row){""")
rep("""(c.amt ? money(c.amt) : '<span style="color:#aaa;">—</span>')) + (row.locked""","""(c.amt ? (c.ccy!==S.currency ? '<span style="color:#6b7280;font-size:10.5px;">'+c.ccy+'</span> ' : '')+money(c.amt) : '<span style="color:#aaa;">—</span>')) + (row.locked""")
rep('<th style="width:92px;" class="r" id="th-rate">Rate</th>','<th style="width:64px;">Bill in</th>\n              <th style="width:92px;" class="r" id="th-rate">Rate</th>')
rep("""$('th-rate').textContent = 'Rate ('+cur+')'; $('th-amt').textContent = 'Amount ('+cur+')';""","""$('th-rate').textContent = 'Rate'; $('th-amt').textContent = 'Amount';""")
rep('<td colspan="9">▸','<td colspan="10">▸')
rep('<td style="text-align:right;"><button class="del-btn" data-action="del-sec"','<td style="text-align:right;"><button class="del-btn" data-action="del-sec"')
rep("</style>",".cur-sel{border:1.5px solid var(--border);border-radius:6px;padding:4px 2px;font-size:12px;background:#fff;width:100%;}\n</style>")
rep("Every rate and amount prints in the quote currency only. The transfer charge is added when a line's cost currency differs.","The quote currency drives the totals. Any line can be billed in another currency (see \"Bill in\" on each row) and prints in that currency; totals are converted internally. The transfer charge is added when a line's cost currency differs from its billing currency.")
rep("const blank = () => ({d:'', u:'Per Shipment', ccy:S.currency,","const blank = () => ({d:'', u:'Per Shipment', ccy:S.currency, bill:'',")
# fix rv for rows (rate shown in billing ccy already via rowCalc.rate)
# openQuote legacy rows
rep("r.ccy = r.ccy||S.currency; }); });","r.ccy = r.ccy||S.currency; r.bill = r.bill||''; }); });")

# ---- PDF table: no VAT col; Amount last, with currency
a=h.index("  const body = [];\n  const OL = outputLines();"); b=h.index("  const tfs = Math.max(6.1, 7.8*scale)")
h=h[:a]+"""  const body = [];
  const OL = outputLines();
  const cm = (l, v) => (l.ccy||cur)+' '+money(v);
  OL.lines.forEach((l, i) => {
    body.push([i+1, pdfSafe(l.d), pdfSafe(l.u), l.allin ? '-' : (l.rate ? (l.pct ? rateStr(l) : cm(l,l.rate)) : '-'), l.q ? String(l.q) : '-',
      pdfSafe(l.rem), l.amt ? cm(l,l.amt) : (l.act ? 'At actuals' : '-')]);
  });
  if(OL.note) body.push([{content:pdfSafe(OL.note), colSpan:7, styles:{fontStyle:'italic', textColor:[90,90,90], fillColor:WHITE}}]);
"""+h[b:]
rep("head:[['#','Description of Charges','Unit','Rate ('+cur+')','Qty','Amount ('+cur+')','VAT','Remarks']],","head:[['#','Description of Charges','Unit','Rate','Qty','Remarks','Amount']],")
rep("columnStyles:{0:{halign:'center',cellWidth:6},1:{cellWidth:62},2:{cellWidth:24},3:{halign:'right',cellWidth:19},4:{halign:'right',cellWidth:11},5:{halign:'right',cellWidth:23,fontStyle:'bold'},6:{halign:'center',cellWidth:9},7:{cellWidth:'auto'}},",
    "columnStyles:{0:{halign:'center',cellWidth:6},1:{cellWidth:'auto'},2:{cellWidth:24},3:{halign:'right',cellWidth:24},4:{halign:'right',cellWidth:10},5:{cellWidth:30},6:{halign:'right',cellWidth:28,fontStyle:'bold'}},")
open(P,'w',encoding='utf-8').write(h); print('ok')
