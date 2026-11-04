"""Build all fixed teaching states from the same Python functions as the worker."""
from html import escape
from pathlib import Path
import json
import sys
import numpy as np

sys.path.insert(0, "assets")
from los import X, Z, linear_blend, line_height, profile_los

out = Path("assets/figures")
out.mkdir(exist_ok=True)

def svg(name, title, body, width=420, height=270):
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
<style>text{{font-family:Arial,sans-serif;font-size:16px;fill:#333b40}}.axis{{stroke:#b8b5ad;stroke-width:1}}.terrain{{stroke:#242b2f;stroke-width:2;fill:none}}.ray{{stroke:#2f5d8a;stroke-width:2;fill:none}}</style>
<rect width="100%" height="100%" fill="#faf7f2"/>
{body}</svg>'''
    (out/name).write_text(content)

for name, peak, label in [("hill.svg",3,"Горка: цель скрыта"),("valley.svg",-3,"Впадина: цель видна")]:
    sx=lambda x: 35+35*x
    sy=lambda z: 135-25*z
    points=f'{sx(0)},{sy(0)} {sx(5)},{sy(peak)} {sx(10)},{sy(0)}'
    svg(name,label,f'''<text x="24" y="25">{label}</text>
<polygon points="35,235 {points} 385,235" fill="#e5e0d6"/>
<polyline points="{points}" class="terrain"/>
<path d="M35 135H385" class="ray"/>
<circle cx="35" cy="135" r="4" fill="#2f5d8a"/><circle cx="385" cy="135" r="4" fill="#2f5d8a"/>
<text x="28" y="120">A</text><text x="379" y="120">B</text>
<text x="180" y="{sy(peak)-12 if peak>0 else sy(peak)+22}">(5, {peak})</text>
<text x="142" y="{190 if peak>0 else 80}">{'Луч внутри грунта' if peak>0 else 'Луч выше грунта'}</text>
<text x="25" y="260">0</text><text x="203" y="260">5</text><text x="368" y="260">10 м</text>''')

t = np.linspace(0, 1, 101)
xs = linear_blend(10., 30., t)
zs = line_height(xs, 10., 4., 30., 12.)
interpolation = [{"t":float(a), "x":float(x), "z":float(z)} for a,x,z in zip(t,xs,zs)]
proofs=[]
for title,left,right in [("Оба конца ниже нуля",-3.,-1.),("Знаки различаются",-3.,3.),("Совпадение с поверхностью",0.,0.)]:
    values=linear_blend(left,right,t)
    proofs.append({"title":title,"left":left,"right":right,"points":[
        {"u":float(u),"value":float(v),"kind":"blocked" if v>0 else "touch" if v==0 else "visible"}
        for u,v in zip(t,values)]})
worked=profile_los(0,80,diagnostics=True)
diff=worked["diagnostics"]["difference"]
points=" ".join(f'{35+4.4*x:g},{125-12*d:g}' for x,d in diff)
svg("profile-difference.svg","Разность высот в учебном примере",f'''<path d="M35 125H387" class="axis"/>
<polyline points="{points}" class="ray"/>
<text x="25" y="24">Разность d(x), м</text><text x="12" y="130">0</text>
<text x="208" y="42">+6</text><text x="25" y="251">0</text><text x="197" y="251">40</text><text x="355" y="251">80 м</text>''')
data={"interpolation":interpolation,"proofs":proofs,
      "worked":{"result":worked,"inputs":[0,80,0,0],"x":X.tolist(),"z":Z.tolist(),"source":"preset"}}
Path("assets/lesson-data.json").write_text(json.dumps(data,ensure_ascii=False,separators=(",",":"))+"\n")

svg("interpolation.svg","Линейная интерполяция: A=(10,4), B=(30,12)",'''<path d="M45 220H390M45 220V35" class="axis"/>
<path d="M60 196L370 52" class="ray"/><path d="M60 196H215V124" stroke="#b5ada0" fill="none" stroke-dasharray="4 3"/>
<circle cx="215" cy="124" r="5" fill="#a3472b"/>
<text x="48" y="182">A=(10, 4)</text><text x="265" y="38">B=(30, 12)</text>
<text x="222" y="116">t=0,5</text><text x="170" y="244">x=20; z=8</text>''')
svg("linear-difference.svg","Разность высот линейна между соседними узлами",'''<path d="M45 70H380" class="axis"/>
<text x="15" y="75">0</text><path d="M65 210L365 120" class="ray"/>
<circle cx="65" cy="210" r="4" fill="#242b2f"/><circle cx="365" cy="120" r="4" fill="#242b2f"/>
<circle cx="215" cy="165" r="5" fill="#a3472b"/>
<text x="45" y="241">d(a)=-3</text><text x="285" y="151">d(b)=-1</text>
<text x="115" y="145">d(x)=-2</text><text x="160" y="38">Разность d(x), м</text>''')

rows=[]
for n in worked["diagnostics"]["nodes"]:
    idx=n["index"]
    fmt=lambda x: f'{x:g}'.replace('.',',')
    rows.append(f'''<tr data-node="{idx}"><th scope="row"><button type="button" class="node-choice" data-node-index="{idx}" aria-pressed="false">{fmt(n['x'])}</button></th><td>{fmt(n['z'])}</td><td>{fmt(n['t'])}</td><td>{fmt(n['line_z'])}</td><td>{fmt(n['gap'])}</td></tr>''')
Path("includes/_node-inspector.md").write_text('''```{=html}
<div class="node-inspector" id="node-inspector">
<div class="lesson-controls inspector-modes" role="group" aria-label="Источник данных разбора">
<button type="button" data-trace-mode="worked" aria-pressed="true">Учебный пример</button>
<button type="button" data-trace-mode="live" aria-pressed="false">Параметры главного графика</button>
</div>
<p class="lesson-status" id="trace-source">Учебный пример: A — 0 м, B — 80 м, обе высоты — 0 м.</p>
<div class="trace-plots"><div><img src="assets/cover-profile.svg" alt="Исходный профиль и линия визирования."><svg id="trace-profile" role="img" aria-label="Профиль и выбранный узел"></svg></div><div><img src="assets/figures/profile-difference.svg" alt="Разность высот достигает +6 м при x = 40 м."><svg id="trace-difference" role="img" aria-label="Разность высот и выбранный узел"></svg></div></div>
<div class="table-scroll"><table class="trace-table"><caption>Узлы между A и B. Выберите абсциссу, чтобы рассмотреть расчёт.</caption><thead><tr><th scope="col">xᵢ, м</th><th scope="col">zᵢ, м</th><th scope="col">tᵢ</th><th scope="col">z_AB, м</th><th scope="col">dᵢ, м</th></tr></thead><tbody id="trace-rows">'''+"\n".join(rows)+'''</tbody></table></div>
<div class="lesson-controls"><button type="button" id="trace-prev">← Предыдущий узел</button><button type="button" id="trace-next">Следующий узел →</button></div>
<p class="trace-detail" id="trace-detail" role="status">Максимум +6 м достигается при x = 40 м.</p>
<p class="lesson-note">Просмотр рассчитанных узлов. NumPy вычисляет массивы целиком; кнопки выбирают строку для объяснения. Операции и значения берутся из Python.</p>
</div>
```
''')
