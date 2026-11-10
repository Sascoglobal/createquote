import base64, os, sys
src, tpl, out = sys.argv[1], sys.argv[2], sys.argv[3]
html = open(tpl, encoding="utf-8").read()
data = open(src, encoding="utf-8").read()
PH = "/*__DATA__*/{charges:[],terms:[],matrix:{},settings:{},team:[],fx:{rates:{AED:1},names:{},fee:0}}"
assert PH in html
html = html.replace(PH, data.replace("</", "<\\/"))
logo = next((p for p in ("logo.png", "logo.jpg", "logo.jpeg") if os.path.exists(p)), None)
uri, ratio = "", "1"
if logo:
    from PIL import Image
    im = Image.open(logo); ratio = "%.4f" % (im.width / im.height)
    mime = "image/png" if logo.endswith("png") else "image/jpeg"
    uri = "data:%s;base64,%s" % (mime, base64.b64encode(open(logo, "rb").read()).decode())
html = html.replace("'/*__LOGO__*/'", "'%s'" % uri).replace("/*__LOGORATIO__*/1", ratio)
open(out, "w", encoding="utf-8").write(html)
print("wrote", out, len(html), "logo:", logo)
