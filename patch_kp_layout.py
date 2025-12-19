#!/usr/bin/env python3
"""Патч: новый layout для КП при 100% оплате"""

FILE = "/opt/bot-dev/services/kp_pdf_generator.py"

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Добавляем CSS для full-payment layout после .unit-details
old_css = ".unit-details {{ margin-left: 410px; }}"
new_css = """.unit-details {{ margin-left: 410px; }}

.fp-layout {{ overflow: hidden; margin-bottom: 20px; }}
.fp-image {{ float: left; width: 380px; }}
.fp-image img {{ width: 100%; display: block; }}
.fp-benefit {{ margin-left: 405px; background: linear-gradient(135deg, #DCB764 0%, #c9a654 100%); border-radius: 12px; padding: 30px; min-height: 320px; display: flex; flex-direction: column; justify-content: center; }}
.fp-benefit-title {{ font-size: 13px; font-weight: 600; color: #313D20; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 20px; opacity: 0.8; }}
.fp-benefit-old {{ font-size: 18px; color: #313D20; text-decoration: line-through; opacity: 0.6; margin-bottom: 8px; }}
.fp-benefit-badge {{ display: inline-block; background: #313D20; color: #F6F0E3; font-size: 12px; font-weight: 600; padding: 6px 12px; border-radius: 4px; margin-bottom: 15px; }}
.fp-benefit-price {{ font-size: 36px; font-weight: 700; color: #313D20; margin-bottom: 15px; line-height: 1.1; }}
.fp-benefit-saving {{ font-size: 16px; color: #313D20; }}
.fp-benefit-saving span {{ font-weight: 700; font-size: 18px; }}"""

content = content.replace(old_css, new_css)

# 2. Заменяем блок unit-body для поддержки нового layout
old_body = """<div class="unit-body">
<div class="{'unit-image-full' if full_payment else 'unit-image'}">
{"<img src='data:image/jpeg;base64," + layout_b64 + "'>" if layout_b64 else ""}
</div>
<div class="{'unit-details-full' if full_payment else 'unit-details'}">
<table class="detail-table">
<tr><td class="detail-label">Корпус</td><td class="detail-value">{bname}</td></tr>
<tr><td class="detail-label">Этаж</td><td class="detail-value">{lot["floor"]}</td></tr>
<tr><td class="detail-label">Площадь</td><td class="detail-value">{lot["area"]} м²</td></tr>
<tr><td class="detail-label">Комнат</td><td class="detail-value">{ltype}</td></tr>
<tr><td class="detail-label">Сдача</td><td class="detail-value">4 кв. 2027</td></tr>
<tr><td class="detail-label">Цена за м²</td><td class="detail-value">{fmt(ppm2)}</td></tr>
</table>
<div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee;">
<div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
<span style="color: #666; font-size: 14px;">Стоимость номера</span>
<span style="font-size: 14px; color: #666;">{fmt(lot["price"])}</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center;">
<span style="color: #313D20; font-size: 15px; font-weight: 500;">При 100% оплате <span style="color: #4a7c23;">(–5%)</span></span>
<span style="font-weight: 700; font-size: 20px; color: #4a7c23;">{fmt(int(lot["price"] * 0.95))}</span>
</div>
</div>
</div>
<div style="clear:both"></div>
</div>"""

new_body = """<div class="unit-body">
{'<div class="fp-layout"><div class="fp-image">' if full_payment else '<div class="unit-image">'}
{"<img src='data:image/jpeg;base64," + layout_b64 + "'>" if layout_b64 else ""}
</div>
{'<div class="fp-benefit"><div class="fp-benefit-title">Ваша выгода</div><div class="fp-benefit-old">' + fmt(lot["price"]) + '</div><div class="fp-benefit-badge">Скидка 5%</div><div class="fp-benefit-price">' + fmt(int(lot["price"] * 0.95)) + '</div><div class="fp-benefit-saving">Экономия: <span>' + fmt(int(lot["price"] * 0.05)) + '</span></div></div></div>' if full_payment else ''}
<div class="{'unit-details-full' if full_payment else 'unit-details'}">
<table class="detail-table">
<tr><td class="detail-label">Корпус</td><td class="detail-value">{bname}</td></tr>
<tr><td class="detail-label">Этаж</td><td class="detail-value">{lot["floor"]}</td></tr>
<tr><td class="detail-label">Площадь</td><td class="detail-value">{lot["area"]} м²</td></tr>
<tr><td class="detail-label">Комнат</td><td class="detail-value">{ltype}</td></tr>
<tr><td class="detail-label">Сдача</td><td class="detail-value">4 кв. 2027</td></tr>
<tr><td class="detail-label">Цена за м²</td><td class="detail-value">{fmt(ppm2)}</td></tr>
</table>
{'' if full_payment else '''<div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee;">
<div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
<span style="color: #666; font-size: 14px;">Стоимость номера</span>
<span style="font-size: 14px; color: #666;">''' + fmt(lot["price"]) + '''</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center;">
<span style="color: #313D20; font-size: 15px; font-weight: 500;">При 100% оплате <span style="color: #4a7c23;">(–5%)</span></span>
<span style="font-weight: 700; font-size: 20px; color: #4a7c23;">''' + fmt(int(lot["price"] * 0.95)) + '''</span>
</div>
</div>'''}
</div>
<div style="clear:both"></div>
</div>"""

content = content.replace(old_body, new_body)

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Патч применён!")
print("Перезапусти бота: systemctl restart rizalta-bot-dev")
