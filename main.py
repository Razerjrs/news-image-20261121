#!/usr/bin/env python3
"""news-image-20261121: sum up Saturday 21 November 2026 in one image.

Pure Python 3.13 standard library. Draws a newspaper front page with a
5x7 bitmap font and writes a deterministic PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Stories drawn (all reported on 21 Nov 2026 by reputable outlets):
  1. Russia's huge overnight attack on Ukraine; missiles land in Poland
     (AP, BBC, The Times).
  2. Wall Street rout: S&P 500 -3.7%, Nasdaq -5.3%, both in correction
     (WSJ, Investopedia, Barron's).
  3. COP31 climate talks in Antalya run into overtime; draft drops
     fossil fuels (Reuters, AP).
  4. UK and EU sign biggest post-Brexit deals in Brussels (Guardian, BBC).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# Palette: newsprint cream, ink navy, accent red, gold.
CREAM = (246, 241, 227)
PAPER = (255, 253, 247)
INK = (26, 26, 26)
NAVY = (20, 38, 74)
NAVY_DARK = (13, 25, 50)
GOLD = (201, 162, 39)
RED = (179, 38, 30)
RED_DARK = (140, 28, 22)
SKY = (31, 58, 95)
SKY_LIGHT = (135, 178, 214)
GREEN = (46, 125, 50)
GREEN_LIGHT = (102, 187, 106)
ORANGE = (230, 126, 34)
YELLOW = (244, 208, 63)
WHITE = (255, 255, 255)
GREY = (120, 120, 120)
GREY_LIGHT = (220, 220, 220)
BLUE = (0, 82, 147)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, one string of 5 bits per row, top to bottom.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(img, x, y, text, scale, color):
    """Draw uppercase ASCII text at (x, y); returns width drawn."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT["?"])
        for r in range(7):
            row = glyph[r]
            for c in range(5):
                if row[c] == "1":
                    fill_rect(img, cx + c * scale, y + r * scale,
                              scale, scale, color)
        cx += 6 * scale
    return cx - x - scale


def wrap_text(text, scale, max_w):
    """Split text into lines no wider than max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
def new_image():
    buf = bytearray(W * H * 3)
    for i in range(0, len(buf), 3):
        buf[i] = CREAM[0]
        buf[i + 1] = CREAM[1]
        buf[i + 2] = CREAM[2]
    return buf


def set_px(img, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        img[i] = color[0]
        img[i + 1] = color[1]
        img[i + 2] = color[2]


def fill_rect(img, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            img[i] = color[0]
            img[i + 1] = color[1]
            img[i + 2] = color[2]


def draw_line(img, x0, y0, x1, y1, color, thick=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        fill_rect(img, x - thick // 2, y - thick // 2, thick, thick, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def fill_circle(img, cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(img, cx - dx, cy + dy, 2 * dx + 1, 1, color)


def draw_circle(img, cx, cy, r, color, thick=2):
    for a in range(0, 360):
        import math
        x = cx + int(r * math.cos(math.radians(a)))
        y = cy + int(r * math.sin(math.radians(a)))
        fill_rect(img, x - thick // 2, y - thick // 2, thick, thick, color)


def burst(img, cx, cy, r, color):
    """Explosion starburst: filled circle plus spikes."""
    fill_circle(img, cx, cy, r, color)
    for dx, dy in ((0, -1), (1, -1), (1, 0), (1, 1),
                   (0, 1), (-1, 1), (-1, 0), (-1, -1)):
        draw_line(img, cx, cy, cx + dx * (r + 14), cy + dy * (r + 14),
                  color, 3)


# ---------------------------------------------------------------- png
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(img, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw.extend(img[y * W * 3:(y + 1) * W * 3])
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- scenes
def scene_war(img, x, y, w, h):
    """Night sky over a city: missile trails and explosions."""
    fill_rect(img, x, y, w, h, SKY)
    # stars
    for sx, sy in ((30, 18), (90, 42), (150, 14), (210, 36), (280, 20),
                   (340, 44), (400, 16), (440, 40), (60, 70), (180, 64),
                   (320, 66), (410, 74)):
        fill_rect(img, x + sx, y + sy, 3, 3, WHITE)
    # missile trails (diagonal streaks with bright heads)
    for (tx, ty, ex, ey) in ((40, 20, 150, 110), (200, 8, 300, 96),
                             (330, 26, 420, 118)):
        draw_line(img, x + tx, y + ty, x + ex, y + ey, YELLOW, 3)
        fill_circle(img, x + ex, y + ey, 5, WHITE)
    # explosions over the skyline
    burst(img, x + 120, y + 118, 12, ORANGE)
    burst(img, x + 120, y + 118, 6, YELLOW)
    burst(img, x + 300, y + 128, 10, ORANGE)
    burst(img, x + 300, y + 128, 5, YELLOW)
    burst(img, x + 400, y + 110, 8, RED)
    # city skyline silhouette
    base = y + h
    for bx, bw, bh in ((0, 46, 52), (46, 34, 78), (80, 52, 44),
                       (132, 30, 66), (162, 56, 40), (218, 36, 72),
                       (254, 48, 46), (302, 34, 64), (336, 54, 42),
                       (390, 40, 58), (430, 30, 36)):
        fill_rect(img, x + bx, base - bh, bw, bh, NAVY_DARK)
    # lit windows
    for wx, wy in ((12, 138), (56, 118), (96, 146), (142, 128),
                   (176, 152), (228, 124), (268, 148), (312, 132),
                   (352, 150), (402, 140), (442, 156)):
        fill_rect(img, x + wx, y + wy, 5, 6, YELLOW)
    # small flags at the bottom corners: Ukraine (blue/yellow), Poland (white/red)
    fill_rect(img, x + 10, base - 22, 34, 9, (0, 87, 183))
    fill_rect(img, x + 10, base - 13, 34, 9, (255, 213, 0))
    fill_rect(img, x + w - 44, base - 22, 34, 9, WHITE)
    fill_rect(img, x + w - 44, base - 13, 34, 9, RED)


def scene_markets(img, x, y, w, h):
    """A stock chart plunging down, in red."""
    fill_rect(img, x, y, w, h, PAPER)
    # grid
    for gy in range(y + 24, y + h - 20, 28):
        draw_line(img, x + 16, gy, x + w - 16, gy, GREY_LIGHT, 1)
    for gx in range(x + 40, x + w - 16, 56):
        draw_line(img, gx, y + 16, gx, y + h - 24, GREY_LIGHT, 1)
    # descending zigzag chart line
    pts = [(x + 24, y + 30), (x + 80, y + 52), (x + 130, y + 44),
           (x + 190, y + 78), (x + 240, y + 70), (x + 300, y + 108),
           (x + 350, y + 100), (x + 410, y + 146), (x + 452, y + 158)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        draw_line(img, ax, ay, bx, by, RED, 5)
    # red down arrow at the end of the line
    ax, ay = pts[-1]
    draw_line(img, ax - 4, ay - 26, ax - 4, ay + 2, RED, 5)
    draw_line(img, ax - 4, ay + 2, ax - 16, ay - 10, RED, 5)
    draw_line(img, ax - 4, ay + 2, ax + 8, ay - 10, RED, 5)
    # falling bars under the line
    for bx, bh in ((60, 26), (120, 40), (180, 34), (240, 52),
                   (300, 46), (360, 64)):
        fill_rect(img, x + bx, y + h - 24 - bh, 22, bh, (232, 120, 110))


def scene_cop31(img, x, y, w, h):
    """A warming globe under a hot sun."""
    fill_rect(img, x, y, w, h, (198, 226, 240))
    # sun with rays
    sx, sy = x + w - 78, y + 42
    fill_circle(img, sx, sy, 26, ORANGE)
    fill_circle(img, sx, sy, 18, YELLOW)
    for dx, dy in ((0, -1), (1, -1), (1, 0), (1, 1),
                   (0, 1), (-1, 1), (-1, 0), (-1, -1)):
        draw_line(img, sx, sy, sx + dx * 40, sy + dy * 40, ORANGE, 4)
    # globe
    gx, gy, gr = x + 150, y + 105, 62
    fill_circle(img, gx, gy, gr, (66, 135, 200))
    fill_circle(img, gx - 22, gy - 14, 16, GREEN)
    fill_circle(img, gx + 18, gy + 10, 20, GREEN)
    fill_circle(img, gx + 26, gy - 26, 10, GREEN_LIGHT)
    fill_circle(img, gx - 30, gy + 26, 9, GREEN_LIGHT)
    draw_circle(img, gx, gy, gr, NAVY, 3)
    # thermometer on the right
    tx, ty = x + w - 156, y + 88
    fill_rect(img, tx, ty, 18, 70, WHITE)
    fill_rect(img, tx + 4, ty + 18, 10, 52, RED)
    fill_circle(img, tx + 9, ty + 70, 15, RED)
    draw_line(img, tx + 9, ty - 6, tx + 9, ty + 70, INK, 2)
    # ground
    fill_rect(img, x, y + h - 26, w, 26, GREEN)
    fill_rect(img, x, y + h - 26, w, 4, GREEN_LIGHT)


def scene_uk_eu(img, x, y, w, h):
    """Union Jack and EU flag side by side, with a gold star between."""
    fill_rect(img, x, y, w, h, PAPER)
    # flag poles
    draw_line(img, x + 78, y + 18, x + 78, y + h - 34, INK, 4)
    draw_line(img, x + w - 78, y + 18, x + w - 78, y + h - 34, INK, 4)
    # Union Jack (simplified): blue field, white diagonals, red cross
    ux, uy, uw, uh = x + 84, y + 22, 128, 84
    fill_rect(img, ux, uy, uw, uh, (0, 36, 125))
    draw_line(img, ux, uy, ux + uw, uy + uh, WHITE, 8)
    draw_line(img, ux + uw, uy, ux, uy + uh, WHITE, 8)
    draw_line(img, ux, uy, ux + uw, uy + uh, RED, 3)
    draw_line(img, ux + uw, uy, ux, uy + uh, RED, 3)
    fill_rect(img, ux + uw // 2 - 10, uy, 20, uh, WHITE)
    fill_rect(img, ux, uy + uh // 2 - 10, uw, 20, WHITE)
    fill_rect(img, ux + uw // 2 - 6, uy, 12, uh, RED)
    fill_rect(img, ux, uy + uh // 2 - 6, uw, 12, RED)
    # EU flag: blue field, ring of 12 gold stars
    ex, ey, ew, eh = x + w - 212, y + 22, 128, 84
    fill_rect(img, ex, ey, ew, eh, (0, 51, 153))
    import math
    for i in range(12):
        a = math.radians(i * 30 - 90)
        px = ex + ew // 2 + int(30 * math.cos(a))
        py = ey + eh // 2 + int(26 * math.sin(a))
        fill_circle(img, px, py, 4, YELLOW)
    # gold star burst between the flags
    burst(img, x + w // 2, y + 64, 10, GOLD)
    burst(img, x + w // 2, y + 64, 5, YELLOW)
    # ground
    fill_rect(img, x, y + h - 26, w, 26, GREEN)
    fill_rect(img, x, y + h - 26, w, 4, GREEN_LIGHT)


# ---------------------------------------------------------------- layout
PANELS = [
    ("WAR IN EUROPE", "UKRAINE UNDER FIRE",
     "400+ DRONES AND 110 MISSILES HIT UKRAINE. 8 KILLED IN KYIV. "
     "A MISSILE LANDS IN POLAND. TUSK CALLS IT A PROVOCATION.",
     scene_war),
    ("MARKETS", "WALL STREET ROUT",
     "S&P 500 -3.7%, NASDAQ -5.3% AS AI SELL-OFF DEEPENS. "
     "BOTH INDEXES NOW IN CORRECTION.",
     scene_markets),
    ("CLIMATE", "COP31 RUNS OVERTIME",
     "ANTALYA CLIMATE TALKS PASS THEIR DEADLINE WITH NO DEAL. "
     "THE DRAFT DROPS ALL MENTION OF FOSSIL FUELS.",
     scene_cop31),
    ("EUROPE", "UK AND EU RESET",
     "BIGGEST POST-BREXIT DEALS SIGNED IN BRUSSELS: FOOD TRADE, "
     "CARBON MARKETS, YOUTH MOBILITY.",
     scene_uk_eu),
]


def draw_panel(img, px, py, kicker, headline, caption, scene):
    pw, ph = 476, 400
    fill_rect(img, px, py, pw, ph, PAPER)
    # border
    for t in range(3):
        draw_line(img, px + t, py + t, px + pw - 1 - t, py + t, NAVY, 1)
        draw_line(img, px + t, py + ph - 1 - t, px + pw - 1 - t,
                  py + ph - 1 - t, NAVY, 1)
        draw_line(img, px + t, py + t, px + t, py + ph - 1 - t, NAVY, 1)
        draw_line(img, px + pw - 1 - t, py + t, px + pw - 1 - t,
                  py + ph - 1 - t, NAVY, 1)
    # scene
    scene(img, px + 8, py + 8, pw - 16, 182)
    # kicker, headline, caption
    draw_text(img, px + 16, py + 202, kicker, 2, RED)
    draw_text(img, px + 16, py + 224, headline, 4, INK)
    lines = wrap_text(caption, 2, pw - 32)
    cy = py + 264
    for line in lines:
        draw_text(img, px + 16, cy, line, 2, INK)
        cy += 17


def build():
    img = new_image()
    # masthead
    fill_rect(img, 0, 0, W, 148, NAVY)
    fill_rect(img, 0, 148, W, 4, GOLD)
    t = "THE WORLD IN ONE DAY"
    draw_text(img, (W - text_width(t, 2)) // 2, 16, t, 2, GOLD)
    t = "SATURDAY 21 NOVEMBER 2026"
    draw_text(img, (W - text_width(t, 5)) // 2, 48, t, 5, WHITE)
    t = "FOUR STORIES THAT DEFINED THE DAY"
    draw_text(img, (W - text_width(t, 2)) // 2, 112, t, 2, WHITE)
    # panels, 2 x 2
    positions = [(24, 168), (524, 168), (24, 588), (524, 588)]
    for (px, py), (kicker, headline, caption, scene) in zip(positions, PANELS):
        draw_panel(img, px, py, kicker, headline, caption, scene)
    # footer: sources
    t = "SOURCES: AP - BBC - REUTERS - THE TIMES - WSJ - 21 NOV 2026"
    draw_text(img, (W - text_width(t, 2)) // 2, 998, t, 2, GREY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(img, path)
    print(f"wrote {path} ({size} bytes)")


if __name__ == "__main__":
    main()
