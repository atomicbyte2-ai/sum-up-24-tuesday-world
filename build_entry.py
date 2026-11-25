#!/usr/bin/env python3
"""Build entry.png for make.fun bounty news-image-20261124.

One-page newspaper front page: Tuesday 24 November 2026 world news,
30 stories, 8 groups. Drawn entirely with Pillow shapes + text.
Renders at 2x (2048) then downscales to 1024x1024 and quantizes to a
<=256-colour palette. Deterministic: no randomness, no timestamps.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2  # render scale
W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/noto"

# ---------------------------------------------------------------- palette
PAPER = (250, 246, 236)
INK = (26, 24, 20)
INK2 = (74, 70, 62)
RED = (178, 34, 28)
RED_DK = (140, 24, 20)
GREEN = (28, 122, 66)
GREEN_BG = (226, 240, 228)
NAVY = (24, 42, 66)
NAVY2 = (36, 58, 88)
GOLD = (196, 148, 44)
LINE = (196, 186, 166)
LIGHT = (238, 231, 216)
SEA = (206, 222, 231)
LAND = (216, 203, 164)
REGION_COLORS = {
    "AMERICAS": (44, 92, 140),
    "EUROPE": (110, 66, 140),
    "MIDDLE EAST": (178, 96, 20),
    "AFRICA": (28, 122, 96),
    "ASIA": (178, 34, 28),
    "SOUTH ASIA": (190, 60, 110),
    "OCEANIA": (20, 110, 150),
    "WORLD": (90, 86, 76),
}


def F(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), int(size * S))


SERIF_BLACK = "NotoSerif-Black.ttf"
SERIF_BOLD = "NotoSerif-Bold.ttf"
SERIF = "NotoSerif-Regular.ttf"
SANS_BLACK = "NotoSans-Black.ttf"
SANS_XBOLD = "NotoSans-ExtraBold.ttf"
SANS_BOLD = "NotoSans-Bold.ttf"
SANS_SB = "NotoSans-SemiBold.ttf"
SANS = "NotoSans-Regular.ttf"
MONO_B = "NotoSansMono-Bold.ttf"
MONO_CB = "NotoSansMono-CondensedBold.ttf"


def sc(v):
    return int(v * S)


def box(d, x0, y0, x1, y1, fill=None, outline=None, width=1):
    d.rectangle([sc(x0), sc(y0), sc(x1), sc(y1)], fill=fill,
                outline=outline, width=sc(width))


def rbox(d, x0, y0, x1, y1, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle([sc(x0), sc(y0), sc(x1), sc(y1)], radius=sc(radius),
                        fill=fill, outline=outline, width=sc(width))


def text(d, x, y, s, font, fill=INK, anchor="la"):
    d.text((sc(x), sc(y)), s, font=font, fill=fill, anchor=anchor)


def tw(d, s, font):
    return d.textlength(s, font=font) / S


def spaced(d, x, y, s, font, fill=INK, spacing=1.5, anchor="la"):
    """Draw text with extra letter spacing (for small-caps labels)."""
    if anchor in ("ma", "mm"):
        total = sum(d.textlength(ch, font=font) for ch in s) / S
        total += spacing * (len(s) - 1)
        x = x - total / 2
    cx = x
    for ch in s:
        d.text((sc(cx), sc(y)), ch, font=font, fill=fill, anchor="la")
        cx += d.textlength(ch, font=font) / S + spacing
    return cx


def wrap(d, s, font, max_w):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(d, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(d, s, name, size, max_w, min_size=7):
    while size > min_size and tw(d, s, F(name, size)) > max_w:
        size -= 0.5
    return F(name, size)


def draw_lines(d, x, y, lines, font, fill=INK, leading=None, anchor="la"):
    if leading is None:
        leading = font.size / S * 1.18
    for ln in lines:
        text(d, x, y, ln, font, fill, anchor)
        y += leading
    return y


# ------------------------------------------------------------------- data
LEADS = [
    dict(num=1, region="ASIA", field="MARKETS", label="LEAD 1 - MARKETS",
         headline="ASIA'S MARKETS ROAR BACK",
         detail="Taiex 40,122; Kospi +6.3% over 5,000; Nikkei +3.9%",
         tag="CONFIRMED - Reuters, CNA", kind="chart", big="+9.0%"),
    dict(num=2, region="MIDDLE EAST", field="WAR", label="LEAD 2 - WAR",
         headline="HOUTHIS HIT RIYADH'S TALLEST TOWER AGAIN",
         detail="11 injured; 2nd strike in 5 days; PIF Tower HQ",
         tag="CONFIRMED - Reuters, WSJ", kind="tower", big="11"),
    dict(num=3, region="EUROPE", field="WAR", label="LEAD 3 - WAR",
         headline="OVERNIGHT STRIKE ON ZAPORIZHZHIA KILLS 2",
         detail="40 wounded incl. 4 children; block hit",
         tag="CONFIRMED - Gov. Semikin, Reuters", kind="block", big="2"),
]

CARDS = [
    dict(num=4, place="Jiuquan, China", region="ASIA", field="SPACE",
         headline="China names Shenzhou-24 crew; Pakistani joins Tiangong",
         detail="Tang Hongbo, Wu Yi, Zeeshan Ali",
         tag="CONFIRMED", icon="rocket", icon_text="1ST"),
    dict(num=5, place="Ulleung, S. Korea", region="ASIA", field="DEFENCE",
         headline="Russian jets trip Korean air-raid alert",
         detail="5-min alert 07:52 KST; no breach",
         tag="CONFIRMED", icon="jet", icon_text="5 MIN"),
    dict(num=6, place="Paris - New Jersey", region="EUROPE", field="BUSINESS",
         headline="Sanofi agrees $41bn cash buy of Insmed",
         detail="$175/share; biggest pharma deal",
         tag="CONFIRMED", icon="pill", icon_text="$41BN"),
    dict(num=7, place="Canberra", region="OCEANIA", field="TECH",
         headline="Australia sets tech fines up to 5% of global revenue",
         detail="Labor-Greens deal; right to sue",
         tag="CONFIRMED", icon="scale", icon_text="5%"),
    dict(num=8, place="Canberra", region="OCEANIA", field="DIPLOMACY",
         headline="Australia-Singapore leaders sign AI pact",
         detail="Supplies MOU; carbon capture",
         tag="CONFIRMED", icon="pact", icon_text="AI"),
    dict(num=9, place="Lausanne", region="AFRICA", field="SPORT",
         headline="CAS restores Senegal as AFCON champions",
         detail="1-0 win over Morocco stands",
         tag="CONFIRMED", icon="trophy", icon_text="1-0"),
    dict(num=10, place="Versailles", region="EUROPE", field="JUSTICE",
         headline="Murder trial ordered for officer who shot Nahel",
         detail="Killed 2023; up to 30 years",
         tag="CONFIRMED", icon="gavel", icon_text="30Y"),
    dict(num=11, place="Taplejung, Nepal", region="SOUTH ASIA", field="DISASTER",
         headline="Magnitude-5.3 quake jolts eastern Nepal",
         detail="01:32 UTC; felt in 5 nations",
         tag="CONFIRMED", icon="quake", icon_text="M5.3"),
    dict(num=12, place="Gaza", region="MIDDLE EAST", field="WAR",
         headline="Israeli strikes kill at least 6 in Gaza",
         detail="2 police among dead; chief killed",
         tag="CONFIRMED", icon="blast", icon_text="6"),
    dict(num=13, place="Dhaka", region="SOUTH ASIA", field="POLITICS",
         headline="Hasina plans return to Bangladesh on Dec 16",
         detail="Dhaka seeks arrest",
         tag="CONFIRMED", icon="parl", icon_text="DEC 16"),
]

BRIEFS = [
    (14, "AMERICAS", "US states sue Musk's firms over Grok sexualised images"),
    (15, "EUROPE", "Rutte: NATO will defend space after Russian nuke-satellite reports"),
    (16, "EUROPE", "Leaked Rosstat data: 500,000+ Russian soldiers dead, may pass 700,000"),
    (17, "EUROPE", "Germany first to get access to Ukraine's Delta battlefield system"),
    (18, "MIDDLE EAST", "Iraq PM orders oil ministry to run Kurdish oilfields"),
    (19, "ASIA", "China opens corruption probe into Politburo member Chen Jining"),
    (20, "OCEANIA", "Solomon Islands tells China it will end 2022 security pact"),
    (21, "ASIA", "US loses measles elimination status after 25+ years"),
    (22, "AMERICAS", "FDA approves first drug for limb-girdle muscular dystrophy"),
    (23, "AMERICAS", "Wall St cools: S&P 500 -0.95%; Trump expected to unveil tariffs on China, EU"),
    (24, "AMERICAS", "Brazil cuts 2027 growth forecast as real weakens"),
    (25, "ASIA", "Malaysia to send 6,500+ Myanmar migrants home in Dec"),
    (26, "AFRICA", "Rebels say they downed Cessna 208 near Minembwe; 2 dead, 2 held [CLAIM]"),
    (27, "MIDDLE EAST", "UN: Gaza war has undone 77 years of human development"),
    (28, "WORLD", "UN: 47,000 women killed by partners or relatives worldwide in 2025"),
    (29, "ASIA", "S. Korea offers up to $375,000 rewards to catch AI cheats in college exam"),
    (30, "EUROPE", "Putin admits strain on oil market, vows response to Ukraine strikes on oil plants"),
]

DATE_CHECK = [
    "Nvidia reinstates Huang (Mon 23)",
    "Hormuz: 3 tankers hit mines (Mon 23)",
    "Russia warns Estonia of 'open war' (Mon 23)",
    "ICJ: Myanmar committed genocide (Thu 19 Nov)",
    "Spain shelves Puigdemont case (Mon 23)",
    "COP31 ends with no deal (Sun 22)",
    "Russian corvette sunk at Benghazi (Sun 22)",
    "Miss Universe final (Wed 25 01:00 UTC)",
    "Shenzhou-24 LAUNCH (Wed 25 00:18 UTC)",
]

TIMELINE = [
    ("01:32 UTC", "Nepal quake"),
    ("06:30 UTC", "Sanofi $41bn deal"),
    ("07:52 KST", "Ulleung alert"),
    ("DAYTIME", "Riyadh tower hit"),
    ("EVENING", "CAS restores Senegal"),
]

NUMBERS = [
    ("+9.0%", "Taiex, record 40,122"),
    ("$41bn", "Sanofi-Insmed"),
    ("11", "hurt in Riyadh"),
    ("2 dead", "40 hurt, Zaporizhzhia"),
    ("M5.3", "Nepal quake"),
    ("5-min", "Ulleung alert"),
    ("6,500+", "migrants"),
    ("1-0", "Senegal"),
    ("47,000", "women killed"),
]

GROUPS = [("AMERICAS", 4), ("EUROPE", 7), ("MIDDLE EAST", 4), ("AFRICA", 2),
          ("ASIA", 8), ("SOUTH ASIA", 2), ("OCEANIA", 2), ("WORLD", 1)]

# lon/lat of story pins on the map
PINS = {
    1: (121, 23), 2: (46.7, 24.7), 3: (35.2, 47.8), 4: (98.5, 39.8),
    5: (130.9, 37.5), 6: (2.3, 48.9), 7: (149.1, -35.3), 8: (149.1, -35.3),
    9: (6.6, 46.5), 10: (2.1, 48.8), 11: (87.7, 27.6), 12: (34.5, 31.5),
    13: (90.4, 23.8),
}
PIN_DXDY = {1: (12, 0), 2: (10, -6), 4: (-12, -8), 5: (0, -12),
            6: (-18, -4), 8: (14, 0), 9: (10, -12), 10: (-8, 16),
            12: (0, 8), 13: (-10, 8)}  # nudge overlapping pins


# ------------------------------------------------------------------ icons
def draw_icon(d, x, y, size, kind, label, color):
    """Small square icon with a simple drawn glyph + short label text."""
    rbox(d, x, y, x + size, y + size, 5, fill=color)
    cx, cy = x + size / 2, y + size / 2
    w = (255, 255, 255)
    if kind == "rocket":
        d.polygon([(sc(cx), sc(y + 6)), (sc(cx + 7), sc(y + 20)),
                   (sc(cx - 7), sc(y + 20))], fill=w)
        box(d, cx - 5, y + 19, cx + 5, y + 26, fill=w)
        d.polygon([(sc(cx), sc(y + 26)), (sc(cx + 4), sc(y + 31)),
                   (sc(cx - 4), sc(y + 31))], fill=(255, 176, 66))
    elif kind == "jet":
        d.polygon([(sc(cx), sc(y + 6)), (sc(cx + 5), sc(y + 18)),
                   (sc(cx + 13), sc(y + 24)), (sc(cx + 4), sc(y + 24)),
                   (sc(cx + 2), sc(y + 29)), (sc(cx - 2), sc(y + 29)),
                   (sc(cx - 4), sc(y + 24)), (sc(cx - 13), sc(y + 24)),
                   (sc(cx - 5), sc(y + 18))], fill=w)
    elif kind == "pill":
        d.ellipse([sc(x + 5), sc(y + 11), sc(x + size - 5), sc(y + 21)],
                  fill=w)
        d.line([sc(cx), sc(y + 11), sc(cx), sc(y + 21)], fill=color,
               width=sc(2))
    elif kind == "scale":
        d.line([sc(cx), sc(y + 6), sc(cx), sc(y + 26)], fill=w, width=sc(2))
        d.line([sc(x + 7), sc(y + 10), sc(x + size - 7), sc(y + 10)],
               fill=w, width=sc(2))
        d.arc([sc(x + 5), sc(y + 18), sc(x + 14), sc(y + 27)], 0, 180, fill=w,
              width=sc(2))
        d.arc([sc(x + size - 14), sc(y + 18), sc(x + size - 5), sc(y + 27)],
              0, 180, fill=w, width=sc(2))
    elif kind == "pact":
        d.ellipse([sc(cx - 11), sc(y + 9), sc(cx - 1), sc(y + 23)], fill=w)
        d.ellipse([sc(cx + 1), sc(y + 9), sc(cx + 11), sc(y + 23)], fill=w)
    elif kind == "trophy":
        d.polygon([(sc(cx - 7), sc(y + 6)), (sc(cx + 7), sc(y + 6)),
                   (sc(cx + 5), sc(y + 18)), (sc(cx - 5), sc(y + 18))],
                  fill=w)
        box(d, cx - 2, y + 18, cx + 2, y + 24, fill=w)
        box(d, cx - 7, y + 24, cx + 7, y + 27, fill=w)
    elif kind == "gavel":
        d.rectangle([sc(cx - 9), sc(y + 7), sc(cx + 9), sc(y + 13)], fill=w)
        d.line([sc(cx + 4), sc(y + 13), sc(cx - 6), sc(y + 26)], fill=w,
               width=sc(3))
        box(d, cx - 10, y + 26, cx - 2, y + 29, fill=w)
    elif kind == "quake":
        pts = [(x + 4, y + 18), (x + 9, y + 18), (x + 12, y + 10),
               (x + 15, y + 25), (x + 18, y + 12), (x + 21, y + 20),
               (x + 24, y + 18), (x + 30, y + 18)]
        d.line([(sc(px), sc(py)) for px, py in pts], fill=w, width=sc(2),
               joint="curve")
    elif kind == "blast":
        for ang in range(0, 360, 45):
            import math
            r1, r2 = 4, 12
            a = math.radians(ang)
            d.line([sc(cx), sc(cy), sc(cx + r2 * math.cos(a)),
                    sc(cy + r2 * math.sin(a))], fill=w, width=sc(2))
        d.ellipse([sc(cx - 5), sc(cy - 5), sc(cx + 5), sc(cy + 5)], fill=w)
    elif kind == "parl":
        for i in range(3):
            box(d, x + 6 + i * 9, y + 9, x + 11 + i * 9, y + 24, fill=w)
        box(d, x + 4, y + 6, x + size - 4, y + 9, fill=w)
        box(d, x + 4, y + 24, x + size - 4, y + 27, fill=w)
    f = fit_font(d, label, SANS_BLACK, 8.5, size - 4, min_size=6)
    # label sits under the glyph
    text(d, cx, y + size - 1, label, f, fill=w, anchor="ma")


# ------------------------------------------------------- lead illustrations
def draw_lead_art(d, x, y, w, h, kind, big):
    rbox(d, x, y, x + w, y + h, 6, fill=NAVY)
    if kind == "chart":
        # rising bars + green arrow
        base = y + h - 26
        heights = [22, 38, 30, 52, 66]
        bw = 26
        gap = 12
        x0 = x + 16
        cols = [(96, 160, 110), (70, 140, 95), (120, 180, 130),
                (52, 130, 84), (28, 122, 66)]
        for i, hh in enumerate(heights):
            bx = x0 + i * (bw + gap)
            box(d, bx, base - hh, bx + bw, base, fill=cols[i])
        import math
        d.line([(sc(x0), sc(base - 24)), (sc(x0 + 4 * (bw + gap) + bw)),
                (sc(base - 72))], fill=(120, 220, 140), width=sc(5))
        d.polygon([(sc(x0 + 4 * (bw + gap) + bw - 2), sc(base - 80)),
                   (sc(x0 + 4 * (bw + gap) + bw + 12), sc(base - 72)),
                   (sc(x0 + 4 * (bw + gap) + bw - 2), sc(base - 62))],
                  fill=(120, 220, 140))
        f = F(SANS_BLACK, 44)
        text(d, x + w - 14, y + 8, big, f, fill=(255, 255, 255), anchor="ra")
        f2 = F(SANS_BOLD, 12)
        text(d, x + w - 14, y + 56, "TAIEX RECORD", f2,
             fill=(180, 220, 190), anchor="ra")
    elif kind == "tower":
        # PIF tower silhouette with impact flash near the top
        tx0, tx1 = x + w / 2 - 26, x + w / 2 + 26
        d.polygon([(sc(tx0), sc(y + h)), (sc(tx0 + 6), sc(y + 18)),
                   (sc(tx1 - 6), sc(y + 18)), (sc(tx1), sc(y + h))],
                  fill=(70, 88, 112))
        for row in range(6):
            wy = y + 30 + row * 11
            for col in range(3):
                wx = tx0 + 8 + col * 14
                box(d, wx, wy, wx + 8, wy + 5,
                    fill=(255, 214, 130) if (row + col) % 3 else (150, 170, 195))
        # skyline
        box(d, x + 12, y + h - 34, x + 52, y + h, fill=(52, 66, 88))
        box(d, x + w - 52, y + h - 26, x + w - 12, y + h, fill=(52, 66, 88))
        # impact flash
        import math
        fx, fy = tx1 + 2, y + 26
        for ang in range(0, 360, 30):
            a = math.radians(ang)
            r = 20 if ang % 60 == 0 else 12
            d.line([sc(fx), sc(fy), sc(fx + r * math.cos(a)),
                    sc(fy + r * math.sin(a))], fill=(255, 176, 66),
                   width=sc(3))
        d.ellipse([sc(fx - 8), sc(fy - 8), sc(fx + 8), sc(fy + 8)],
                  fill=(255, 214, 130))
        f = F(SANS_BLACK, 46)
        text(d, x + 16, y + 8, big, f, fill=(255, 255, 255), anchor="la")
        f2 = F(SANS_BOLD, 12)
        text(d, x + 16, y + 58, "INJURED", f2, fill=(255, 200, 160),
             anchor="la")
    elif kind == "block":
        # damaged apartment block, smoke, big numbers
        bx0, bx1 = x + 18, x + w - 70
        box(d, bx0, y + 26, bx1, y + h, fill=(96, 84, 74))
        d.polygon([(sc(bx1), sc(y + 26)), (sc(bx1), sc(y + 52)),
                   (sc(bx1 - 26), sc(y + 44)), (sc(bx1 - 12), sc(y + 62)),
                   (sc(bx1 - 30), sc(y + 56)), (sc(bx1 - 18), sc(y + 26))],
                  fill=(52, 44, 40))
        for row in range(4):
            wy = y + 34 + row * 14
            for col in range(5):
                wx = bx0 + 8 + col * 20
                if wx + 10 > bx1 - 34:
                    continue
                box(d, wx, wy, wx + 10, wy + 7,
                    fill=(255, 214, 130) if (row * 5 + col) % 4 == 0
                    else (60, 52, 46))
        # smoke puffs
        for sx, sy, sr in [(bx1 - 8, y + 18, 9), (bx1 + 6, y + 10, 7),
                           (bx1 + 16, y + 22, 6)]:
            d.ellipse([sc(sx - sr), sc(sy - sr), sc(sx + sr), sc(sy + sr)],
                      fill=(200, 196, 188))
        f = F(SANS_BLACK, 46)
        text(d, x + w - 58, y + 8, big, f, fill=(255, 255, 255), anchor="la")
        f2 = F(SANS_BOLD, 12)
        text(d, x + w - 58, y + 58, "DEAD", f2, fill=(255, 200, 160),
             anchor="la")
        f3 = F(SANS_BLACK, 22)
        text(d, x + w - 12, y + 74, "40 HURT", f3, fill=(255, 255, 255),
             anchor="ra")


# -------------------------------------------------------------------- map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 71), (-95, 80), (-80, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-145, 60), (-165, 60)],
    # Greenland
    [(-58, 64), (-40, 70), (-25, 70), (-20, 76), (-55, 80), (-60, 74)],
    # South America
    [(-80, 10), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-58, -35), (-65, -41), (-70, -52), (-73, -40), (-70, -20),
     (-80, -5), (-81, 5)],
    # Europe
    [(-10, 36), (-9, 43), (0, 46), (-2, 49), (3, 51), (8, 55), (10, 57),
     (18, 56), (21, 55), (24, 58), (30, 60), (30, 70), (20, 70), (12, 71),
     (5, 60), (-5, 58), (-10, 52)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (43, 0), (40, -10), (35, -20), (32, -28),
     (25, -34), (18, -35), (12, -18), (8, -2), (9, 4), (-8, 5), (-13, 8)],
    # Asia
    [(30, 36), (36, 36), (43, 39), (48, 38), (54, 37), (57, 26), (60, 25),
     (66, 25), (72, 20), (77, 8), (80, 13), (85, 19), (89, 22), (92, 21),
     (97, 16), (100, 8), (103, 2), (105, 9), (108, 12), (109, 15),
     (106, 20), (110, 22), (114, 22), (118, 25), (120, 28), (122, 31),
     (120, 35), (122, 38), (126, 40), (128, 38), (130, 42), (135, 44),
     (140, 46), (142, 50), (140, 55), (142, 59), (156, 52), (158, 56),
     (162, 60), (170, 66), (178, 65), (170, 60), (162, 56), (150, 60),
     (140, 62), (130, 70), (110, 74), (95, 76), (80, 73), (68, 69),
     (55, 68), (44, 68), (35, 66), (30, 62), (28, 58), (24, 55), (21, 54),
     (23, 45), (28, 44), (30, 41)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (124, -33), (129, -32), (132, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20)],
    # UK, Japan, SE Asia islands, NZ, Madagascar, New Guinea (small blobs)
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (140, 37), (141, 40),
     (141, 44), (143, 42), (140, 39), (137, 36), (133, 34), (130, 32)],
    [(95, 5), (98, 8), (100, 5), (102, 0), (100, -3), (97, -1)],
    [(110, -7), (114, -8), (114, -9), (110, -8)],
    [(141, -1), (146, -6), (150, -8), (147, -9), (141, -8)],
    [(44, -16), (47, -15), (50, -16), (49, -22), (45, -25), (43, -20)],
    [(167, -35), (170, -38), (174, -40), (178, -38), (174, -35), (168, -37)],
]


def draw_map(d, x, y, w, h):
    rbox(d, x, y, x + w, y + h, 6, fill=SEA)
    text(d, x + 10, y + 6, "WHERE IT HAPPENED - STORIES 1-13",
         F(SANS_BOLD, 10), fill=NAVY, anchor="la")
    mx0, my0 = x + 6, y + 22
    mw, mh = w - 12, h - 28
    def proj(lon, lat):
        px = mx0 + (lon + 180) / 360.0 * mw
        py = my0 + (75 - lat) / 135.0 * mh
        return (sc(px), sc(py))
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=(180, 166, 124))
    for num, (lon, lat) in PINS.items():
        dx, dy = PIN_DXDY.get(num, (0, 0))
        px = mx0 + (lon + 180) / 360.0 * mw + dx
        py = my0 + (75 - lat) / 135.0 * mh + dy
        d.ellipse([sc(px - 8), sc(py - 8), sc(px + 8), sc(py + 8)],
                  fill=RED, outline=(255, 255, 255), width=sc(1.5))
        f = F(SANS_BLACK, 9)
        text(d, px, py - 6.5, str(num), f, fill=(255, 255, 255), anchor="ma")


# ------------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (sc(W), sc(H)), PAPER)
    d = ImageDraw.Draw(img)
    M = 24           # side margin
    CW = W - 2 * M   # 976 content width

    # ---- masthead
    y = 10
    spaced(d, W / 2, y, "THE WORLD IN ONE DAY", F(SANS_BOLD, 12.5),
           fill=RED, spacing=3, anchor="ma")
    y = 28
    f_date = fit_font(d, "TUESDAY 24 NOVEMBER 2026", SERIF_BLACK, 45, CW)
    text(d, W / 2, y, "TUESDAY 24 NOVEMBER 2026", f_date, fill=INK,
         anchor="ma")
    y = 76
    f_sub = F(SANS_SB, 11.5)
    text(d, W / 2, y,
         "30 STORIES  -  8 GROUPS  -  ALL FROM THIS ONE DAY (UTC)  -  "
         "EDITION SET AFTER THE DAY ENDED",
         f_sub, fill=INK2, anchor="ma")
    box(d, M, 96, W - M, 97, fill=INK)
    box(d, M, 100, W - M, 101, fill=INK)

    # ---- timeline strip
    y = 108
    rbox(d, M, y, W - M, y + 38, 5, fill=LIGHT)
    text(d, M + 10, y + 12, "THE DAY, HOUR BY HOUR",
         F(SANS_BLACK, 10), fill=RED, anchor="la")
    tw_col = (CW - 185) / 5
    for i, (t, label) in enumerate(TIMELINE):
        cx = M + 175 + i * tw_col
        d.ellipse([sc(cx), sc(y + 15), sc(cx + 7), sc(y + 22)], fill=RED)
        text(d, cx + 11, y + 3, t, F(SANS_BLACK, 10.5), fill=INK, anchor="la")
        text(d, cx + 11, y + 19, label, F(SANS, 10), fill=INK2, anchor="la")

    # ---- group chips
    y = 152
    chip_f = F(SANS_BLACK, 10.5)
    total_text = 0
    widths = []
    for name, n in GROUPS:
        s = "%s %d" % (name, n)
        wdt = tw(d, s, chip_f) + 18
        widths.append(wdt)
        total_text += wdt
    gap = (CW - total_text) / (len(GROUPS) - 1)
    cx = M
    for (name, n), wdt in zip(GROUPS, widths):
        rbox(d, cx, y, cx + wdt, y + 24, 12,
             fill=REGION_COLORS[name])
        text(d, cx + wdt / 2, y + 5.5, "%s %d" % (name, n), chip_f,
             fill=(255, 255, 255), anchor="ma")
        cx += wdt + gap

    # ---- numbers strip
    y = 184
    text(d, M, y, "THE DAY IN NUMBERS", F(SANS_BLACK, 10.5), fill=RED,
         anchor="la")
    y = 198
    cell = CW / 9
    for i, (num, lab) in enumerate(NUMBERS):
        cx = M + i * cell
        if i:
            d.line([sc(cx), sc(y + 2), sc(cx), sc(y + 28)], fill=LINE,
                   width=sc(1))
        f_n = fit_font(d, num, SANS_BLACK, 15, cell - 8, min_size=10)
        text(d, cx + cell / 2, y, num, f_n, fill=INK, anchor="ma")
        f_l = fit_font(d, lab, SANS, 8.5, cell - 6, min_size=7)
        text(d, cx + cell / 2, y + 17, lab, f_l, fill=INK2, anchor="ma")

    # ---- lead panels
    y = 232
    lead_h = 196
    lead_w = (CW - 2 * 10) / 3
    art_h = 100
    for i, lead in enumerate(LEADS):
        x0 = M + i * (lead_w + 10)
        rbox(d, x0, y, x0 + lead_w, y + lead_h, 5, fill=(255, 255, 255),
             outline=LINE, width=1)
        draw_lead_art(d, x0 + 5, y + 5, lead_w - 10, art_h, lead["kind"],
                      lead["big"])
        # red label banner
        by = y + 5 + art_h + 5
        box(d, x0 + 5, by, x0 + lead_w - 5, by + 17, fill=RED)
        text(d, x0 + 10, by + 3, lead["label"], F(SANS_BLACK, 9.5),
             fill=(255, 255, 255), anchor="la")
        f_h = F(SANS_BLACK, 16.5)
        lines = wrap(d, lead["headline"], f_h, lead_w - 20)
        hy = by + 22
        draw_lines(d, x0 + 10, hy, lines[:2], f_h, fill=INK, leading=18)
        dy = hy + 2 * 18 + 2
        f_dt = F(SANS, 11)
        dlines = wrap(d, lead["detail"], f_dt, lead_w - 20)
        draw_lines(d, x0 + 10, dy, dlines[:1], f_dt, fill=INK2, leading=13.5)
        ty = y + lead_h - 13
        text(d, x0 + 10, ty, lead["tag"], F(SANS_BOLD, 9), fill=GREEN,
             anchor="la")

    # ---- cards grid (5 x 2)
    y = 436
    card_w = (CW - 4 * 8) / 5
    card_h = 98
    for idx, card in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x0 = M + col * (card_w + 8)
        y0 = y + row * (card_h + 6)
        rbox(d, x0, y0, x0 + card_w, y0 + card_h, 5,
             fill=(255, 255, 255), outline=LINE, width=1)
        # number badge + icon
        rbox(d, x0 + 6, y0 + 6, x0 + 40, y0 + 40, 4,
             fill=REGION_COLORS[card["region"]])
        draw_icon(d, x0 + 6, y0 + 6, 34, card["icon"], card["icon_text"],
                  REGION_COLORS[card["region"]])
        text(d, x0 + 46, y0 + 6, "%d  %s" % (card["num"], card["place"]),
             F(SANS_BLACK, 10), fill=INK, anchor="la")
        text(d, x0 + 46, y0 + 18, "%s - %s" % (card["region"], card["field"]),
             F(SANS_BOLD, 8.5),
             fill=REGION_COLORS[card["region"]], anchor="la")
        f_h = F(SANS_BOLD, 12)
        lines = wrap(d, card["headline"], f_h, card_w - 12)
        draw_lines(d, x0 + 6, y0 + 44, lines[:2], f_h, fill=INK, leading=14)
        f_dt = F(SANS, 9.5)
        dlines = wrap(d, card["detail"], f_dt, card_w - 12)
        draw_lines(d, x0 + 6, y0 + 44 + 2 * 14 + 1, dlines[:1], f_dt,
                   fill=INK2, leading=12)
        text(d, x0 + 6, y0 + card_h - 14, card["tag"], F(SANS_BOLD, 8),
             fill=GREEN, anchor="la")

    # ---- briefs
    y = 646
    text(d, M, y, "ALSO ON TUESDAY 24 NOVEMBER  -  BRIEFS 14-30",
         F(SANS_BLACK, 11), fill=RED, anchor="la")
    box(d, M, y + 16, W - M, y + 17, fill=INK)
    by = y + 22
    cols = 3
    col_w = (CW - 2 * 14) / 3
    rows = 6
    f_b = F(SANS, 10.5)
    f_r = F(SANS_BOLD, 9)
    for idx, (num, region, txt) in enumerate(BRIEFS):
        col, row = divmod(idx, rows)
        bx = M + col * (col_w + 14)
        byy = by + row * 26
        text(d, bx, byy, "%d" % num, F(SANS_BLACK, 11), fill=RED, anchor="la")
        rc = REGION_COLORS[region]
        tag_w = tw(d, region, f_r) + 8
        rbox(d, bx + 24, byy + 1, bx + 24 + tag_w, byy + 12, 5, fill=rc)
        text(d, bx + 24 + tag_w / 2, byy + 2, region, f_r,
             fill=(255, 255, 255), anchor="ma")
        lines = wrap(d, txt, f_b, col_w - 24 - tag_w - 8)
        draw_lines(d, bx + 24 + tag_w + 8, byy, lines[:2], f_b, fill=INK,
                   leading=12.5)

    # ---- map + date check
    y = 826
    map_w = 470
    dc_x = M + map_w + 12
    dc_w = CW - map_w - 12
    box_h = 168
    draw_map(d, M, y, map_w, box_h)
    rbox(d, dc_x, y, dc_x + dc_w, y + box_h, 6, fill=(255, 255, 255),
         outline=LINE, width=1)
    text(d, dc_x + 10, y + 6, "DATE CHECK - LEFT OUT, NOT TUESDAY",
         F(SANS_BLACK, 10.5), fill=RED, anchor="la")
    f_dc = F(SANS, 10.5)
    dy = y + 26
    for item in DATE_CHECK:
        text(d, dc_x + 10, dy, "-  " + item, f_dc, fill=INK2, anchor="la")
        dy += 15.5

    # ---- footer
    y = 1000
    box(d, M, y - 4, W - M, y - 3, fill=INK)
    f_f = F(SANS, 9)
    text(d, M, y + 2,
         "HOW SURE: CONFIRMED = official / multiple outlets  -  "
         "REPORTED = credible report  -  CLAIM = one side, unverified",
         f_f, fill=INK2, anchor="la")
    text(d, M, y + 14,
         "Scenes are drawn illustrations, not photos  -  Times UTC unless "
         "labelled  -  Tuesday 24 November 2026",
         f_f, fill=INK2, anchor="la")

    out = img.resize((W, H), Image.LANCZOS)
    pal = out.convert("P", palette=Image.ADAPTIVE, colors=160, dither=Image.NONE)
    pal = pal.convert("RGB")
    path = os.path.join(HERE, "entry.png")
    pal.save(path, optimize=True)
    print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    build()
