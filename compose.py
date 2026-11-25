#!/usr/bin/env python3
"""Build-time composer for news-image-20261125.

Draws the 1024x1024 newspaper page with PIL only (stdlib + Pillow).
Deterministic: no randomness, no network, no timestamps in the PNG.
Run from the repo root:  python3 compose.py   -> writes image.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)

INK = (18, 18, 18)
PAPER = (250, 247, 238)
RED = (158, 24, 24)
NAVY = (24, 52, 92)
GREY = (90, 86, 78)

REGION_COLORS = {
    "EUROPE": (31, 78, 121),
    "MIDDLE EAST": (139, 26, 26),
    "ASIA-PACIFIC": (14, 107, 74),
    "AMERICAS": (91, 58, 140),
    "AFRICA": (178, 106, 0),
    "CLIMATE": (46, 125, 50),
    "SPORT": (0, 96, 120),
}

# (region, headline) -- 27 grid stories; lead + 5 numbers strip = 33 total.
GRID = [
    ("EUROPE", "POLAND \u2014 NATO sends AWACS radar jet after missiles land"),
    ("EUROPE", "BRUSSELS \u2014 EU unveils 22nd sanctions package on Russia"),
    ("EUROPE", "TALLINN \u2014 Russia warns Estonia of \u201cverge of war\u201d"),
    ("EUROPE", "MOSCOW \u2014 Putin vows retaliation for refinery strikes"),
    ("EUROPE", "PARIS \u2014 Sarkozy corruption case sent to trial, April 2027"),
    ("EUROPE", "BERLIN \u2014 Most Germans oppose more military aid to Kyiv"),
    ("MIDDLE EAST", "HORMUZ \u2014 Mines hit 3 tankers east of the strait"),
    ("MIDDLE EAST", "TEHRAN \u2014 Winter gas crisis deepens; power rationed"),
    ("MIDDLE EAST", "WASHINGTON \u2014 US sanctions Iran shadow-bank networks"),
    ("MIDDLE EAST", "ADEN \u2014 Houthis push to 60 km from Yemeni capital"),
    ("MIDDLE EAST", "GAZA \u2014 Israel kills head of Hamas security service"),
    ("ASIA-PACIFIC", "JIUQUAN \u2014 Shenzhou-24 lifts off; first Pakistani in orbit"),
    ("ASIA-PACIFIC", "CANBERRA \u2014 Australia moves to fine tech giants"),
    ("ASIA-PACIFIC", "PUNJAB \u2014 BJP and Akali Dal revive alliance for 2027"),
    ("ASIA-PACIFIC", "NEW DELHI \u2014 Nepal PM Balendra Shah on state visit"),
    ("ASIA-PACIFIC", "SEOUL \u2014 Russian jets near island trigger alert"),
    ("AMERICAS", "WASHINGTON \u2014 Trump pardons turkeys; honours Giuliani"),
    ("AMERICAS", "TEXAS \u2014 Fort Hood gunman seeks execution delay"),
    ("AMERICAS", "CHICAGO \u2014 Radar fault delays flights at O\u2019Hare"),
    ("AMERICAS", "NEW YORK \u2014 Sanofi in $41bn deal to buy Insmed"),
    ("AFRICA", "DAKAR \u2014 Senegal reinstated as AFCON champions"),
    ("AFRICA", "KINSHASA \u2014 DR Congo demands local stakes from miners"),
    ("AFRICA", "DAKAR \u2014 About 175 migrants missing after boat leaves"),
    ("AFRICA", "ANTANANARIVO \u2014 Warrants sought for ex-president Rajoelina"),
    ("CLIMATE", "GENEVA \u2014 WFP: 266m face acute hunger; costs up $727m"),
    ("SPORT", "LONDON \u2014 England chase down 185 to level T20I series"),
    ("SPORT", "MUNICH \u2014 Bayern post record \u20ac988m revenue"),
]

NUMBERS = [
    ("26", "DEAD IN BANTEN\nFACTORY FIRE"),
    ("11", "HURT AS HOUTHIS\nHIT RIYADH TOWER"),
    ("700,000+", "RUSSIAN TROOPS\nDEAD, NEW ANALYSIS"),
    ("0", "CLIMATE DEALS\nAT COLLAPSED COP31"),
    ("74,746", "KILLED IN GAZA,\nWAFA TOLL"),
]


def wrap(draw, text, fnt, width):
    """Wrap text to fit width; returns list of lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, width, max_lines):
    """Wrap to at most max_lines, ellipsising the last line if needed."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and draw.textlength(lines[-1] + "\u2026", font=fnt) > width:
        lines[-1] = lines[-1][:-1].rstrip()
    lines[-1] = (lines[-1] + "\u2026").strip()
    return lines


def draw_lead_art(draw, x0, y0, x1, y1):
    """Editorial illustration: dusk sea, two ships, drone streaks, burst."""
    # Sky gradient: dusk orange -> deep navy.
    top = (232, 148, 74)
    mid = (94, 88, 130)
    bot = (22, 42, 78)
    horizon = y0 + int((y1 - y0) * 0.52)
    for y in range(y0, y1):
        if y < horizon:
            t = (y - y0) / max(1, horizon - y0)
            c = tuple(int(top[i] + (mid[i] - top[i]) * t) for i in range(3))
        else:
            t = (y - horizon) / max(1, y1 - horizon)
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * t) for i in range(3))
        draw.line([(x0, y), (x1, y)], fill=c)
    # Low sun.
    sx, sy = x0 + 70, y0 + 42
    for r, a in ((34, 90), (26, 140), (18, 200)):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 214, 130, a))
    draw.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(255, 226, 160))
    # Sea with light streaks.
    for i in range(9):
        yy = horizon + 8 + i * 9
        draw.line([(x0 + 12 + i * 7, yy), (x1 - 20 - i * 5, yy)],
                  fill=(150, 170, 205), width=2)
    # Ship 1 (cargo, left) and ship 2 (warship, right), dark silhouettes.
    def ship(bx, by, scale, warship):
        hull = [(bx, by), (bx + 150 * scale, by), (bx + 138 * scale, by - 16 * scale),
                (bx + 12 * scale, by - 16 * scale)]
        draw.polygon(hull, fill=(12, 16, 24))
        draw.rectangle([bx + 30 * scale, by - 34 * scale, bx + 62 * scale, by - 16 * scale],
                       fill=(12, 16, 24))
        if warship:
            draw.polygon([(bx + 96 * scale, by - 16 * scale), (bx + 128 * scale, by - 16 * scale),
                          (bx + 112 * scale, by - 30 * scale)], fill=(12, 16, 24))
            draw.rectangle([bx + 108 * scale, by - 46 * scale, bx + 112 * scale, by - 28 * scale],
                           fill=(12, 16, 24))
        else:
            draw.rectangle([bx + 78 * scale, by - 40 * scale, bx + 118 * scale, by - 16 * scale],
                           fill=(16, 22, 34))
    ship(x0 + 18, y1 - 52, 0.85, False)
    ship(x0 + 218, y1 - 44, 0.95, True)
    # Explosion burst above the warship.
    cx, cy = x0 + 330, y0 + 78
    for r, col in ((30, (255, 120, 40)), (20, (255, 180, 60)), (11, (255, 232, 150))):
        pts = []
        for k in range(12):
            import math
            ang = k * math.pi / 6
            rr = r if k % 2 == 0 else r * 0.55
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        draw.polygon(pts, fill=col)
    # Smoke puffs.
    for ox, oy, r in ((cx - 26, cy - 26, 12), (cx + 22, cy - 30, 10), (cx + 4, cy - 38, 13)):
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=(70, 70, 80))
    # Drone dots with dotted trails.
    for dx, dy in ((x0 + 90, y0 + 46), (x0 + 150, y0 + 30), (x0 + 262, y0 + 40)):
        for t in range(0, 46, 8):
            draw.ellipse([dx - t - 2, dy - 2, dx - t + 2, dy + 2], fill=(255, 255, 255))
        draw.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=(20, 20, 20),
                     outline=(255, 255, 255), width=1)
    # Frame.
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 28  # margin

    # ---- Masthead ----
    d.text((W // 2, 10), "THE WORLD IN ONE DAY", font=SERIF_B(44),
           fill=INK, anchor="ma")
    d.rectangle([mx, 62, W - mx, 88], fill=INK)
    d.text((W // 2, 66), "WEDNESDAY  25  NOVEMBER  2026", font=SANS_B(21),
           fill=(255, 255, 255), anchor="ma")
    d.line([(mx, 96), (W - mx, 96)], fill=INK, width=2)

    # ---- Lead banner ----
    ly0, ly1 = 104, 330
    ax0, ax1 = mx, 448
    draw_lead_art(d, ax0, ly0, ax1, ly1)
    d.text((ax0, ly1 + 4), "EDITORIAL ILLUSTRATION: DRONES OVER THE BALTIC AND THE MEDITERRANEAN",
           font=SANS(9), fill=GREY)
    tx = 468
    d.text((tx, ly0 + 2), "WAR AT SEA  \u2022  UKRAINE", font=SANS_B(15), fill=RED)
    d.text((tx, ly0 + 26), "UKRAINE HITS", font=SERIF_B(46), fill=INK)
    d.text((tx, ly0 + 76), "RUSSIAN SHIPS", font=SERIF_B(46), fill=INK)
    d.line([(tx, ly0 + 132), (W - mx, ly0 + 132)], fill=RED, width=3)
    sub = ("Zelenskiy confirms drone strikes on a Russian cargo ship in the "
           "Gulf of Finland and a warship sunk off Libya. Moscow calls it "
           "\u201cterrorism\u201d and vows consequences.")
    for i, ln in enumerate(wrap(d, sub, SANS(16), W - mx - tx)):
        d.text((tx, ly0 + 142 + i * 22), ln, font=SANS(16), fill=(40, 40, 40))
    d.text((tx, ly1 - 22), "KYIV \u2022 BENGHAZI \u2022 GULF OF FINLAND",
           font=SANS_B(12), fill=GREY)

    # ---- By the numbers ----
    ny0, ny1 = 352, 432
    d.text((mx, ny0 - 2), "BY THE NUMBERS", font=SANS_B(13), fill=RED)
    d.line([(mx + 150, ny0 + 8), (W - mx, ny0 + 8)], fill=(200, 192, 178), width=1)
    bw, gap = 184, 8
    for i, (num, lab) in enumerate(NUMBERS):
        x0 = mx + i * (bw + gap)
        d.rectangle([x0, ny0 + 16, x0 + bw, ny1], fill=(255, 255, 255),
                    outline=(200, 192, 178), width=1)
        d.text((x0 + bw // 2, ny0 + 19), num, font=SANS_B(26), fill=NAVY, anchor="ma")
        for j, ln in enumerate(lab.split("\n")):
            d.text((x0 + bw // 2, ny0 + 50 + j * 13), ln, font=SANS_B(9),
                   fill=INK, anchor="ma")

    # ---- Grid ----
    gy = 440
    d.text((mx, gy), "AROUND THE WORLD \u2014 27 MORE STORIES", font=SANS_B(13), fill=INK)
    d.text((W - mx, gy), "33 STORIES \u2022 8 REGIONS", font=SANS_B(13),
           fill=RED, anchor="ra")
    d.line([(mx, gy + 20), (W - mx, gy + 20)], fill=INK, width=2)
    cw, ch, cgx, cgy = 312, 54, 8, 4
    top = gy + 28
    for idx, (region, head) in enumerate(GRID):
        r, c = divmod(idx, 3)
        x0 = mx + c * (cw + cgx)
        y0 = top + r * (ch + cgy)
        col = REGION_COLORS[region]
        d.rectangle([x0, y0, x0 + cw, y0 + ch], fill=(255, 255, 255),
                    outline=(205, 198, 184), width=1)
        d.rectangle([x0, y0, x0 + 5, y0 + ch], fill=col)
        d.text((x0 + 12, y0 + 3), region, font=SANS_B(9), fill=col)
        lines = fit_lines(d, head, SANS_B(12), cw - 20, 2)
        for j, ln in enumerate(lines):
            d.text((x0 + 12, y0 + 16 + j * 14), ln, font=SANS_B(12), fill=INK)

    # ---- Footer ----
    fy = 1004
    d.line([(mx, fy - 6), (W - mx, fy - 6)], fill=(200, 192, 178), width=1)
    d.text((W // 2, fy), "ALL EVENTS REPORTED 24\u201325 NOVEMBER 2026  \u2022  SOURCES: REUTERS, AP, RFE/RL, UN NEWS",
           font=SANS(10), fill=GREY, anchor="ma")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
