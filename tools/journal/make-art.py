"""Generate a synthetic contour map for the article hero."""
from pathlib import Path
import contourpy
import numpy as np

xx, yy = np.meshgrid(np.linspace(0, 640, 220), np.linspace(0, 400, 150))
X = (xx - 355) / 175
Y = (yy - 190) / 110
R = (X + 0.38 * Y)**2 + (Y - 0.22 * X)**2
z = 16*np.exp(-R) + 4.3*np.exp(-((xx-170)/200)**2-((yy-285)/98)**2)
z += 1.9*np.exp(-((xx-565)/80)**2-((yy-45)/120)**2)
z += 0.65*np.cos(xx/47 + yy/73)*np.exp(-R/3)
cg = contourpy.contour_generator(x=xx[0], y=yy[:,0], z=z)

def path(points):
    return "M" + " ".join(f"{x:.1f},{y:.1f}" for x,y in points)

major = []
minor = []
for i, level in enumerate(np.arange(0.75, 16.0, 0.65)):
    for points in cg.lines(level):
        if len(points) > 2:
            (major if i % 5 == 0 else minor).append(f'<path d="{path(points)}"/>')

svg = f'''<svg viewBox="0 0 640 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="map-title map-desc">
  <title id="map-title">Горизонтали условного холма</title>
  <desc id="map-desc">Красная линия между точками А и Б пересекает систему замкнутых горизонталей.</desc>
  <defs><pattern id="map-grid" width="39" height="39" patternUnits="userSpaceOnUse"><path d="M39 0H0V39" fill="none" stroke="var(--map-line)" stroke-opacity=".21"/></pattern></defs>
  <rect width="640" height="400" fill="var(--map-bg)"/>
  <rect width="640" height="400" fill="url(#map-grid)"/>
  <g fill="none" stroke="var(--map-line)" stroke-width="1.0" opacity=".55">{''.join(minor)}</g>
  <g fill="none" stroke="var(--map-line)" stroke-width="1.45" opacity=".9">{''.join(major)}</g>
  <path d="M83 265L550 124" stroke="var(--map-bg)" stroke-width="5" stroke-dasharray="6 6"/>
  <path d="M83 265L550 124" stroke="var(--accent)" stroke-width="2.4" stroke-dasharray="6 6"/>
  <g stroke="var(--map-bg)" stroke-width="2.5"><circle cx="83" cy="265" r="6.5" fill="var(--map-ink)"/><circle cx="550" cy="124" r="6.5" fill="var(--accent)"/></g>
  <g font-family="var(--mono)" font-weight="600" font-size="16" fill="var(--map-ink)" paint-order="stroke" stroke="var(--map-bg)" stroke-width="4"><text x="66" y="252">A</text><text x="559" y="122">B</text></g>
  <g transform="translate(588 48)" stroke="var(--map-ink)" stroke-width="1.1" fill="none"><path d="M0 26V0m-4 7 4-7 4 7"/><text x="0" y="-7" text-anchor="middle" fill="var(--map-ink)" stroke="none" font-size="10" font-family="var(--mono)">С</text></g>
  <g transform="translate(31 362)" fill="var(--map-ink)" font-family="var(--mono)" font-size="10" letter-spacing="1.7"><text y="0">СХЕМА РЕЛЬЕФА</text><text y="15" opacity=".75">УСЛОВНЫЕ ГОРИЗОНТАЛИ</text></g>
</svg>'''
Path('assets/hero.svg').write_text(svg)
