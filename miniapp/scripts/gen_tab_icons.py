"""Generate tab bar icons for WeChat mini program."""
import struct
import zlib
import math
import os

SIZE = 81
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')


def png_chunk(tag, data):
    crc = zlib.crc32(tag + data) & 0xffffffff
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', crc)


def write_png(path, pixels):
    """pixels: list of (r,g,b,a) tuples, row-major."""
    width = height = SIZE
    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            r, g, b, a = pixels[y * width + x]
            raw += bytes([r, g, b, a])

    compressed = zlib.compress(raw, 9)
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += png_chunk(b'IHDR', ihdr)
    png += png_chunk(b'IDAT', compressed)
    png += png_chunk(b'IEND', b'')

    with open(path, 'wb') as f:
        f.write(png)


def circle_mask(cx, cy, r):
    mask = []
    for y in range(SIZE):
        for x in range(SIZE):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            mask.append(1.0 if dist <= r else 0.0)
    return mask


def draw_icon(draw_fn, color, bg=(0, 0, 0, 0)):
    pixels = [bg] * (SIZE * SIZE)
    draw_fn(pixels, color)
    return pixels


def set_px(pixels, x, y, color):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        pixels[y * SIZE + x] = color


def fill_rect(pixels, x0, y0, x1, y1, color):
    for y in range(y0, y1):
        for x in range(x0, x1):
            set_px(pixels, x, y, color)


def fill_round_rect(pixels, x0, y0, w, h, r, color):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            in_rect = True
            if x < x0 + r and y < y0 + r:
                in_rect = (x - x0 - r) ** 2 + (y - y0 - r) ** 2 <= r ** 2
            elif x > x0 + w - r - 1 and y < y0 + r:
                in_rect = (x - (x0 + w - r - 1) - r) ** 2 + (y - y0 - r) ** 2 <= r ** 2
            elif x < x0 + r and y > y0 + h - r - 1:
                in_rect = (x - x0 - r) ** 2 + (y - (y0 + h - r - 1) - r) ** 2 <= r ** 2
            elif x > x0 + w - r - 1 and y > y0 + h - r - 1:
                in_rect = (x - (x0 + w - r - 1) - r) ** 2 + (y - (y0 + h - r - 1) - r) ** 2 <= r ** 2
            if in_rect:
                set_px(pixels, x, y, color)


def draw_home(pixels, color):
    # roof
    for i in range(20):
        w = i * 2 + 1
        cx = SIZE // 2
        y = 18 + i
        for x in range(cx - w // 2, cx + w // 2 + 1):
            set_px(pixels, x, y, color)
    # body
    fill_round_rect(pixels, 22, 38, 37, 28, 4, color)
    # door
    door = tuple(max(0, c - 40) for c in color[:3]) + (255,)
    fill_round_rect(pixels, 35, 50, 11, 16, 2, door)


def draw_scan(pixels, color):
    # corner brackets
    t = 4
    l = 16
    corners = [(18, 18), (SIZE - 18 - l, 18), (18, SIZE - 18 - l), (SIZE - 18 - l, SIZE - 18 - l)]
    for cx, cy in corners:
        fill_rect(pixels, cx, cy, cx + l, cy + t, color)
        fill_rect(pixels, cx, cy, cx + t, cy + l, color)
    # center dot
    for y in range(SIZE):
        for x in range(SIZE):
            if (x - SIZE // 2) ** 2 + (y - SIZE // 2) ** 2 <= 36:
                set_px(pixels, x, y, color)


def draw_chat(pixels, color):
    # bubble
    fill_round_rect(pixels, 14, 16, 53, 38, 10, color)
    # tail
    for i in range(10):
        set_px(pixels, 22 + i, 54 - i, color)
        set_px(pixels, 23 + i, 54 - i, color)
    # dots
    dot_c = tuple(min(255, c + 80) for c in color[:3]) + (255,)
    for dx in [28, 40, 52]:
        for y in range(SIZE):
            for x in range(SIZE):
                if (x - dx) ** 2 + (y - 35) ** 2 <= 9:
                    set_px(pixels, x, y, dot_c)


def draw_user(pixels, color):
    # head
    for y in range(SIZE):
        for x in range(SIZE):
            if (x - SIZE // 2) ** 2 + (y - 28) ** 2 <= 144:
                set_px(pixels, x, y, color)
    # body
    for y in range(48, 68):
        for x in range(18, 63):
            dx = abs(x - SIZE // 2)
            if dx < 22 - (y - 48) * 0.3:
                set_px(pixels, x, y, color)


ICONS = {
    'tab-home': draw_home,
    'tab-scan': draw_scan,
    'tab-chat': draw_chat,
    'tab-user': draw_user,
}

GRAY = (153, 153, 153, 255)
GREEN = (45, 90, 39, 255)

os.makedirs(OUT_DIR, exist_ok=True)

for name, fn in ICONS.items():
    write_png(os.path.join(OUT_DIR, f'{name}.png'), draw_icon(fn, GRAY))
    write_png(os.path.join(OUT_DIR, f'{name}-active.png'), draw_icon(fn, GREEN))

print(f'Generated {len(ICONS) * 2} icons in {OUT_DIR}')
