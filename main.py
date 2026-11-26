#!/usr/bin/env python3
"""THE WORLD - Thursday 26 November 2026.

One-page newspaper image summing up the world's news of 26 November 2026.
Pure Python 3 standard library: draws the page into an RGB buffer and
encodes it as a PNG with zlib. No network, no files read, no randomness:
the same bytes come out of every run.
"""
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---- palette ------------------------------------------------------------
PAPER = (247, 243, 232)
INK = (20, 33, 61)
NAVY = (16, 28, 54)
NAVY2 = (28, 48, 88)
RED = (179, 32, 44)
GOLD = (201, 162, 39)
TEAL = (14, 116, 110)
GREY = (90, 96, 110)
LIGHT = (226, 230, 236)
WHITE = (255, 255, 255)
CREAM = (250, 246, 236)
DARKTXT = (30, 30, 34)
SKY = (52, 84, 138)
ORANGE = (232, 116, 30)
YELLOW = (245, 197, 66)
GREEN = (34, 139, 80)

# ---- 5x7 bitmap font (my own glyph patterns) ---------------------------
# Each glyph: 7 rows, each row a 5-bit value, bit 4 = leftmost pixel.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
}


def glyph_width(scale):
    return 6 * scale


def text_width(text, scale):
    return sum(glyph_width(scale) for _ in text) - scale


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, length, color, t=1):
        self.fill_rect(x, y, length, t, color)

    def vline(self, x, y, length, color, t=1):
        self.fill_rect(x, y, t, length, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        # filled circle by scanlines
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, t=2):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, t, 1, color)
            self.fill_rect(cx + dx - t + 1, cy + dy, t, 1, color)
        for dx in range(-r, r + 1):
            dy = int((r * r - dx * dx) ** 0.5)
            self.fill_rect(cx + dx, cy - dy, 1, t, color)
            self.fill_rect(cx + dx, cy + dy - t + 1, 1, t, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # filled triangle via scanline interpolation
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
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
            xlo, xhi = int(min(xa, xb)), int(max(xa, xb))
            self.fill_rect(xlo, y, xhi - xlo + 1, 1, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s.upper():
            rows = FONT.get(ch)
            if rows is None:
                cx += glyph_width(scale)
                continue
            for r, bits in enumerate(rows):
                for c in range(5):
                    if bits & (1 << (4 - c)):
                        self.fill_rect(cx + c * scale, y + r * scale,
                                       scale, scale, color)
            cx += glyph_width(scale)
        return cx

    def text_center(self, cx, y, s, scale, color):
        w = text_width(s, scale)
        self.text(cx - w // 2, y, s, scale, color)
        return w

    def wrap(self, s, scale, max_w):
        """Split text into lines fitting max_w pixels."""
        words = s.split(" ")
        lines = []
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


# ---- vector illustrations -------------------------------------------------

def draw_stars(cv, x0, y0, x1, y1):
    """Fixed star field, deterministic positions."""
    pts = [(40, 30), (120, 70), (210, 25), (300, 60), (380, 30),
           (470, 80), (90, 120), (180, 150), (260, 110), (350, 140),
           (430, 120), (30, 180), (150, 200), (330, 190), (480, 170),
           (70, 230), (240, 240), (410, 230), (500, 200), (160, 90)]
    for (px, py) in pts:
        if x0 <= px < x1 and y0 <= py < y1:
            cv.fill_rect(px, py, 2, 2, WHITE)
            cv.fill_rect(px - 1, py, 4, 1, WHITE)
            cv.fill_rect(px, py - 1, 1, 4, WHITE)


def draw_rocket(cv, x, y, s):
    """Upright rocket, scale s (body height ~ 120*s)."""
    # flame
    cv.triangle(x + 8 * s, y + 118 * s, x + 22 * s, y + 118 * s,
                x + 15 * s, y + 148 * s, ORANGE)
    cv.triangle(x + 11 * s, y + 118 * s, x + 19 * s, y + 118 * s,
                x + 15 * s, y + 136 * s, YELLOW)
    # fins
    cv.triangle(x + 2 * s, y + 92 * s, x + 9 * s, y + 88 * s,
                x + 9 * s, y + 116 * s, RED)
    cv.triangle(x + 28 * s, y + 92 * s, x + 21 * s, y + 88 * s,
                x + 21 * s, y + 116 * s, RED)
    # body
    cv.fill_rect(x + 9 * s, y + 18 * s, 12 * s, 100 * s, WHITE)
    cv.rect(x + 9 * s, y + 18 * s, 12 * s, 100 * s, LIGHT, 1)
    # nose cone
    cv.triangle(x + 9 * s, y + 18 * s, x + 21 * s, y + 18 * s,
                x + 15 * s, y, RED)
    # window
    cv.circle(x + 15 * s, y + 42 * s, 5 * s, SKY)
    cv.ring(x + 15 * s, y + 42 * s, 5 * s, NAVY, 2)
    # band
    cv.fill_rect(x + 9 * s, y + 78 * s, 12 * s, 6 * s, RED)
    # engine
    cv.fill_rect(x + 11 * s, y + 118 * s, 8 * s, 5 * s, GREY)


def draw_station(cv, x, y, s):
    """Small space station: core module + solar panels + ring."""
    cv.fill_rect(x, y + 10 * s, 90 * s, 12 * s, LIGHT)
    cv.rect(x, y + 10 * s, 90 * s, 12 * s, GREY, 1)
    cv.fill_rect(x + 34 * s, y + 4 * s, 22 * s, 24 * s, WHITE)
    cv.rect(x + 34 * s, y + 4 * s, 22 * s, 24 * s, GREY, 1)
    cv.circle(x + 45 * s, y + 16 * s, 4 * s, SKY)
    # solar panels
    cv.fill_rect(x - 34 * s, y + 8 * s, 32 * s, 16 * s, NAVY2)
    cv.fill_rect(x + 92 * s, y + 8 * s, 32 * s, 16 * s, NAVY2)
    cv.vline(x - 18 * s, y + 12 * s, 8 * s, GOLD, 1)
    cv.vline(x - 2 * s, y + 12 * s, 8 * s, GOLD, 1)
    cv.vline(x + 108 * s, y + 12 * s, 8 * s, GOLD, 1)
    # dish
    cv.line(x + 60 * s, y + 10 * s, x + 72 * s, y - 6 * s, WHITE, 2)
    cv.circle(x + 73 * s, y - 7 * s, 3 * s, GOLD)


def draw_building(cv, x, y, w, h):
    """Supermarket front with striped awning and open door."""
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)
    # awning stripes
    aw = 14
    for i in range(0, w, aw):
        col = RED if (i // aw) % 2 == 0 else WHITE
        cv.fill_rect(x + i, y, min(aw, w - i), 16, col)
    cv.hline(x, y + 16, w, INK, 2)
    # sign band
    cv.fill_rect(x + 6, y + 26, w - 12, 20, NAVY)
    cv.text(x + 12, y + 29, "MARKET", 2, WHITE)
    # windows
    cv.fill_rect(x + 12, y + 58, 34, 30, SKY)
    cv.fill_rect(x + w - 46, y + 58, 34, 30, SKY)
    # door, open with light
    cv.fill_rect(x + w // 2 - 14, y + 56, 28, h - 56, GOLD)
    cv.rect(x + w // 2 - 14, y + 56, 28, h - 56, INK, 2)
    # green freed badge
    cv.circle(x + w - 22, y + 22, 16, GREEN)
    cv.ring(x + w - 22, y + 22, 16, WHITE, 2)
    cv.line(x + w - 30, y + 22, x + w - 24, y + 28, WHITE, 3)
    cv.line(x + w - 24, y + 28, x + w - 13, y + 14, WHITE, 3)


def draw_sea_plane(cv, x, y, w, h):
    """Gulf waves and a small plane silhouette above them."""
    # sky band
    cv.fill_rect(x, y, w, h - 46, (214, 228, 240))
    # plane silhouette
    px, py = x + w // 2, y + 26
    cv.line(px - 46, py, px + 46, py, INK, 3)
    cv.line(px - 10, py - 2, px + 34, py - 16, INK, 3)
    cv.line(px - 34, py + 2, px - 6, py + 14, INK, 3)
    cv.triangle(px + 46, py - 3, px + 46, py + 3, px + 58, py, INK)
    cv.triangle(px - 46, py - 3, px - 46, py + 3, px - 56, py - 8, INK)
    # sea
    sy = y + h - 46
    cv.fill_rect(x, sy, w, 46, (38, 92, 150))
    for k in range(3):
        yy = sy + 10 + k * 13
        for xx in range(x + 6, x + w - 6, 26):
            cv.line(xx, yy, xx + 13, yy - 5, WHITE, 2)
            cv.line(xx + 13, yy - 5, xx + 26, yy, WHITE, 2)
    # life ring
    cv.ring(x + w - 34, sy + 24, 10, ORANGE, 3)


def draw_bars(cv, x, y, w, h):
    """GDP bar chart: Q2 2.2% vs Q3 4.3%."""
    base = y + h - 26
    cv.hline(x, base, w, INK, 2)
    cv.vline(x, y + 8, h - 34, INK, 2)
    # Q2 bar (2.2) and Q3 bar (4.3), heights proportional to value
    bh2 = int((h - 40) * 2.2 / 5.0)
    bh3 = int((h - 40) * 4.3 / 5.0)
    cv.fill_rect(x + 26, base - bh2, 44, bh2, GREY)
    cv.fill_rect(x + 26 + 76, base - bh3, 44, bh3, RED)
    cv.text(x + 30, base + 6, "Q2", 2, DARKTXT)
    cv.text(x + 30 + 76, base + 6, "Q3", 2, DARKTXT)
    cv.text(x + 28, base - bh2 - 16, "2.2%", 2, DARKTXT)
    cv.text(x + 28 + 76, base - bh3 - 16, "4.3%", 2, RED)
    # up arrow over Q3
    ax = x + 26 + 76 + 52
    cv.line(ax, base - bh3 - 4, ax + 26, base - bh3 - 30, GREEN, 3)
    cv.line(ax + 26, base - bh3 - 30, ax + 16, base - bh3 - 28, GREEN, 3)
    cv.line(ax + 26, base - bh3 - 30, ax + 24, base - bh3 - 20, GREEN, 3)


def draw_globe(cv, cx, cy, r):
    """Simple globe with meridians."""
    cv.circle(cx, cy, r, (38, 92, 150))
    cv.ring(cx, cy, r, NAVY, 2)
    cv.ring(cx, cy, int(r * 0.55), WHITE, 1)
    cv.hline(cx - r, cy, 2 * r, WHITE, 1)
    cv.line(cx - int(r * 0.7), cy - int(r * 0.7), cx + int(r * 0.7),
            cy + int(r * 0.7), WHITE, 1)
    cv.line(cx - int(r * 0.7), cy + int(r * 0.7), cx + int(r * 0.7),
            cy - int(r * 0.7), WHITE, 1)


def draw_flame(cv, x, y, s):
    """Stylised fire over a road."""
    cv.fill_rect(x, y + 62 * s, 120 * s, 6 * s, INK)
    cv.fill_rect(x, y + 70 * s, 120 * s, 4 * s, WHITE)
    for i in range(0, 120 * s, 20 * s):
        cv.fill_rect(x + i, y + 62 * s, 10 * s, 6 * s, YELLOW)
    cv.triangle(x + 30 * s, y + 62 * s, x + 58 * s, y + 62 * s,
                x + 44 * s, y + 6 * s, ORANGE)
    cv.triangle(x + 62 * s, y + 62 * s, x + 92 * s, y + 62 * s,
                x + 77 * s, y + 18 * s, RED)
    cv.triangle(x + 40 * s, y + 62 * s, x + 54 * s, y + 62 * s,
                x + 47 * s, y + 30 * s, YELLOW)
    cv.triangle(x + 66 * s, y + 62 * s, x + 80 * s, y + 62 * s,
                x + 73 * s, y + 38 * s, YELLOW)


# ---- panel helpers ----------------------------------------------------------

def panel(cv, x, y, w, h, kicker, kicker_color, headline, body, art=None):
    cv.fill_rect(x, y, w, h, CREAM)
    cv.rect(x, y, w, h, INK, 2)
    cv.fill_rect(x, y, w, 4, kicker_color)
    tx = x + 14
    ty = y + 14
    cv.text(tx, ty, kicker, 2, kicker_color)
    ty += 22
    for line in cv.wrap(headline, 3, w - 28):
        cv.text(tx, ty, line, 3, INK)
        ty += 26
    ty += 4
    for line in cv.wrap(body, 2, w - 28):
        cv.text(tx, ty, line, 2, DARKTXT)
        ty += 17
    if art is not None:
        art(cv, x, y, w, h, ty)


# ---- page layout ------------------------------------------------------------

def panel2(cv, x, y, w, h, kicker, kicker_color, headline, body, art_fn):
    """Panel with a picture strip on top, text below."""
    cv.fill_rect(x, y, w, h, CREAM)
    cv.rect(x, y, w, h, INK, 2)
    art_h = 84
    art_fn(cv, x, y, w, art_h)
    cv.hline(x, y + art_h, w, INK, 2)
    tx = x + 14
    ty = y + art_h + 12
    cv.text(tx, ty, kicker, 2, kicker_color)
    ty += 22
    for line in cv.wrap(headline, 3, w - 28):
        cv.text(tx, ty, line, 3, INK)
        ty += 26
    ty += 4
    for line in cv.wrap(body, 2, w - 28):
        cv.text(tx, ty, line, 2, DARKTXT)
        ty += 17


def draw_page(cv):
    # ---- masthead ------------------------------------------------------
    cv.fill_rect(0, 0, W, 124, NAVY)
    cv.hline(0, 8, W, GOLD, 3)
    cv.hline(0, 116, W, GOLD, 3)
    cv.text_center(W // 2, 18, "THE WORLD", 9, WHITE)
    cv.text_center(W // 2, 90, "THURSDAY 26 NOVEMBER 2026", 3, GOLD)
    # ---- tagline -------------------------------------------------------
    cv.text_center(W // 2, 131,
                   "ONE DAY OF WORLD NEWS * SIX STORIES * FIVE CONTINENTS",
                   2, GREY)
    cv.hline(16, 152, W - 32, INK, 1)

    # ---- hero: Pakistan's first astronaut ------------------------------
    hx, hy, hw, hh = 16, 160, 584, 380
    cv.fill_rect(hx, hy, hw, hh, CREAM)
    cv.rect(hx, hy, hw, hh, INK, 2)
    cv.fill_rect(hx + 2, hy + 2, hw - 4, 198, NAVY)
    draw_stars(cv, hx + 2, hy + 2, hx + hw - 2, hy + 200)
    draw_rocket(cv, hx + 64, hy + 24, 1)
    draw_station(cv, hx + 330, hy + 52, 1)
    cv.text_center(hx + 400, hy + 172, "SHENZHOU-24 * TIANGONG", 2, WHITE)
    ty = hy + 214
    cv.text(hx + 14, ty, "SPACE * CHINA-PAKISTAN", 2, RED)
    ty += 24
    for line in cv.wrap("PAKISTAN'S FIRST ASTRONAUT REACHES TIANGONG STATION",
                        4, hw - 28):
        cv.text(hx + 14, ty, line, 4, INK)
        ty += 34
    ty += 6
    for line in cv.wrap(
            "Zeeshan Ali flies aboard Shenzhou-24, the first foreigner "
            "on China's space station.", 2, hw - 28):
        cv.text(hx + 14, ty, line, 2, DARKTXT)
        ty += 17

    # ---- right column --------------------------------------------------
    rx, rw = 616, 392
    # Colombia: hostages freed
    panel(cv, rx, 160, rw, 190, "COLOMBIA * RESCUE", RED,
          "76 HOSTAGES FREED IN CARTAGENA",
          "Police storm a supermarket after a 17-hour siege; "
          "one gunman killed, all captives safe.")
    cv.circle(rx + rw - 26, 160 + 24, 14, GREEN)
    cv.ring(rx + rw - 26, 160 + 24, 14, WHITE, 2)
    cv.line(rx + rw - 33, 160 + 24, rx + rw - 28, 160 + 29, WHITE, 3)
    cv.line(rx + rw - 28, 160 + 29, rx + rw - 18, 160 + 16, WHITE, 3)
    # Mississippi: plane crash
    panel(cv, rx, 366, rw, 174, "UNITED STATES * AIR DISASTER", RED,
          "MISSISSIPPI PLANE CRASH KILLS SIX",
          "A Cessna 210 goes down in the Gulf of Mexico; "
          "two children among the dead.")
    wy = 366 + 174 - 26
    for k in range(2):
        yy = wy + k * 11
        for xx in range(rx + 8, rx + rw - 8, 26):
            cv.line(xx, yy, xx + 13, yy - 4, SKY, 2)
            cv.line(xx + 13, yy - 4, xx + 26, yy, SKY, 2)

    # ---- middle row ----------------------------------------------------
    my, mh = 556, 234
    mw = 320
    # US economy
    def us_art(cv2, ax, ay, aw, ah):
        draw_bars(cv2, ax + 18, ay + 4, aw - 36, ah - 8)

    panel2(cv, 16, my, mw, mh, "UNITED STATES * ECONOMY", TEAL,
           "US ECONOMY GROWS 4.3%",
           "Q3 growth revised up from 3.4%; new tariffs "
           "unveiled on 14 partners.", us_art)
    # Pacific
    def pac_art(cv2, ax, ay, aw, ah):
        draw_globe(cv2, ax + aw // 2, ay + ah // 2 + 2, 32)
        cv2.text(ax + 14, ay + ah - 18, "PACIFIC", 2, GREY)

    panel2(cv, 352, my, mw, mh, "ASIA-PACIFIC * DIPLOMACY", TEAL,
           "SWISS EXPELLED FROM N. KOREA",
           "Swiss office shut in Pyongyang; Solomons pick "
           "Australia as partner.", pac_art)
    # Cairo
    def cairo_art(cv2, ax, ay, aw, ah):
        draw_flame(cv2, ax + aw // 2 - 36, ay + 8, 1)

    panel2(cv, 688, my, mw, mh, "EGYPT * TRAGEDY", TEAL,
           "31 DIE IN CAIRO TANKER FIRE",
           "Fuel tanker crash sets a highway ablaze; "
           "Huawei convicted in a US court.", cairo_art)

    # ---- bottom strip: also today --------------------------------------
    bx, by, bw, bh = 16, 806, 992, 202
    cv.fill_rect(bx, by, bw, bh, INK)
    cv.fill_rect(bx, by, bw, 4, GOLD)
    cv.text(bx + 16, by + 16, "ALSO ON 26 NOVEMBER", 3, GOLD)
    items = [
        "INDIA marks 77th Constitution Day",
        "18 YEARS since the Mumbai attacks of 26/11",
        "CHESS: Gukesh v Sindarov, game 3 in Geneva",
        "BANGLADESH garment wage up 36%",
        "EU summit opens in Brussels",
        "INDONESIA: dozens trapped in flooded gold mine",
    ]
    col_x = [bx + 16, bx + 508]
    row_y = [by + 56, by + 102, by + 148]
    for i, item in enumerate(items):
        ix = col_x[i % 2]
        iy = row_y[i // 2]
        cv.fill_rect(ix, iy + 4, 9, 9, GOLD)
        for j, line in enumerate(cv.wrap(item, 2, 440)):
            cv.text(ix + 18, iy + j * 17, line, 2, WHITE)
    cv.text_center(W // 2, by + 186,
                   "THE WORLD * THURSDAY 26 NOVEMBER 2026 * ALL STORIES "
                   "FIRST REPORTED ON 26 NOVEMBER 2026", 1, LIGHT)


# ---- PNG encoder (stdlib only) --------------------------------------------

def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    cv = Canvas(W, H, PAPER)
    draw_page(cv)
    data = encode_png(cv)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    # best-effort local copy for inspection; a read-only repo must not
    # fail the run, so any error here is swallowed.
    try:
        os.makedirs("out", exist_ok=True)
        with open(os.path.join("out", "entry.png"), "wb") as f:
            f.write(data)
    except OSError:
        pass
    sys.stdout.write("wrote %s %d bytes\n" % (path, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
