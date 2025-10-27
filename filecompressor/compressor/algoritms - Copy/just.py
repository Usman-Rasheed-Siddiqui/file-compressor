
import zlib, lzma, os

def compress_file_zlib(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    compressed = zlib.compress(data, level=9)
    with open(output_path, 'wb') as f:
        f.write(compressed)
    print(f"✅ ZLIB compressed {len(data)} → {len(compressed)} bytes "
          f"({(1 - len(compressed)/len(data))*100:.2f}% smaller)")

def decompress_file_zlib(input_path, output_path):
    with open(input_path, 'rb') as f:
        compressed = f.read()
    data = zlib.decompress(compressed)
    with open(output_path, 'wb') as f:
        f.write(data)
    print("✅ ZLIB decompressed successfully")

def compress_file_lzma(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    compressed = lzma.compress(data, preset=9)
    with open(output_path, 'wb') as f:
        f.write(compressed)
    print(f"✅ LZMA compressed {len(data)} → {len(compressed)} bytes "
          f"({(1 - len(compressed)/len(data))*100:.2f}% smaller)")

def decompress_file_lzma(input_path, output_path):
    with open(input_path, 'rb') as f:
        compressed = f.read()
    data = lzma.decompress(compressed)
    with open(output_path, 'wb') as f:
        f.write(data)
    print("✅ LZMA decompressed successfully")

# Test run

BASE_DIR = os.path.dirname(__file__)  # folder of this script
input_path = os.path.join(BASE_DIR, 'book.pdf')
output_path = os.path.join(BASE_DIR, 'recovered.pdf')


#compress_file_lzma(input_path, output_path)
decompress_file_lzma(output_path, input_path)
