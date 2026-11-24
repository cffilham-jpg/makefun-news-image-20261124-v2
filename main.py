#!/usr/bin/env python3
"""news-image-20261124 v2 -- legibility-first news poster.

Pure Python 3.13 standard library. Draws a 1024x1024 PNG summing up the
world news of Tuesday 24 November 2026: one dominant chess hero, four large
secondary cards, eight one-liners. Deterministic: two runs produce
byte-identical output. Honors MAKEFUN_OUTPUT_DIR (default "out").
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (250, 248, 240)
INK = (11, 31, 58)
INK_SOFT = (28, 52, 88)
RED = (200, 16, 46)
GOLD = (201, 162, 39)
GOLD_LIGHT = (232, 205, 110)
WHITE = (255, 255, 255)
CREAM = (236, 231, 214)
GREY = (90, 96, 110)

# ---------------------------------------------------------------- font
# Single-stroke vector font on a 5 x 8 grid (x 0..4, y 0..7). Each glyph is
# a tuple of polylines; each polyline is a tuple of (x, y) points. The
# poster is set entirely in capitals, so only capitals, digits and the
# punctuation the copy needs are defined.

FONT = {
    "A": (((0, 7), (2, 0), (4, 7)), ((1, 5), (3, 5))),
    "B": (((0, 0), (0, 7)), ((0, 0), (3, 0), (4, 1), (4, 3), (3, 4), (0, 4)),
          ((0, 4), (3, 4), (4, 5), (4, 6), (3, 7), (0, 7))),
    "C": (((4, 1), (3, 0), (1, 0), (0, 1), (0, 6), (1, 7), (3, 7), (4, 6)),),
    "D": (((0, 0), (0, 7), (3, 7), (4, 6), (4, 1), (3, 0), (0, 0)),),
    "E": (((4, 0), (0, 0), (0, 7), (4, 7)), ((0, 3), (3, 3))),
    "F": (((0, 7), (0, 0), (4, 0)), ((0, 3), (3, 3))),
    "G": (((4, 1), (3, 0), (1, 0), (0, 1), (0, 6), (1, 7), (3, 7), (4, 6),
          (4, 4), (2, 4)),),
    "H": (((0, 0), (0, 7)), ((4, 0), (4, 7)), ((0, 3), (4, 3))),
    "I": (((2, 0), (2, 7)), ((0, 0), (4, 0)), ((0, 7), (4, 7))),
    "J": (((4, 0), (4, 6), (3, 7), (1, 7), (0, 6)),),
    "K": (((0, 0), (0, 7)), ((4, 0), (0, 3)), ((2, 4), (4, 7))),
    "L": (((0, 0), (0, 7), (4, 7)),),
    "M": (((0, 7), (0, 0), (2, 4), (4, 0), (4, 7)),),
    "N": (((0, 7), (0, 0), (4, 7), (4, 0)),),
    "O": (((1, 0), (3, 0), (4, 1), (4, 6), (3, 7), (1, 7), (0, 6), (0, 1),
          (1, 0)),),
    "P": (((0, 7), (0, 0), (3, 0), (4, 1), (4, 3), (3, 4), (0, 4)),),
    "Q": (((1, 0), (3, 0), (4, 1), (4, 6), (3, 7), (1, 7), (0, 6), (0, 1),
          (1, 0)), ((2, 5), (4, 7))),
    "R": (((0, 7), (0, 0), (3, 0), (4, 1), (4, 3), (3, 4), (0, 4)),
          ((2, 4), (4, 7))),
    "S": (((4, 1), (3, 0), (1, 0), (0, 1), (0, 3), (1, 4), (3, 4), (4, 5),
          (4, 6), (3, 7), (1, 7), (0, 6)),),
    "T": (((0, 0), (4, 0)), ((2, 0), (2, 7))),
    "U": (((0, 0), (0, 6), (1, 7), (3, 7), (4, 6), (4, 0)),),
    "V": (((0, 0), (2, 7), (4, 0)),),
    "W": (((0, 0), (1, 7), (2, 4), (3, 7), (4, 0)),),
    "X": (((0, 0), (4, 7)), ((4, 0), (0, 7))),
    "Y": (((0, 0), (2, 3), (4, 0)), ((2, 3), (2, 7))),
    "Z": (((0, 0), (4, 0), (0, 7), (4, 7)),),
    "0": (((1, 0), (3, 0), (4, 1), (4, 6), (3, 7), (1, 7), (0, 6), (0, 1),
          (1, 0)), ((1, 5), (3, 2))),
    "1": (((1, 1), (2, 0), (2, 7)), ((0, 7), (4, 7))),
    "2": (((0, 1), (1, 0), (3, 0), (4, 1), (4, 3), (0, 7), (4, 7)),),
    "3": (((0, 1), (1, 0), (3, 0), (4, 1), (4, 3), (2, 3)),
          ((2, 3), (4, 3), (4, 6), (3, 7), (1, 7), (0, 6))),
    "4": (((3, 0), (0, 4), (4, 4)), ((3, 0), (3, 7))),
    "5": (((4, 0), (0, 0), (0, 3), (3, 3), (4, 4), (4, 6), (3, 7), (1, 7),
          (0, 6)),),
    "6": (((4, 1), (3, 0), (1, 0), (0, 1), (0, 6), (1, 7), (3, 7), (4, 6),
          (4, 4), (3, 3), (1, 3), (0, 4)),),
    "7": (((0, 0), (4, 0), (2, 7)),),
    "8": (((1, 0), (3, 0), (4, 1), (4, 3), (3, 4), (1, 4), (0, 3), (0, 1),
          (1, 0)),
         ((1, 4), (3, 4), (4, 5), (4, 6), (3, 7), (1, 7), (0, 6), (0, 5),
          (1, 4))),
    "9": (((0, 2), (0, 1), (1, 0), (3, 0), (4, 1), (4, 3), (3, 4), (1, 4),
          (0, 3)), ((4, 1), (4, 7))),
    " ": (),
    ".": (((2, 6), (2, 7)),),
    ",": (((2, 5), (2, 6), (1, 7)),),
    ":": (((2, 2), (2, 3)), ((2, 5), (2, 6))),
    ";": (((2, 2), (2, 3)), ((2, 5), (2, 6), (1, 7))),
    "'": (((2, 0), (1, 2)),),
    "\u2019": (((2, 0), (1, 2)),),
    '"': (((1, 0), (1, 2)), ((3, 0), (3, 2))),
    "!": (((2, 0), (2, 5)), ((2, 6), (2, 7))),
    "?": (((0, 1), (1, 0), (3, 0), (4, 1), (4, 2), (2, 4), (2, 5)),
          ((2, 6), (2, 7))),
    "-": (((0, 4), (4, 4)),),
    "$": (((4, 1), (3, 0), (1, 0), (0, 1), (0, 3), (1, 4), (3, 4), (4, 5),
          (4, 6), (3, 7), (1, 7), (0, 6)), ((2, 0), (2, 7))),
    "%": (((0, 1), (1, 0), (2, 1), (1, 2), (0, 1)),
          ((2, 6), (3, 5), (4, 6), (3, 7), (2, 6)), ((0, 7), (4, 0))),
    "(": (((3, 0), (2, 1), (2, 6), (3, 7)),),
    ")": (((1, 0), (2, 1), (2, 6), (1, 7)),),
    "/": (((4, 7), (0, 0)),),
    "+": (((2, 1), (2, 6)), ((0, 3), (4, 3))),
    "=": (((0, 2), (4, 2)), ((0, 5), (4, 5))),
    "\u00b7": (((2, 3), (2, 4)),),
}

GRID_W = 6  # advance width per glyph, in grid units (5 + 1 spacing)
GRID_H = 7  # cap height, in grid units


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        span = 3 * (x1 - x0)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.buf[o:o + span] = row

    def rect_border(self, x, y, w, h, t, color):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def stamp(self, cx, cy, t, color):
        self.fill_rect(cx - t // 2, cy - t // 2, t, t, color)

    def line(self, x0, y0, x1, y1, t, color):
        dx = x1 - x0
        dy = y1 - y0
        n = int(max(abs(dx), abs(dy)) * 2) + 1
        for i in range(n + 1):
            f = i / n
            self.stamp(int(round(x0 + dx * f)), int(round(y0 + dy * f)),
                       t, color)

    def disc(self, cx, cy, r, color):
        r2 = r * r
        for dy in range(-r, r + 1):
            half = int((r2 - dy * dy) ** 0.5)
            self.fill_rect(cx - half, cy + dy, half * 2 + 1, 1, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Filled triangle via scanlines (vertices sorted by y).
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if cy == ay:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / (by - ay) if by != ay else 0.0
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / (cy - by) if cy != by else 0.0
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / (cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = (xa, xb) if xa <= xb else (xb, xa)
            self.fill_rect(int(round(lo)), y, int(round(hi)) - int(round(lo)) + 1,
                           1, color)


# ---------------------------------------------------------------- text
def text_width(text, size):
    s = size / GRID_H
    return int(round((len(text) * GRID_W - 1) * s))


def draw_text(cv, x, y, text, size, color, align="left"):
    """Draw text with its top at y. align: left, center (x = centre), right."""
    s = size / GRID_H
    thick = max(1, int(round(s * 0.85)))
    w = text_width(text, size)
    if align == "center":
        x = x - w // 2
    elif align == "right":
        x = x - w
    cx = float(x)
    for ch in text:
        glyph = FONT.get(ch)
        if glyph:
            for poly in glyph:
                for (ax, ay), (bx, by) in zip(poly, poly[1:]):
                    cv.line(int(round(cx + ax * s)), int(round(y + ay * s)),
                            int(round(cx + bx * s)), int(round(y + by * s)),
                            thick, color)
        cx += GRID_W * s


# ---------------------------------------------------------------- pieces
def pill(cv, x, y, text, size, fg, bg=None, border=None):
    """Small verification pill; returns its width."""
    w = text_width(text, size) + 20
    h = size + 12
    if bg is not None:
        cv.fill_rect(x, y, w, h, bg)
    if border is not None:
        cv.rect_border(x, y, w, h, 2, border)
    draw_text(cv, x + 10, y + 6, text, size, fg)
    return w


def draw_piece(cv, cx, cy, r, color, kind):
    """Simple geometric chess piece centred at (cx, cy), radius r."""
    base_w = int(r * 1.5)
    cv.fill_rect(cx - base_w // 2, cy + r // 2, base_w, max(2, r // 3), color)
    cv.disc(cx, cy, int(r * 0.62), color)
    if kind == "king":
        t = max(2, r // 4)
        cv.fill_rect(cx - t // 2, cy - r - t, t, int(r * 0.9), color)
        cv.fill_rect(cx - int(r * 0.45), cy - r + int(r * 0.25),
                     int(r * 0.9), t, color)
    elif kind == "queen":
        t = max(2, r // 4)
        cv.fill_rect(cx - t // 2, cy - r - t, t, int(r * 0.8), color)
        cv.disc(cx - int(r * 0.5), cy - int(r * 0.7), max(2, r // 5), color)
        cv.disc(cx + int(r * 0.5), cy - int(r * 0.7), max(2, r // 5), color)
    elif kind == "rook":
        t = max(2, r // 4)
        cv.fill_rect(cx - int(r * 0.55), cy - r, int(r * 1.1), int(r * 0.5),
                     color)
        cv.fill_rect(cx - int(r * 0.18), cy - r - t, int(r * 0.36), t, color)
    elif kind == "bishop":
        cv.triangle(cx, cy - r - 2, cx - int(r * 0.4), cy - int(r * 0.4),
                    cx + int(r * 0.4), cy - int(r * 0.4), color)
    elif kind == "knight":
        cv.triangle(cx - int(r * 0.3), cy - int(r * 0.4), cx + int(r * 0.5),
                    cy - r, cx + int(r * 0.55), cy + int(r * 0.3), color)


def draw_board(cv, x, y, size):
    """8x8 board with a mid-game scatter of pieces; returns nothing."""
    sq = size // 8
    cv.rect_border(x - 3, y - 3, size + 6, size + 6, 3, GOLD)
    for r in range(8):
        for c in range(8):
            col = CREAM if (r + c) % 2 == 0 else INK_SOFT
            cv.fill_rect(x + c * sq, y + r * sq, sq, sq, col)
    # (row, col, side, kind) -- a plausible mid-game position.
    pieces = [
        (0, 0, "dark", "rook"), (0, 4, "dark", "king"),
        (0, 7, "dark", "rook"), (1, 2, "dark", "pawn"),
        (1, 5, "dark", "pawn"), (2, 3, "dark", "knight"),
        (3, 4, "dark", "pawn"), (4, 3, "light", "pawn"),
        (5, 2, "light", "knight"), (6, 1, "light", "pawn"),
        (6, 6, "light", "pawn"), (7, 0, "light", "rook"),
        (7, 3, "light", "queen"), (7, 4, "light", "king"),
        (7, 7, "light", "rook"),
    ]
    for (r, c, side, kind) in pieces:
        cx = x + c * sq + sq // 2
        cy = y + r * sq + sq // 2
        dark_sq = (r + c) % 2 == 1
        if side == "light":
            col = GOLD_LIGHT if dark_sq else WHITE
            if not dark_sq:
                cv.disc(cx, cy, sq // 2 - 2, INK)
        else:
            col = GOLD if dark_sq else INK
            if dark_sq:
                cv.disc(cx, cy, sq // 2 - 2, GOLD_LIGHT)
        draw_piece(cv, cx, cy, sq // 2 - 4, col, kind)


def draw_card(cv, x, y, w, h, label, pill_text, head_lines, body):
    """One secondary news card: red label bar, big headline, one body line."""
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect_border(x, y, w, h, 2, INK)
    cv.fill_rect(x, y, w, 28, RED)
    draw_text(cv, x + 14, y + 5, label, 18, WHITE)
    pw = text_width(pill_text, 16) + 20
    pill(cv, x + w - pw - 10, y + 4, pill_text, 16, WHITE, border=WHITE)
    ty = y + 28 + 8
    for line in head_lines:
        draw_text(cv, x + 14, ty, line, 30, INK)
        ty += 34
    draw_text(cv, x + 14, ty + 4, body, 16, GREY)


# ---------------------------------------------------------------- poster
def draw_poster():
    cv = Canvas(W, H, PAPER)

    # Masthead: navy band, title, date, red rule.
    cv.fill_rect(0, 0, W, 100, INK)
    draw_text(cv, W // 2, 12, "THE WORLD IN ONE DAY", 44, WHITE, align="center")
    draw_text(cv, W // 2, 64, "TUESDAY 24 NOVEMBER 2026", 22, GOLD_LIGHT,
              align="center")
    cv.fill_rect(0, 100, W, 4, RED)

    # Date-check strip.
    cv.rect_border(28, 108, 968, 22, 2, RED)
    draw_text(cv, W // 2, 111,
              "DATE CHECK: EVERY STORY FROM 24 NOVEMBER EDITIONS AND WIRES",
              16, INK, align="center")

    # Hero: chess dominates the page.
    cv.fill_rect(28, 136, 968, 398, INK)
    cv.rect_border(28, 136, 968, 398, 3, GOLD)
    draw_text(cv, W // 2, 150, "THE KINGS ARE TWENTY", 52, WHITE,
              align="center")
    draw_text(cv, W // 2, 210, "GAME 1 BEGINS IN GENEVA TODAY", 28,
              GOLD_LIGHT, align="center")
    cv.fill_rect(60, 246, 904, 2, GOLD)
    draw_board(cv, 60, 262, 180)
    draw_text(cv, 292, 268, "GUKESH (INDIA) VS SINDAROV (UZBEKISTAN)", 20,
              WHITE)
    draw_text(cv, 292, 294, "WORLD CHESS CHAMPIONSHIP", 20, GOLD_LIGHT)
    draw_text(cv, 292, 320, "FONDATION MARTIN BODMER, COLOGNY", 20, WHITE)
    draw_text(cv, 292, 346, "15:00 CET - SINDAROV HAS WHITE", 20, WHITE)
    pill(cv, 292, 384, "CONFIRMED", 16, GOLD_LIGHT, border=GOLD)
    numbers = [
        ("$2.5M", "PRIZE FUND"),
        ("14", "GAMES IN THE MATCH"),
        ("20 + 20", "YEARS OLD EACH"),
    ]
    for i, (num, label) in enumerate(numbers):
        cx = 28 + 968 // 6 + i * (968 // 3)
        draw_text(cv, cx, 460, num, 44, GOLD_LIGHT, align="center")
        draw_text(cv, cx, 506, label, 16, WHITE, align="center")

    # Four secondary cards, 2x2.
    cards = [
        ("MARKETS", "REPORTED", ["STOCKS ADD $3TN", "AS HUANG RETURNS"],
         "HUANG BACK MONDAY AT NVIDIA"),
        ("INDIA", "CONFIRMED", ["MODI OPENS AI", "CENTRE IN PATNA"],
         "RS 400 CRORE RESEARCH PARK"),
        ("INDIA", "CONFIRMED", ["TOP COURT FREES", "GODHRA CONVICT"],
         "BAIL GRANTED IN TRAIN CASE"),
        ("USA", "REPORTED", ["DEMOCRATS PLAN", "12 DEBATES 2028"],
         "FIRST DEBATE JUNE 2027"),
    ]
    for i, (label, ptext, head, body) in enumerate(cards):
        x = 28 + (i % 2) * 498
        y = 546 + (i // 2) * 136
        draw_card(cv, x, y, 470, 126, label, ptext, head, body)

    # One-liner strip: eight stories, two columns.
    draw_text(cv, 28, 820, "ALSO TODAY", 20, RED)
    cv.fill_rect(206, 829, 790, 2, GOLD)
    oneliners = [
        "INDIA-CHINA TALKS IN ARUNACHAL",
        "CONGRESS-SP SEAT TALKS OPEN IN UP",
        "4 RSF COMMANDERS DEFECT IN SUDAN",
        "IRAN WAR FUNDING MAY END DEC 11",
        "FOSSIL POWER SHARE FALLS BELOW 60%",
        "REPLIT CEO MET VP VANCE ON FRIDAY",
        "DE BRUYNE: FEELINGS NEVER CHANGE",
        "SUPERMOON MEETS SEVEN SISTERS",
    ]
    for i, line in enumerate(oneliners):
        x = 28 + (i // 4) * 498
        y = 848 + (i % 4) * 32
        cv.fill_rect(x, y + 4, 8, 8, RED)
        draw_text(cv, x + 16, y, line, 16, INK)

    # Footer: region counts.
    cv.fill_rect(28, 968, 968, 2, INK)
    draw_text(cv, W // 2, 976,
              "EUROPE 1 \u00b7 ASIA 4 \u00b7 N. AMERICA 3 \u00b7 AFRICA 1 "
              "\u00b7 MIDDLE EAST 1 \u00b7 WORLD 3",
              16, INK, align="center")
    return cv


# ---------------------------------------------------------------- png
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    return out + struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF)


def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.buf[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR",
                  struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    cv = draw_poster()
    write_png(os.path.join(outdir, "entry.png"), cv)


if __name__ == "__main__":
    main()
