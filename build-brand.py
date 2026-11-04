"""Build the B4 identity from Bezier curves and outlined Cyrillic glyphs.

Run manually after changing the identity: python build-brand.py
Requires fontTools; the normal site build uses the committed SVG masters.
"""
from pathlib import Path
from html import escape
import hashlib
import json
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'assets/brand'
OUT.mkdir(exist_ok=True)
INK, PAPER, ACCENT = '#22262B', '#FAF7F2', '#A3472B'

# Three independently drawn, closed level sets; no automatic bitmap tracing.
CONTOURS = [
    'M 72,10 C 55,7 47,19 37,32 C 28,44 14,48 8,62 '
    'C 1,79 14,90 32,96 C 49,102 71,119 89,118 '
    'C 108,119 119,105 115,88 C 112,74 106,64 106,49 '
    'C 106,30 89,13 72,10 Z',
    'M 73,34 C 60,30 52,42 44,50 C 36,58 24,60 23,71 '
    'C 22,81 36,84 48,88 C 62,93 78,103 91,101 '
    'C 105,99 100,86 96,74 C 91,61 86,38 73,34 Z',
    'M 69,54 C 61,51 55,59 49,63 C 42,67 38,70 42,76 '
    'C 45,80 56,80 65,83 C 74,86 85,91 86,81 '
    'C 86,73 77,57 69,54 Z',
]
# The point lies exactly on the top-right cubic of the outer contour.
def cubic(a, b, c, d, t):
    return (1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*d
POINT = [cubic(106,106,89,72,.42), cubic(49,30,13,10,.42)]

def mark(ink=INK, accent=ACCENT, small=False):
    paths = [CONTOURS[0], CONTOURS[2]] if small else CONTOURS
    stroke = 7.2 if small else 4.5
    return (f'<g fill="none" stroke="{ink}" stroke-width="{stroke}" '
            'stroke-linecap="round" stroke-linejoin="round">' +
            ''.join(f'<path d="{p}"/>' for p in paths) + '</g>' +
            f'<circle cx="{POINT[0]:.4f}" cy="{POINT[1]:.4f}" '
            f'r="{8 if small else 6.4}" fill="{accent}"/>')

def svg(body, width, height, title, description):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{escape(title)}</title>\n'
            f'<desc id="desc">{escape(description)}</desc>\n{body}\n</svg>\n')

FONT = ROOT / 'assets/fonts/EB-Garamond-Bold.ttf'
FACE = TTFont(FONT)
GLYPHS = FACE.getGlyphSet()
CMAP = FACE.getBestCmap()
UNITS = FACE['head'].unitsPerEm
KERN = {'Ту':-68, 'ул':-7, 'ло':-15, 'ом':-9, 'ма':-12}

def outlines(text, font, size, x, baseline, color=INK, x_stretch=1):
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    scale = size / font['head'].unitsPerEm
    offset, paths = 0, []
    for i, char in enumerate(text):
        if i and font is FACE:
            offset += KERN.get(text[i-1:i+1], 0)
        name = cmap[ord(char)]
        pen = SVGPathPen(glyphs, ntos=lambda v: format(v,'.4f').rstrip('0').rstrip('.') if v else '0')
        transformed = TransformPen(pen,(scale*x_stretch,0,0,-scale,
                                       x+offset*scale*x_stretch,baseline))
        glyphs[name].draw(transformed)
        d = pen.getCommands()
        if d:
            paths.append(f'<path d="{d}"/>')
        offset += font['hmtx'][name][0]
    return f'<g fill="{color}">' + ''.join(paths) + '</g>', offset*scale*x_stretch

def logo(ink=INK, accent=ACCENT):
    word, advance = outlines('Тулома', FACE, 140, 145, 113, ink, 1.035)
    return f'<g transform="translate(6 16) scale(.9)">{mark(ink,accent)}</g>'+word, round(145+advance+10)

body, WIDTH = logo()
DESCRIPTION = 'Три замкнутые изолинии, опорная точка и надпись «Тулома», набранная кривыми.'
for filename, a, b in [('tuloma-logo.svg',INK,ACCENT),
                       ('tuloma-logo-ink.svg',INK,INK),
                       ('tuloma-logo-reverse.svg',PAPER,PAPER)]:
    content,_ = logo(a,b)
    (OUT/filename).write_text(svg(content,WIDTH,164,'Тулома',DESCRIPTION))

for filename, a, b, micro in [('tuloma-mark.svg',INK,ACCENT,False),
                             ('tuloma-mark-ink.svg',INK,INK,False),
                             ('tuloma-mark-reverse.svg',PAPER,PAPER,False),
                             ('tuloma-mark-small.svg',INK,ACCENT,True)]:
    (OUT/filename).write_text(svg(mark(a,b,micro),128,128,'Знак Туломы',DESCRIPTION))

word,advance = outlines('Тулома',FACE,140,6,113,INK,1.035)
(OUT/'tuloma-wordmark.svg').write_text(svg(word,round(advance+16),164,'Тулома','Векторная надпись; все буквы переведены в кривые.'))

# Portable full signature: both descriptor lines are also genuine outlines.
descriptor_font = TTFont(ROOT/'assets/fonts/PT-Serif.ttf')
full = f'<g transform="translate(32 22) scale(1.45)">{body}</g>'
for text,y in [('Авторский интерактивный журнал',303),
               ('о математике геопространственных вычислений',347)]:
    line,_ = outlines(text,descriptor_font,30,32,y)
    full += line
(OUT/'tuloma-signature.svg').write_text(svg(full,1000,390,'Тулома — авторский интерактивный журнал',
    'Авторский интерактивный журнал о математике геопространственных вычислений. Вся композиция в кривых.'))

social = '<rect width="1200" height="630" fill="'+PAPER+'"/>'
social += f'<g transform="translate(74 115) scale(1.65)">{body}</g>'
for text,y,size in [('Геометрия · Карты · Алгоритмы',72,23),
                    ('Авторский интерактивный журнал',462,28),
                    ('о математике геопространственных вычислений',504,28)]:
    line,_=outlines(text,descriptor_font,size,80,y)
    social+=line
social+='<path d="M80 554H1120" stroke="#DED9CE"/>'
(OUT/'tuloma-social.svg').write_text(svg(social,1200,630,'Тулома — геометрия, карты и алгоритмы','Карточка журнала для ссылок.'))

styles = '<style>:root{--ink:#22262B;--paper:#FAF7F2;--point:#A3472B}@media(prefers-color-scheme:dark){:root{--ink:#FAF7F2;--paper:#22262B;--point:#E5AE8E}}</style>'
favicon = styles + '<rect width="128" height="128" rx="24" fill="var(--paper)"/>' + mark('var(--ink)','var(--point)',True)
(OUT/'favicon.svg').write_text(svg(favicon,128,128,'Тулома','Упрощённый знак для малых размеров.'))
static_icon = '<rect width="128" height="128" rx="24" fill="'+PAPER+'"/>'+mark(INK,ACCENT,True)
(OUT/'favicon-static.svg').write_text(svg(static_icon,128,128,'Тулома','Малая иконка на светлой подложке.'))
touch = '<rect width="180" height="180" rx="32" fill="'+PAPER+'"/><g transform="translate(26 26)">'+mark()+'</g>'
(OUT/'apple-touch.svg').write_text(svg(touch,180,180,'Тулома','Знак для иконки приложения.'))

# An actual vector proof, shared with the downloadable identity kit.
proof = '<rect width="1200" height="760" fill="'+PAPER+'"/>'
proof += '<text x="52" y="49" font-family="serif" font-size="20" fill="'+INK+'">Тулома / B4 / векторный оригинал</text>'
proof += f'<g transform="translate(100 80) scale(1.6)">{body}</g>'
proof += '<path d="M52 400H1148" stroke="#DED9CE"/>'
proof += f'<g transform="translate(85 460) scale(1.4)">{mark()}</g>'
proof += f'<g transform="translate(330 520) scale(.5)">{mark()}</g>'
proof += '<rect x="470" y="452" width="678" height="213" fill="'+INK+'"/>'
reverse,_=logo(PAPER,PAPER)
proof += f'<g transform="translate(500 480) scale(.98)">{reverse}</g>'
(OUT/'tuloma-b4-proof.svg').write_text(svg(proof,1200,760,'Тулома — векторная айдентика B4','Цветной, компактный и монохромный варианты.'))

metadata = {
    'name':'Тулома', 'direction':'B4 — Контурное поле',
    'descriptor':'Авторский интерактивный журнал о математике геопространственных вычислений.',
    'category':'Авторский научно-познавательный журнал',
    'palette':{'ink':INK,'paper':PAPER,'accent':ACCENT},
    'wordmark':{'family':'EB Garamond','weight':700,'horizontal_scale':1.035,
                'pair_adjustments_font_units':KERN,'font_sha256':hashlib.sha256(FONT.read_bytes()).hexdigest()},
    'contours':CONTOURS,'point':POINT,'stroke':4.5,
    'construction':'Hand-drawn Bezier level sets; glyph outlines. No embedded raster images or external fonts.',
    'font_source':'https://github.com/google/fonts/tree/main/ofl/ebgaramond',
}
(OUT/'master.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
print(f'Built B4 masters: {WIDTH} × 164; all logo lettering is outlined.')
