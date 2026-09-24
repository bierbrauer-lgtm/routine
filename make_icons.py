"""Erzeugt die App-Icons (PNG) ohne externe Bibliotheken."""
import math
import struct
import zlib

TOP = (0x2F, 0xC4, 0x80)
BOTTOM = (0x0D, 0x5E, 0x46)
CHECK = [((0.28, 0.52), (0.43, 0.67)), ((0.43, 0.67), (0.73, 0.36))]
HALF_WIDTH = 0.045


def seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def shade(u, v):
    if min(seg_dist(u, v, a, b) for a, b in CHECK) < HALF_WIDTH:
        return (255, 255, 255)
    t = (u * 0.4 + v * 0.6)
    return tuple(TOP[i] + (BOTTOM[i] - TOP[i]) * t for i in range(3))


def write_png(path, size, ss=3):
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            acc = [0.0, 0.0, 0.0]
            for sy in range(ss):
                for sx in range(ss):
                    c = shade((x + (sx + 0.5) / ss) / size, (y + (sy + 0.5) / ss) / size)
                    for i in range(3):
                        acc[i] += c[i]
            raw.extend(round(a / (ss * ss)) for a in acc)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(chunk(b"IEND", b""))


if __name__ == "__main__":
    for s in (180, 192, 512):
        write_png(f"icon-{s}.png", s)
        print(f"icon-{s}.png")
