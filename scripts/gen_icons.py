from pathlib import Path
import struct
import zlib

def write_png(path, rgb, size=81):
    w = h = size
    raw = b"".join(b"\x00" + bytes([rgb[0], rgb[1], rgb[2]] * w) for _ in range(h))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    data = zlib.compress(raw, 9)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", data) + chunk(b"IEND", b"")
    Path(path).write_bytes(png)


def main():
    d = Path(__file__).resolve().parents[1] / "miniapp" / "images"
    d.mkdir(parents=True, exist_ok=True)
    pairs = [
        ("888888", "tab-home.png"),
        ("2d5a27", "tab-home-active.png"),
        ("888888", "tab-scan.png"),
        ("2d5a27", "tab-scan-active.png"),
        ("888888", "tab-chat.png"),
        ("2d5a27", "tab-chat-active.png"),
        ("888888", "tab-user.png"),
        ("2d5a27", "tab-user-active.png"),
    ]
    for hexc, name in pairs:
        c = tuple(int(hexc[i : i + 2], 16) for i in (0, 2, 4))
        write_png(d / name, c)
    print("icons created:", d)


if __name__ == "__main__":
    main()
