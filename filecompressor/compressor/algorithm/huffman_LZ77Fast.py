from .utility import (
    build_frequency_table, read_binary_file, pad_bitstring,
    bitstring_to_bytes, save_frequency_table,
    calculate_compression_ratio, load_frequency_table,
    bytes_to_bitstring, remove_padding,
    write_binary_file, encode_data_to_bytes
)

import os, time
from .lz77_fast import LZ77Fast


class Node:
    def __init__(self, symbol, freq, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(freq_table):
    if not freq_table:
        return None

    nodes = []
    for symbol, frequency in freq_table.items():
        leaf = Node(symbol, frequency)
        nodes.append(leaf)

    while len(nodes) > 1:
        nodes = sorted(nodes, key=lambda x: x.freq)
        node1 = nodes.pop(0)
        node2 = nodes.pop(0)
        merged = Node(symbol=None, freq=node1.freq + node2.freq,
                      left=node1, right=node2)
        nodes.append(merged)

    return nodes[0]


def generate_huffman_code(node, current_node, code_map):
    if node is None:
        return

    if node.symbol is not None:
        code_map[node.symbol] = current_node
        return

    generate_huffman_code(node.left, current_node + "0", code_map)
    generate_huffman_code(node.right, current_node + "1", code_map)


def encode_data(data, code_map):
    encoded_bits = []
    if not data:
        return ""
    for byte in data:
        encoded_bits.append(code_map[byte])
    return "".join(encoded_bits)


def decode_data(encoded_bits, root):
    decoded_bytes = []
    current = root

    for bit in encoded_bits:
        if bit == "0":
            current = current.left
        elif bit == "1":
            current = current.right
        else:
            raise ValueError(f"Invalid bit: {bit}")

        if current is None:
            raise ValueError("Traversal reached None — corrupted bitstream or padding issue.")

        if current.symbol is not None:
            decoded_bytes.append(current.symbol)
            current = root

    return bytes(decoded_bytes)


def compress_huffmanLZ77Fast(input_path, output_path):
    BASE_DIR = os.path.dirname(__file__)
    input_path = os.path.join(BASE_DIR, input_path)
    output_path = os.path.join(BASE_DIR, output_path)

    data = read_binary_file(input_path)
    if not data:
        print("Empty file — nothing to compress.")
        return

    print("[INFO] Running LZ77 Fast compression...")
    start = time.time()

    lz77 = LZ77Fast()
    tokens = lz77.lz77_encode(data)
    byte_stream = LZ77Fast.tokens_to_bytes(tokens)

    freq_table = build_frequency_table(byte_stream)
    root = build_huffman_tree(freq_table)
    code_map = {}
    generate_huffman_code(root, "", code_map)

    payload = encode_data_to_bytes(byte_stream, code_map)
    save_frequency_table(output_path, freq_table, payload)

    original_size = len(data)
    compressed_size = os.path.getsize(output_path)
    ratio = calculate_compression_ratio(original_size, compressed_size)

    print(f"[STATS] Original: {original_size} bytes | Compressed: {compressed_size} bytes")
    print(f"[STATS] Compression Ratio: {ratio:.2f}%")
    print(f"[TIME] Compression finished in {time.time() - start:.2f}s")

    return ratio


def decompress_huffmanLZ77Fast(input_path, output_path):
    BASE_DIR = os.path.dirname(__file__)
    input_path = os.path.join(BASE_DIR, input_path)
    output_path = os.path.join(BASE_DIR, output_path)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input not found: {input_path}")

    freq_table, payload_offset, payload_bytes = load_frequency_table(input_path)
    root = build_huffman_tree(freq_table)

    bitstring = bytes_to_bitstring(payload_bytes)
    clean_bits = remove_padding(bitstring)

    decoded_stream = decode_data(clean_bits, root)
    tokens = LZ77Fast.bytes_to_tokens(decoded_stream)
    original_data = LZ77Fast().lz77_decode(tokens)

    write_binary_file(output_path, original_data)
    print(f"✅ Decompressed successfully: {output_path}")


# # ✅ ✅ ✅ RUN TEST (same as your original)
# if __name__ == "__main__":
#     start = time.time()
#     ratio = compress_huffmanLZ77Fast('lorem.txt', 'sample_copy.huf')
#     print("[TIME] Time Taken:", time.time() - start)
#     print(f"[STATS] Total ratio: {ratio:.2f}%")

    # Uncomment for testing decompress
    # decompress_huffmanLZ77Fast('sample_copy.huf', 'sample_decompressed.txt')
