import struct
import zlib
import time
import os
from io import BytesIO

def read_bmp(file_bytes):
    f = BytesIO(file_bytes)
    header_file = f.read(2)

    if header_file != b'BM':
        raise ValueError("Not a valid BMP file")
    
    file_size = struct.unpack('<I', f.read(4))[0]
    f.read(4)
    pixel_array_offset = struct.unpack('<I', f.read(4))[0]
    
    dib_header_size = struct.unpack('<I', f.read(4))[0]
    width = struct.unpack('<I', f.read(4))[0]
    height = struct.unpack('<I', f.read(4))[0]
    color_planes = struct.unpack('<H', f.read(2))[0]
    bits_per_pixel = struct.unpack('<H', f.read(2))[0]

    if bits_per_pixel not in (24, 32):
        raise ValueError(f"Unsupported BMP format: {bits_per_pixel} bits per pixel")
    

    bytes_per_pixel = bits_per_pixel // 8
    f.read(24) #Skip remaining header fields

    f.seek(pixel_array_offset)
    row_padded = (width * bytes_per_pixel + 3) & (~3)
    pixels = []

    for _ in range(height):
        row_data = f.read(row_padded)
        row = []
        for x in range(width):
            i = x * bytes_per_pixel

            if bytes_per_pixel == 4:
                b, g, r, a = row_data[i: i + 4]
                row.append((r, g, b, a))

            else:
                b, g, r, a = row_data[i: i + 3]
                row.append((r, g, b, 255))

        pixels.append(row)

    return width, height, pixels, bits_per_pixel


def write_bmp(width, height, pixels, bits_per_pixel = 24):

    bytes_per_pixel = bits_per_pixel // 8
    row_padded = (width * bytes_per_pixel + 3) & (~3)
    padding = row_padded - width * bytes_per_pixel

    pixel_data = bytearray()

    for y in range(height):
        for x in range(width):
            r, g, b, a  = pixels[y][x]
            if bytes_per_pixel == 4:
                pixel_data.extend([b, g, r, a])

            else:
                pixel_data.extend([b, g, r])

        pixel_data.extend(b'\x00' * padding)

    

    filesize = 54 + len(pixel_data)
    f = BytesIO()
    f.write(b'BM')
    f.write(struct. pack('<I', filesize))
    f.write(b'\x00\x00\x00\x00')    # Reserved
    f.write(struct.pack('<I', 54))  # Pixel data offset
    f.write(struct.pack('<I', 40))  # DIB header size
    f.write(struct.pack('<I', width))
    f.write(struct.pack('<I', height))
    f.write(struct.pack('<H', 1))   # color planes
    f.write(struct.pack('<H', bits_per_pixel))
    f.write(struct.pack('<I', 0))   # no compression
    f.write(struct.pack('<I', len(pixel_data)))
    f.write(struct.pack('<I', 2835))    # horizontal resolution
    f.write(struct.pack('<I', 2835))    # vertical resolution
    f.write(struct.pack('<I', 0))    # color in palette
    f.write(struct.pack('<I', 0))    # Important colors
    f.write(pixel_data)

    f.seek(0)

    return f.read()


def compress_bmp(file_bytes):

    width, height, pixels, bits_per_pixel = read_bmp(file_bytes)
    bytes_per_pixel = bits_per_pixel // 8

    raw_data = bytearray()
    for row in pixels:
        for r, g, b, a in row:
            if bytes_per_pixel == 4:
                raw_data.extend([r, g, b, a])
            else:
                raw_data.extend([r, g, b])

    compressed = zlib.compress(raw_data, level = 9)

    out = BytesIO()
    out.write(struct.pack('<III', width, height, bits_per_pixel))
    out.write(compressed)
    out.seek(0)
    return out.read()


def decompress_bmp(file_bytes):

    f = BytesIO(file_bytes)
    
    width, height, bits_per_pixel = struct.unpack('<III', f.read(12))
    compressed_data = f.read()
    bytes_per_pixel = bits_per_pixel // 8

    raw_data = zlib.decompress(compressed_data)

    pixels = []
    i = 0

    for _ in range(height):
        row = []
        for _ in range(width):
            if bytes_per_pixel == 4:
                r, g, b, a = raw_data[i : i + 4]
                i += 4
                row.append((r, g, b, a))
            else:
                r, g, b = raw_data[i: i + 3]
                i += 3
                row.append((r, g, b, 255))
        pixels.append(row)

    
    bmp_bytes = write_bmp(width, height, pixels, bits_per_pixel)
    return bmp_bytes

