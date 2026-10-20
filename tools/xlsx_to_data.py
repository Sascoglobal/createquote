"""Reads Sasco_Quote_Templates.xlsx and writes data.json for the quote generator."""
import json, sys
from openpyxl import load_workbook

src = sys.argv[1]
out = sys.argv[2]
wb = load_workbook(src, data_only=True)


def s(v):
    return "" if v is None else str(v).strip()


def num(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


charges = []
for r in wb["Charges"].iter_rows(min_row=2, values_only=True):
    if not r[0] or not s(r[9]):
        continue
    charges.append({
        "id": s(r[0]), "mode": s(r[1]) or "ALL", "dir": s(r[2]) or "ALL", "load": s(r[3]) or "ALL",
        "nature": s(r[4]) or "ALL", "ctype": s(r[5]) or "ALL", "inco": s(r[6]) or "ALL",
        "cat": s(r[7]) or "OTHER", "sec": s(r[8]), "d": s(r[9]), "u": s(r[10]),
        "r": num(r[11]), "q": num(r[12]) if num(r[12]) is not None else 0,
        "rc": s(r[13]) or "Editable", "on": s(r[14]) or "N", "vat": s(r[15]) or "Y", "rem": s(r[16]),
    })

terms = []
for r in wb["Terms"].iter_rows(min_row=2, values_only=True):
    if not r[0] or not s(r[4]):
        continue
    terms.append({
        "id": s(r[0]), "layer": s(r[1]), "key": s(r[2]) or "ALL", "mode": s(r[3]) or "ALL",
        "text": s(r[4]), "on": s(r[5]) != "N", "untick": s(r[6]) != "N",
    })

matrix = {}
cats = ["ORIGIN", "FREIGHT", "INSURANCE", "DESTINATION", "CUSTOMS", "DELIVERY"]
for r in wb["Incoterm_Matrix"].iter_rows(min_row=5, values_only=True):
    if not r[0] or r[1] not in ("Import", "Export"):
        continue
    matrix.setdefault(s(r[0]), {})[s(r[1])] = {c: (s(r[3 + i]) or "Y") for i, c in enumerate(cats)}

keymap = {
    "Company name": "company_name", "Company email": "company_email",
    "Address (printed in PDF header)": "address", "Phone (printed in PDF header)": "phone",
    "Website": "website", "Company TRN (VAT registration no.)": "trn",
    "Quote number prefix": "quote_prefix", "Default validity (days)": "validity_days",
    "Default currency": "currency", "Default VAT rate": "vat_rate",
    "Default payment terms line": "payment_terms", "Email subject format": "email_subject",
    "Email greeting": "email_greeting", "Email opening line": "email_open",
    "Email closing line": "email_close", "Email signature": "email_sig",
    "Bank details printed on quote? (Y/N)": "bank_print",
    "Bank - beneficiary / bank / IBAN / SWIFT": "bank_details",
}
settings = {}
for r in wb["Settings"].iter_rows(min_row=4, values_only=True):
    if r[0] in keymap:
        settings[keymap[r[0]]] = r[1] if r[1] is not None else ""

team = []
for r in wb["Sales_Team"].iter_rows(min_row=2, values_only=True):
    if r[1] and "@" in s(r[1]):
        team.append({"name": s(r[0]), "email": s(r[1]).lower(), "role": s(r[2]), "active": s(r[3]) != "N"})

json.dump({"charges": charges, "terms": terms, "matrix": matrix, "settings": settings, "team": team},
          open(out, "w"), ensure_ascii=False)
print(len(charges), "charges,", len(terms), "terms,", len(matrix), "incoterms,", len(team), "team")
