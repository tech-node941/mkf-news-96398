#!/usr/bin/env python3
"""make.fun news-image-20261119: newspaper front page for Thursday 19 November 2026.

Pure standard-library PNG writer with a built-in 5x7 bitmap font.
Deterministic: no network, no randomness, no timestamps.
"""
import os
import struct
import zlib

W, H = 1024, 768

PAPER = bytes((244, 239, 227))
INK = bytes((24, 24, 24))
DARK = bytes((18, 32, 60))
GOLD = bytes((222, 168, 88))
RED = bytes((146, 32, 26))
GREY = bytes((105, 100, 90))
WHITE = bytes((250, 248, 240))
SLATE = bytes((122, 132, 152))
# 5x7 bitmap font: 7 row masks per glyph, MSB = leftmost pixel
F = {
" ": (0,0,0,0,0,0,0), "!": (4,4,4,4,4,0,4), "\"": (10,10,0,0,0,0,0),
"#": (10,31,10,10,31,10,0), "$": (4,15,20,14,5,30,4), "%": (25,26,2,4,8,11,19),
"&": (12,18,20,8,21,18,13), "(": (2,4,8,8,8,4,2), ")": (8,4,2,2,2,4,8),
"*": (0,4,21,14,21,4,0), "+": (0,4,4,31,4,4,0), ",": (0,0,0,0,12,4,8),
"-": (0,0,0,31,0,0,0), ".": (0,0,0,0,0,12,12), "/": (1,2,2,4,8,8,16),
"0": (14,17,19,21,25,17,14), "1": (4,12,4,4,4,4,14), "2": (14,17,1,2,4,10,31),
"3": (31,2,4,2,1,17,14), "4": (2,6,10,18,31,2,2), "5": (31,16,30,1,1,17,14),
"6": (6,8,16,30,17,17,14), "7": (31,1,2,4,8,8,8), "8": (14,17,17,14,17,17,14),
"9": (14,17,17,15,1,2,12), ":": (0,12,12,0,12,12,0), ";": (0,12,12,0,12,4,8),
"<": (2,4,8,16,8,4,2), "=": (0,0,31,0,31,0,0), ">": (8,4,2,1,2,4,8),
"?": (14,11,1,2,4,0,4), "@": (14,17,23,21,23,16,14),
"A": (14,17,17,31,17,17,17), "B": (30,17,17,30,17,17,30), "C": (14,17,16,16,16,17,14),
"D": (30,17,17,17,17,17,30), "E": (31,16,16,30,16,16,31), "F": (31,16,16,30,16,16,16),
"G": (14,17,16,23,17,17,15), "H": (17,17,17,31,17,17,17), "I": (14,4,4,4,4,4,14),
"J": (7,2,2,2,2,18,12), "K": (17,18,20,24,20,18,17), "L": (16,16,16,16,16,16,31),
"M": (17,27,21,21,17,17,17), "N": (17,25,21,19,17,17,17), "O": (14,17,17,17,17,17,14),
"P": (30,17,17,30,16,16,16), "Q": (14,17,17,17,21,12,13), "R": (30,17,17,30,20,18,17),
"S": (15,16,16,14,1,1,30), "T": (31,4,4,4,4,4,4), "U": (17,17,17,17,17,17,14),
"V": (17,17,17,17,17,10,4), "W": (17,17,17,21,21,27,17), "X": (17,17,10,4,10,17,17),
"Y": (17,17,10,4,4,4,4), "Z": (31,1,2,4,8,16,31),
"[": (14,8,8,8,8,8,14), "\\": (16,16,8,4,2,2,1), "]": (14,2,2,2,2,2,14),
"^": (4,10,17,0,0,0,0), "_": (0,0,0,0,0,0,31),
"a": (0,0,14,1,15,17,15), "b": (16,16,30,17,17,17,30), "c": (0,0,15,16,16,16,15),
"d": (1,1,15,17,17,17,15), "e": (0,0,14,17,31,16,14), "f": (6,9,8,28,8,8,8),
"g": (0,15,17,15,1,1,14), "h": (16,16,30,17,17,17,17), "i": (4,0,12,4,4,4,14),
"j": (2,0,6,2,2,2,12), "k": (16,16,18,20,24,20,18), "l": (12,4,4,4,4,4,14),
"m": (0,0,26,21,21,21,21), "n": (0,0,30,17,17,17,17), "o": (0,0,14,17,17,17,14),
"p": (0,30,17,30,16,16,16), "q": (0,15,17,15,1,1,1), "r": (0,0,22,25,16,16,16),
"s": (0,0,15,16,14,1,30), "t": (8,8,28,8,8,9,6), "u": (0,0,17,17,17,19,13),
"v": (0,0,17,17,17,10,4), "w": (0,0,17,21,21,21,10), "x": (0,0,17,10,4,10,17),
"y": (0,17,17,15,1,1,14), "z": (0,0,31,2,4,8,31),
}
def wrap(text, n):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = cur + (" " if cur else "") + w
    if cur:
        lines.append(cur)
    return lines

class Img:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def px_set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i+3] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px_set(xx, yy, c)

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def text(self, x, y, s, c, scale=1):
        cx = x
        for ch in s:
            g = F.get(ch)
            if g is None:
                cx += 6 * scale
                continue
            for r in range(7):
                for b in range(5):
                    if g[r] >> (4 - b) & 1:
                        for dy in range(scale):
                            for dx in range(scale):
                                self.px_set(cx + b*scale + dx, y + r*scale + dy, c)
            cx += 6 * scale

    def text_center(self, cx, y, s, c, scale=1):
        w = len(s) * 6 * scale - scale
        self.text(cx - w // 2, y, s, c, scale)

    def to_png(self):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            i = y * self.w * 3
            raw += self.px[i:i + self.w * 3]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(
                ">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        sig = b"\x89PNG\r\n\x1a\n"
        ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0))
        idat = chunk(b"IDAT", comp)
        iend = chunk(b"IEND", b"")
        return sig + ihdr + idat + iend

def draw(img):
    m = 18
    img.rect(0, 0, W, H, PAPER)
    img.rect(0, 0, W, 8, DARK)
    img.rect(0, 8, W, 2, GOLD)
    img.rect(0, H - 26, W, 26, DARK)
    img.rect(0, H - 26, W, 1, GOLD)

    # dateline
    img.text(m, 20, "THURSDAY, NOVEMBER 19, 2026", RED, 2)
    img.text(W - m - len("VOL. 1 - NO. 320") * 6, 22, "VOL. 1 - NO. 320", GREY, 1)

    # masthead
    img.rect(0, 46, W, 84, DARK)
    img.rect(0, 46, W, 2, GOLD)
    img.text_center(W // 2, 54, "WORLD NEWS", PAPER, 7)
    img.text_center(W // 2, 112, "GLOBAL DISPATCH  *  19 NOVEMBER 2026  *  FINAL EDITION", GOLD, 1)
    img.rect(m, 136, W - 2 * m, 3, INK)
    img.rect(m, 142, W - 2 * m, 1, GREY)

    # top story with kicker
    y = 158
    img.rect(m, y - 2, 92, 16, RED)
    img.text(m + 5, y, "TOP STORY", PAPER, 1)
    img.text(W - m - 104, y - 2, "MUST READ", RED, 2)
    img.rect(W - m - 154, y + 3, 50, 2, RED)
    y += 26
    img.text(m, y, "GRAND THEFT AUTO VI", DARK, 5)
    y += 44
    img.text(m, y, "CONSOLES SELL OUT ON LAUNCH DAY", DARK, 3)
    y += 24
    img.text(m, y, "MIDNIGHT QUEUES CIRCLE CITY BLOCKS AS ROCKSTAR BLOCKBUSTER FINALLY GOES ON SALE", INK, 2)
    y += 20
    img.text(m, y, "Record pre-orders strain retailer servers; analyscall it the biggest entertainment launch ever.", GREY, 1)
    y += 16
    img.rect(m, y, W - 2 * m, 2, INK)
    return y + 6
def body(img, y):
    m = 18
    col_w = 320
    gap = 16
    bh = 174
    boxes = [
        ("WORLD", "CLIMATE SUMMIT DEAL", ["Delegates reach tentative pact on", "emissions timeline as talks enter", "final hours; island states demand", "faster cuand more funding."], RED),
        ("MARKETS", "GLOBAL STOCKS MIXED", ["Indexes waver as traders weigh", "the rate outlook; tech shares slip", "while energy and defense names", "hold steady into the close."], DARK),
        ("TECH / AI", "AI RACE RESHAPES TECH", ["Fresh data-center investment signals", "an AI infrastructure race, while", "regulators circle big chip and", "cloud mergers on two continents."], DARK),
        ("SPORTS", "CHAMPIONS LEAGUE", ["Stunning comeback in Europe: late", "goals flip the tie and send the", "underdogs through to the knockout", "round in front of a roaring crowd."], DARK),
        ("BUSINESS", "OIL NEAR $79, GOLD RECORD", ["Crude steadies as supply worries", "offset demand fears; gold sea", "fresh record while the dollar", "softens against the euro."], DARK),
        ("CULTURE", "GTA VI SMASHES RECORDS", ["Launch-day sales top forecasts;", "survey finds 1 in 3 gamers took", "the day off as midnight queues", "circle blocks in 40 cities."], RED),
    ]
    x0, y0 = m, y
    for i, (tag, head, lines, accent) in enumerate(boxes):
        col, row = i % 3, i // 3
        x = x0 + col * (col_w + gap)
        yy = y0 + row * (bh + 12)
        img.rect(x, yy, col_w, bh, WHITE)
        img.frame(x, yy, col_w, bh, INK, 1)
        img.rect(x, yy, col_w, 15, accent)
        img.text(x + 5, yy + 4, tag, WHITE, 1)
        img.text(x + 8, yy + 22, head, DARK, 2)
        img.rect(x + 8, yy + 38, col_w - 16, 1, GREY)
        for j, ln in enumerate(lines):
            img.text(x + 8, yy + 46 + j * 14, ln, INK, 1)
        img.text(x + 8, yy + bh - 17, "PAGE 4  *  CONT. P. 7", GREY, 1)
    return y0 + 2 * (bh + 12)
def footer(img, y):
    m = 18
    img.rect(m, y + 4, W - 2 * m, 2, INK)
    img.text_center(W // 2, y + 12, "THE WORLD IN FIVE STORIES  *  FULL COVERAGE PAGES 2-8", DARK, 2)
    img.rect(0, H - 24, W, 24, DARK)
    img.text(m, H - 17, "WORLD NEWS  *  THURSDAY 19 NOVEMBER 2026  *  MAKE.FUN EDITION", GOLD, 1)
    img.text(W - m - 116, H - 17, "tech-node941", PAPER, 1)

def main():
    img = Img(W, H, PAPER)
    y = draw(img)
    y2 = body(img, y)
    footer(img, y2)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    data = img.to_png()
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(data)
    print("wrote", os.path.join(out_dir, "entry.png"), len(data), "bytes")

if __name__ == "__main__":
    main()
