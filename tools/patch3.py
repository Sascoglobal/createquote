P='index.template.html'; h=open(P,encoding='utf-8').read()
a=h.index("  const tdS = 'padding:5px 8px;border:1px solid #d7dee8;font-size:13px;';")
b=h.index("  h += `<p>${escHtml(close)}</p>")
new = r"""  // Plain, paste-safe layout: one line per item ("Description: CUR amount"). No tables, so Outlook/Gmail keep it tidy.
  const P = 'margin:0 0 3px 0;';
  const line = (l, v, b) => `<p style="${P}">${escHtml(l)}: ${b?'<b>':''}${escHtml(v)}${b?'</b>':''}</p>`;
  let h = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#1a202c;">`;
  h += `<p style="margin:0 0 10px 0;">${escHtml(greet)}</p><p style="margin:0 0 10px 0;">${escHtml(open)}</p>`;
  let text = greet+'\n\n'+open+'\n\n';
  info.forEach(i => { h += line(i[0], i[1], false); text += i[0]+': '+i[1]+'\n'; });
  h += `<p style="margin:12px 0 4px 0;"><b>Charges</b></p>`; text += '\nCHARGES\n';
  const OL = outputLines();
  OL.lines.forEach(r => {
    const cc = r.ccy || cur;
    const amt = r.amt ? cc+' '+money(r.amt) : (r.act ? 'At actuals' : '-');
    let d = r.d;
    if(!r.allin && !r.pct && r.q && r.q!==1 && r.rate) d += ' ('+r.q+' x '+cc+' '+money(r.rate)+')';
    if(r.pct && r.rate) d += ' ('+rateStr(r)+')';
    if(r.rem) d += ' - '+r.rem;
    h += line(d, amt, true); text += d+': '+amt+'\n';
  });
  if(OL.note){ h += `<p style="${P}font-style:italic;color:#6b7280;font-size:12px;">${escHtml(OL.note)}</p>`; text += OL.note+'\n'; }
  h += `<p style="margin:10px 0 3px 0;">&nbsp;</p>`; text += '\n';
  const tot = [['Subtotal', C.sub]];
  if(C.disc>0) tot.push(['Discount', -C.disc]);
  tot.push([`VAT (${Math.round(S.vatRate*10000)/100}%)`, C.vat], ['TOTAL', C.grand]);
  tot.forEach((t,i) => {
    const v = (t[1]<0?'- ':'')+cur+' '+money(Math.abs(t[1])), last = i===tot.length-1;
    h += `<p style="${P}${last?'font-size:14px;':''}">${last?'<b>':''}${t[0]}: ${last?'':'<b>'}${v}</b></p>`;
    text += `${t[0]}: ${v}\n`;
  });
  const notes = gv('f-notes').trim();
  if(notes){ h += `<p style="margin:10px 0 0 0;"><b>Notes:</b> ${escHtml(notes).replace(/\n/g,'<br>')}</p>`; text += '\nNotes: '+notes+'\n'; }
  const tcs = S.terms.filter(t => t.on && t.text && t.text.trim());
  if(tcs.length){
    h += `<p style="margin:12px 0 4px 0;"><b>Terms &amp; Conditions</b></p>` + tcs.map((t,i) => `<p style="${P}font-size:12px;color:#374151;">${i+1}. ${escHtml(t.text)}</p>`).join('');
    text += '\nTERMS & CONDITIONS\n' + tcs.map((t,i) => (i+1)+'. '+t.text).join('\n') + '\n';
  }
"""
h=h[:a]+new+h[b:]
# the old code declared `let h`/`let text` before tdS? ensure no duplicates
import re
print(h.count("let h = `<div style=\"font-family"), h.count("let text ="))
open(P,'w',encoding='utf-8').write(h)
