"""Build the editorial figure from the same example as the LOS experiment."""
from pathlib import Path
import sys

sys.path.insert(0, "assets")
from los import X, Z, profile_los

result = profile_los(0, 80)
x = lambda value: 46 + 9.2 * value
y = lambda value: 228 - 11.4 * value
trace = " ".join(f"{x(a):.2f},{y(b):.2f}" for a, b in zip(X, Z))
base = f"{x(0)},228 {trace} {x(100)},228"
a, b = result["a"], result["b"]
z_line = lambda value: a[1] + (value - a[0]) * (b[1] - a[1]) / (b[0] - a[0])

parts = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1010 265" role="img" aria-labelledby="title desc">
  <title id="title">Вершина перекрывает линию визирования</title>
  <desc id="desc">Профиль длиной 100 м. Вершина на отметке 40 м на 6 м выше отрезка между наблюдателем и целью.</desc>
  <rect width="1010" height="265" fill="white"/>''']
for value in (0, 5, 10, 15):
    parts.append(f'<path d="M46 {y(value):.2f} H966" stroke="#e9e4da"/>')
    parts.append(f'<text x="37" y="{y(value)+4:.2f}" text-anchor="end" font-size="11" fill="#5b6068">{value}</text>')
for value in (0, 20, 40, 60, 80, 100):
    parts.append(f'<path d="M{x(value)} 57 V228" stroke="#e9e4da"/>')
    parts.append(f'<text x="{x(value)}" y="247" text-anchor="middle" font-size="11" fill="#5b6068">{value}</text>')
parts += [
    '<text x="46" y="32" font-size="12" fill="#5b6068">Высота, м</text>',
    '<text x="506" y="257" text-anchor="middle" font-size="12" fill="#5b6068">Расстояние, м</text>',
    f'<polygon points="{base}" fill="#ede8dd"/>',
    f'<polyline points="{trace}" fill="none" stroke="#22262b" stroke-width="1.8" stroke-linejoin="round"/>',
    f'<path d="M{x(a[0])} {y(a[1])} L{x(b[0])} {y(b[1])}" stroke="#2f5d8a" stroke-width="1.8"/>',
]
for left, right in result["below"]:
    segment = f'M{x(left):.2f} {y(z_line(left)):.2f} L{x(right):.2f} {y(z_line(right)):.2f}'
    parts.append(f'<path d="{segment}" stroke="#fff" stroke-width="3.5"/>')
    parts.append(f'<path d="{segment}" stroke="#b0382a" stroke-dasharray="5 3" stroke-width="1.8"/>')
px, py = x(result["x_peak"]), y(result["peak_z"])
parts += [
    f'<path d="M{px} {py:.2f} V{y(z_line(result["x_peak"])):.2f}" stroke="#b0382a" stroke-dasharray="3 3"/>',
    f'<circle cx="{px}" cy="{py:.2f}" r="4" fill="white" stroke="#b0382a" stroke-width="1.5"/>',
    f'<path d="M{px+3} {py-2:.2f} L{px+29} {py-14:.2f}" stroke="#b0382a"/>',
    f'<text x="{px+34}" y="{py-13:.2f}" font-size="12" fill="#8e3224">Вершина на 6 м выше линии</text>',
    f'<circle cx="{x(a[0])}" cy="{y(a[1])}" r="5.3" fill="#2f5d8a"/>',
    f'<rect x="{x(b[0])-4.7}" y="{y(b[1])-4.7}" width="9.4" height="9.4" fill="#a3472b"/>',
    f'<text x="{x(a[0])}" y="{y(a[1])-10}" text-anchor="middle" font-size="14" fill="#2f5d8a">A</text>',
    f'<text x="{x(b[0])}" y="{y(b[1])-10}" text-anchor="middle" font-size="14" fill="#a3472b">B</text>',
    '</svg>',
]
parts[0] = parts[0].replace('viewBox=', 'font-family="Arial,sans-serif" viewBox=')
Path("assets/cover-profile.svg").write_text("\n".join(parts) + "\n")
