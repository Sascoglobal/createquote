import json, sys
src, tpl, out = sys.argv[1], sys.argv[2], sys.argv[3]
html = open(tpl, encoding="utf-8").read()
data = open(src, encoding="utf-8").read()
assert "/*__DATA__*/{charges:[],terms:[],matrix:{},settings:{},team:[],fx:{rates:{AED:1},names:{},fee:0}}" in html
html = html.replace("/*__DATA__*/{charges:[],terms:[],matrix:{},settings:{},team:[],fx:{rates:{AED:1},names:{},fee:0}}", data.replace("</", "<\\/"))
open(out, "w", encoding="utf-8").write(html)
print("wrote", out, len(html))
