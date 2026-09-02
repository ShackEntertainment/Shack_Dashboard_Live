"""
SHACK ENTERTAINMENT — shack_render_mcp.py
Draft-layer renderer: turns the approved brief into real PNG drafts via Pillow.
Writes to 03_Drafts only. Approval is the MD's act.
"""
import os
from PIL import Image, ImageDraw, ImageFont
from mcp.server.fastmcp import FastMCP

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
STOCK = os.path.join(project_root, 'assets', 'stock')
LOGOS = os.path.join(project_root, 'assets', 'Shack_Logos')
DRAFTS = os.path.join(project_root, '03_Drafts')
os.makedirs(DRAFTS, exist_ok=True)

NAVY = (20, 38, 63); GREY = (85, 85, 85); PAPER = (245, 246, 248)
FB = 'C:\\Windows\\Fonts\\arialbd.ttf'
FR = 'C:\\Windows\\Fonts\\arial.ttf'
LANE = 'ARTISTS UNLIMITED  ·  THE LIVE EXCHANGE  ·  SHACK NEWS NETWORK'
FOOT = ('Shack Entertainment Limited · Company No. 14628241 · '
        '25 Fielding Avenue, Twickenham, England TW2 5LX')

mcp = FastMCP('ShackRender')

def F(size, bold=True):
    return ImageFont.truetype(FB if bold else FR, size)

def atmosphere(size, crop, opacity):
    img = Image.open(os.path.join(STOCK, 'jazz_night_01.jpg')).convert('RGB')
    w, h = img.size
    if crop == 'right':
        img = img.crop((int(w * 0.47), 0, w, h))
    elif crop == 'left':
        img = img.crop((0, 0, int(w * 0.40), h))
    img = img.resize(size)
    return Image.blend(Image.new('RGB', size, PAPER), img, opacity)

def center(d, y, text, font, fill, W):
    x = (W - d.textlength(text, font=font)) / 2
    d.text((x, y), text, font=font, fill=fill)

def mark(canvas, height, y):
    p = os.path.join(LOGOS, 'live_exchange_trans.png')
    if not os.path.exists(p):
        return
    m = Image.open(p).convert('RGBA')
    r = height / m.height
    m = m.resize((int(m.width * r), height))
    canvas.paste(m, ((canvas.width - m.width) // 2, y), m)

@mcp.tool()
def render_le_poster(crop: str = 'right', opacity: float = 0.35) -> str:
    """Render LE event poster drafts (A3 + social) from the approved brief into 03_Drafts."""
    out = []
    W, H = 2480, 1754
    c = atmosphere((W, H), crop, opacity).convert('RGBA')
    d = ImageDraw.Draw(c)
    center(d, 170, 'LIVE EXCHANGE', F(170), NAVY, W)
    center(d, 400, 'EVENT POSTER | TUESDAY 30 OCT 2026 | 8PM', F(64, False), GREY, W)
    mark(c, 520, H - 780)
    center(d, H - 210, LANE, F(40, False), GREY, W)
    center(d, H - 140, FOOT, F(36, False), GREY, W)
    p1 = os.path.join(DRAFTS, 'LE_poster_A3_draft.png')
    c.convert('RGB').save(p1)
    out.append(p1)
    W, H = 1080, 1350
    c = atmosphere((W, H), crop, opacity).convert('RGBA')
    d = ImageDraw.Draw(c)
    center(d, 120, 'LIVE EXCHANGE', F(92), NAVY, W)
    center(d, 260, 'EVENT POSTER | TUESDAY 30 OCT 2026 | 8PM', F(30, False), GREY, W)
    mark(c, 300, H - 560)
    center(d, H - 170, LANE, F(22, False), GREY, W)
    center(d, H - 120, FOOT, F(20, False), GREY, W)
    p2 = os.path.join(DRAFTS, 'LE_poster_social_draft.png')
    c.convert('RGB').save(p2)
    out.append(p2)
    return 'Drafts banked: ' + ' | '.join(out) + ' — awaiting Bola approval'

if __name__ == '__main__':
    mcp.run()